"""
pipeline/search.py - Stage 10: strategy search with an in-sample / out-of-sample split.

Grid-searches parameters of three signal families from the library, ranks every
parameter set on the IN-SAMPLE period only, then measures how the ranking holds
up on the untouched OUT-OF-SAMPLE period (decay report):

  sma_cross            fast x slow             24 sets
  rsi_reversion        n x entry x exit        36 sets
  bollinger_breakout   window x k              16 sets

It also prefers a ROBUST REGION (a parameter whose neighbours are also good)
over the single best cell, because an isolated peak is usually luck.

    python -m pipeline search --symbol SPY
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import itertools
import sys

import numpy as np
import pandas as pd

from common import metrics as M
from common.backtest import backtest
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.ingest import load_bars
from pipeline.signals import target_position

IS_END, OOS_START = "2021-12-31", "2022-01-01"      # 4 years in-sample, 4 years out-of-sample (incl. 2022 bear market)
GRIDS = {
    "sma_cross": {"fast": [5, 10, 20, 30, 50], "slow": [50, 100, 150, 200, 250]},
    "rsi_reversion": {"n": [2, 3, 5, 14], "entry": [10, 20, 30], "exit": [50, 60, 70]},
    "bollinger_breakout": {"window": [10, 20, 30, 50], "k": [1.0, 1.5, 2.0, 2.5]},
}


def grid_points(name: str):
    keys = list(GRIDS[name])
    for values in itertools.product(*GRIDS[name].values()):
        p = dict(zip(keys, values))
        if name == "sma_cross" and p["fast"] >= p["slow"]:
            continue                                     # fast must be shorter than slow
        yield p


def search(bars, costs, families=None) -> pd.DataFrame:
    rows = []
    for name in families or GRIDS:
        for p in grid_points(name):
            res = backtest(bars, target_position(name, bars, **p), costs=costs)   # causal signal: one run, two windows
            r_is, r_oos = res.returns.loc[:IS_END], res.returns.loc[OOS_START:]
            rows.append({"family": name, "params": p, **{f"p_{k}": v for k, v in p.items()},
                         "IS_sharpe": M.sharpe_ratio(r_is), "IS_cagr": M.cagr(r_is),
                         "OOS_sharpe": M.sharpe_ratio(r_oos), "OOS_cagr": M.cagr(r_oos), "trades": len(res.trades)})
    df = pd.DataFrame(rows)
    df["IS_rank"] = df["IS_sharpe"].rank(ascending=False, method="min", na_option="bottom").astype(int)
    df["OOS_rank"] = df["OOS_sharpe"].rank(ascending=False, method="min", na_option="bottom").astype(int)
    df["decay"] = df["OOS_sharpe"] - df["IS_sharpe"]
    return df


def robust_choice(ma: pd.DataFrame) -> pd.Series:
    """MA cell with the best AVERAGE in-sample Sharpe over itself and its grid neighbours."""
    grid = ma.pivot(index="p_fast", columns="p_slow", values="IS_sharpe")
    vals = grid.values
    score = np.full(vals.shape, np.nan)
    for i, j in itertools.product(range(vals.shape[0]), range(vals.shape[1])):
        if not np.isnan(vals[i, j]):
            score[i, j] = np.nanmean(vals[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2])
    i, j = np.unravel_index(np.nanargmax(score), score.shape)
    pick = ma[(ma.p_fast == grid.index[i]) & (ma.p_slow == grid.columns[j])].iloc[0].copy()
    pick["neighbour_IS_sharpe"] = score[i, j]
    return pick


def run(symbol: str = "SPY", quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    bars = load_bars(symbol, cfg["data"]["start"], cfg["data"]["end"])
    costs = cost_model(cfg)
    df = search(bars, costs)
    bh = bars["close"].pct_change().fillna(0)
    bh_is, bh_oos = M.sharpe_ratio(bh.loc[:IS_END]), M.sharpe_ratio(bh.loc[OOS_START:])
    out(f"\nTested {len(df)} parameter sets on {symbol} | in-sample to {IS_END}, out-of-sample from {OOS_START} | "
        f"costs: {costs.name}")
    out(f"Buy & hold Sharpe: in-sample {bh_is:.2f}, out-of-sample {bh_oos:.2f}")

    out("\nDecay report - best set per family, chosen on IN-SAMPLE Sharpe only:")
    best = df.loc[df.groupby("family")["IS_sharpe"].idxmax()]
    for _, b in best.iterrows():
        out(f"  {b.family:<19} {str(b.params):<36} IS {b.IS_sharpe:5.2f} -> OOS {b.OOS_sharpe:5.2f}  "
            f"(decay {b.decay:+.2f}, OOS rank {b.OOS_rank} of {len(df)}, trades {b.trades})")
    top = df.nsmallest(5, "IS_rank")
    out("\nTop 5 by in-sample Sharpe:")
    out(top[["family", "params", "IS_sharpe", "OOS_sharpe", "decay", "OOS_rank"]].round(3).to_string(index=False))
    rank_corr = df["IS_sharpe"].corr(df["OOS_sharpe"], method="spearman")
    beat = (df["OOS_sharpe"] > bh_oos).mean()
    out(f"\n  Rank correlation IS vs OOS Sharpe across {len(df)} sets: {rank_corr:.2f}  (near 0 = IS ranking has little value)")
    out(f"  Average decay of the top 5: {top.decay.mean():+.2f} Sharpe points")
    out(f"  Share of ALL sets that beat buy & hold out-of-sample: {beat:.0%}")

    ma = df[df.family == "sma_cross"]
    rob = robust_choice(ma)
    peak = ma.loc[ma.IS_sharpe.idxmax()]
    out(f"\n  Single best MA cell {peak.params}: IS {peak.IS_sharpe:.2f} -> OOS {peak.OOS_sharpe:.2f}")
    out(f"  Robust MA region   {rob.params}: neighbour-average IS {rob.neighbour_IS_sharpe:.2f}, own IS "
        f"{rob.IS_sharpe:.2f} -> OOS {rob.OOS_sharpe:.2f}")
    out(f"  -> To promote a set, edit pipeline/config.yaml strategy: {{name: sma_cross, params: {rob.params}}}"
        f" and re-run evaluate + diagnose first.")

    csv = output_path("Lab10_grid_results.csv")
    df.drop(columns="params").round(4).to_csv(csv, index=False)
    rep = output_path("Lab10_decay_report.csv")
    best.drop(columns="params").round(4).to_csv(rep, index=False)
    out(f"  Full grid -> _outputs/{csv.name}; decay report -> _outputs/{rep.name}")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    for ax, col, title in [(axes[0], "IS_sharpe", "In-sample Sharpe 2018-2021"),
                           (axes[1], "OOS_sharpe", "Out-of-sample Sharpe 2022-2025")]:
        grid = ma.pivot(index="p_fast", columns="p_slow", values=col)
        im = ax.imshow(grid.values, cmap="RdYlGn", vmin=-0.5, vmax=1.5, aspect="auto")
        ax.set_xticks(range(len(grid.columns)), [int(x) for x in grid.columns])
        ax.set_yticks(range(len(grid.index)), [int(x) for x in grid.index])
        ax.set_xlabel("Slow SMA")
        ax.set_ylabel("Fast SMA")
        ax.set_title(f"{symbol} sma_cross: {title}")
        ax.grid(False)
        for i, j in itertools.product(range(grid.shape[0]), range(grid.shape[1])):
            if pd.notna(grid.values[i, j]):
                ax.text(j, i, f"{grid.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=axes, shrink=0.8, label="Sharpe")
    save(fig, "Lab10_grid_heatmap.png")
    return {"n_sets": len(df), "rank_corr": float(rank_corr), "top5_decay": float(top.decay.mean()),
            "beat_bh_oos": float(beat), "best": best[["family", "IS_sharpe", "OOS_sharpe"]].round(2).to_dict("records"),
            "robust": rob.params}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline search", description="Stage 10 - strategy search")
    ap.add_argument("--symbol", default="SPY")
    a = ap.parse_args(argv)
    stage_banner(10, "strategy search: grid, in/out-of-sample, decay")
    run(a.symbol.upper())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
