"""
pipeline/regime.py - Stage 12: a regime filter (gate) for the signals.

  1. PCA on the universe's daily returns - how many independent drivers move the book?
  2. K-means on backward-looking SPY features (volatility, trend, stock-bond correlation)
     -> market regimes named by their volatility
  3. WALK-FORWARD labels: refit K-means each January on data up to the previous
     December only, so today's regime never uses future data
  4. GATE: a signal's target is forced flat while the regime is 'High vol (stress)'
     -> compare gated and ungated strategies after costs

    python -m pipeline regime --clusters 3
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from common import metrics as M
from common.backtest import backtest
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.indicators import ta_sma
from pipeline.ingest import load_bars, load_closes
from pipeline.signals import target_position

STRESS = "High vol (stress)"


def regime_features(closes: pd.DataFrame) -> pd.DataFrame:
    rets = closes.pct_change()
    spy = closes["SPY"]
    return pd.DataFrame({
        "vol_21": rets["SPY"].rolling(21).std() * np.sqrt(252),
        "ret_21": spy.pct_change(21),
        "ret_63": spy.pct_change(63),
        "dist_sma200": spy / ta_sma(spy, 200) - 1,
        "corr_spy_tlt": rets["SPY"].rolling(63).corr(rets["TLT"]),
    }).dropna()


def fit_regimes(train: pd.DataFrame, k: int):
    scaler = StandardScaler().fit(train)
    km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(scaler.transform(train))
    order = train.groupby(km.labels_)["vol_21"].mean().sort_values().index
    names = dict(zip(order, ["Low vol", "Moderate vol", STRESS] if k == 3
                     else [f"Regime {i + 1} (vol rank)" for i in range(k - 1)] + [STRESS]))
    return scaler, km, names


def walk_forward_regimes(feat: pd.DataFrame, k: int, first_year: int = 2020) -> pd.Series:
    """Label each year with a model fitted only on data before that year."""
    out = []
    for year in range(first_year, feat.index[-1].year + 1):
        train, test = feat.loc[:f"{year - 1}-12-31"], feat.loc[f"{year}-01-01":f"{year}-12-31"]
        if len(test) == 0 or len(train) < 200:
            continue
        scaler, km, names = fit_regimes(train, k)
        out.append(pd.Series(km.predict(scaler.transform(test)), index=test.index).map(names))
    return pd.concat(out).rename("regime")


def regime_gate(target: pd.Series, regimes: pd.Series, blocked=(STRESS,)) -> pd.Series:
    """Force the target flat on days whose (known-at-close) regime is blocked."""
    allowed = ~regimes.reindex(target.index).isin(blocked)
    return target.where(allowed, 0.0)


def run(k: int = 3, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k_: None)
    cfg = load_config()
    universe = cfg["universe"]["trade"]
    closes = load_closes(universe, cfg["data"]["start"], cfg["data"]["end"])
    rets = closes.pct_change().dropna()

    pca = PCA().fit(StandardScaler().fit_transform(rets))
    ev = pca.explained_variance_ratio_
    out(f"\n[1] PCA on {rets.shape[1]} assets x {rets.shape[0]} days")
    for i in range(4):
        out(f"  PC{i + 1}: {ev[i]:6.1%} of variance  (cumulative {ev[:i + 1].sum():6.1%})")
    load = pd.DataFrame(pca.components_[:3].T, index=rets.columns, columns=["PC1", "PC2", "PC3"])
    out("  Loadings:\n  " + load.round(2).to_string().replace("\n", "\n  "))
    out("  -> PC1 = broad equity factor; TLT and GLD load differently (diversifiers)")

    feat = regime_features(closes)
    scaler, km, names = fit_regimes(feat, k)
    full = pd.Series(km.labels_, index=feat.index).map(names)
    order = list(names.values())                                    # volatility rank, low -> high
    prof = feat.groupby(full).mean().reindex(order)
    prof["days"] = full.value_counts().reindex(order)
    prof["share"] = prof["days"] / prof["days"].sum()
    out(f"\n[2] K-means ({k} clusters, full-sample fit = hindsight, for description only):")
    out("  " + prof.round(3).to_string().replace("\n", "\n  "))
    nxt = rets["SPY"].shift(-1).reindex(feat.index)
    trend = (closes["SPY"] > ta_sma(closes["SPY"], 200)).astype(float).reindex(feat.index)
    rows = []
    for name in prof.index:
        m = full == name
        rows.append({"regime": name, "days": int(m.sum()), "B&H Sharpe": M.sharpe_ratio(nxt[m].dropna()),
                     "Trend-filter Sharpe": M.sharpe_ratio((nxt * trend)[m].dropna())})
    out("  Next-day SPY performance by regime:\n  "
        + pd.DataFrame(rows).set_index("regime").round(2).to_string().replace("\n", "\n  "))

    wf = walk_forward_regimes(feat, k)
    out(f"\n[3] Walk-forward regimes {wf.index[0].date()} to {wf.index[-1].date()} (refit each January on past data):")
    out("  " + wf.value_counts().reindex(order).fillna(0).astype(int).to_string().replace("\n", "\n  "))
    out(f"  Latest regime ({wf.index[-1].date()}): {wf.iloc[-1]} -> gate is "
        f"{'CLOSED (flat)' if wf.iloc[-1] == STRESS else 'OPEN (signals pass through)'}")

    bars = load_bars("SPY", cfg["data"]["start"], cfg["data"]["end"])
    costs = cost_model(cfg)
    test = bars.loc[wf.index[0]:]
    out(f"\n[4] Regime gate, SPY {test.index[0].date()} to {test.index[-1].date()} (net of {costs.name} costs):")
    results, curves = [], {}
    bh = backtest(test, pd.Series(1.0, test.index), costs=costs)
    curves["SPY buy & hold"] = bh.equity
    for name in [cfg["strategy"]["name"], "trend_filter", "dip_buy"]:
        params = cfg["strategy"]["params"] if name == cfg["strategy"]["name"] else {}
        tgt = target_position(name, bars, **params).loc[test.index]
        for label, t in [("ungated", tgt), ("gated", regime_gate(tgt, wf))]:
            res = backtest(test, t, costs=costs)
            m = res.metrics()
            results.append({"signal": name, "version": label, "CAGR": m["CAGR"], "Sharpe": m["Sharpe"],
                            "Max drawdown": m["Max drawdown"], "Exposure": m["Exposure"], "Trades": m["Trades"]})
            if name == cfg["strategy"]["name"]:
                curves[f"{name} {label}"] = res.equity
    r = pd.DataFrame(results)
    show = r.assign(**{c: r[c].map("{:.2%}".format) for c in ["CAGR", "Max drawdown", "Exposure"]},
                    Sharpe=r.Sharpe.round(2))
    out("  " + show.to_string(index=False).replace("\n", "\n  "))
    g = r.pivot(index="signal", columns="version", values="Sharpe")
    helped = list(g.index[g["gated"] > g["ungated"]])
    out(f"  -> the gate improved Sharpe for: {', '.join(helped) or 'none'}. A gate is a model too: "
        f"diagnose and A/B test it before it goes live.")
    path = output_path("Lab12_regime_labels.csv")
    wf.to_csv(path)
    out(f"  Walk-forward labels -> _outputs/{path.name}")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3), gridspec_kw={"width_ratios": [0.8, 1.6, 1.4]})
    axes[0].bar(range(1, len(ev) + 1), ev * 100, color="#1f4e79")
    axes[0].plot(range(1, len(ev) + 1), np.cumsum(ev) * 100, "o-", color="#c0504d", label="Cumulative")
    axes[0].set_title("PCA explained variance (%)")
    axes[0].legend()
    colours = {"Low vol": "#4f9a3b", "Moderate vol": "#e2a400", STRESS: "#c0504d"}
    s = closes["SPY"].reindex(wf.index)
    axes[1].plot(s.index, s, color="#333333", lw=0.8)
    for name in order:
        m = wf == name
        axes[1].scatter(s.index[m], s[m], s=6, color=colours.get(name), label=name)
    axes[1].set_title("SPY coloured by WALK-FORWARD regime")
    axes[1].legend(markerscale=3)
    for name, eq in curves.items():
        axes[2].plot(eq.index, eq / eq.iloc[0], label=name, lw=1.2)
    axes[2].set_title("Regime gate on the configured strategy")
    axes[2].legend(fontsize=8)
    save(fig, "Lab12_regimes.png")
    return {"pc1": float(ev[0]), "latest_regime": wf.iloc[-1], "gate": r.round(4).to_dict("records")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline regime", description="Stage 12 - regime gate")
    ap.add_argument("--clusters", type=int, default=3)
    a = ap.parse_args(argv)
    stage_banner(12, "regime filter: PCA + K-means gate on signals")
    run(a.clusters)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
