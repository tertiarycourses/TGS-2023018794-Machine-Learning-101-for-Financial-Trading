"""
pipeline/ml.py - Stage 11: a walk-forward machine-learning signal.

  features  : lagged returns, momentum, RSI(14), RSI(2), MACD histogram, Bollinger %B,
              21-day volatility, distance to SMA 50/200, volume z-score (all known at close t)
  label     : 1 if close t+1 > close t (used for training only - never as a feature)
  models    : logistic regression, random forest, XGBoost
  validation: walk-forward TimeSeriesSplit(5, gap=1) - always train on the past, test on the next block
  signal    : probability P(up) -> target position 1 if P(up) > threshold, else 0
              -> traded next bar through the same backtester and costs as every other signal

    python -m pipeline ml --threshold 0.55
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import metrics as M
from common.backtest import backtest
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.indicators import ta_bb, ta_macd, ta_rsi, ta_sma
from pipeline.ingest import load_bars

warnings.filterwarnings("ignore", category=UserWarning)


def build_features(bars: pd.DataFrame) -> pd.DataFrame:
    """Every feature uses data up to today's close only (no look-ahead). Last row has no label yet."""
    c = bars["close"]
    r = c.pct_change()
    f = pd.DataFrame(index=bars.index)
    for lag in (1, 2, 3, 5):
        f[f"ret_lag{lag}"] = r.shift(lag - 1)                  # ret_lag1 = today's return
    f["mom_5"], f["mom_21"] = c.pct_change(5), c.pct_change(21)
    f["rsi_14"], f["rsi_2"] = ta_rsi(c, 14), ta_rsi(c, 2)
    f["macd_hist"] = ta_macd(c)[2] / c
    mid, up, lo = ta_bb(c)
    f["bb_pct_b"] = (c - lo) / (up - lo)
    f["vol_21"] = r.rolling(21).std() * np.sqrt(252)
    f["dist_sma50"], f["dist_sma200"] = c / ta_sma(c, 50) - 1, c / ta_sma(c, 200) - 1
    f["volume_z"] = (bars["volume"] - bars["volume"].rolling(21).mean()) / bars["volume"].rolling(21).std()
    f["target"] = (c.shift(-1) > c).astype(int)                # the LABEL (tomorrow up?)
    return f.iloc[:-1].dropna()


def _xgb():
    from xgboost import XGBClassifier
    return XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                         random_state=42, eval_metric="logloss")


MODELS = {
    "Logistic regression": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=1000)),
    "Random forest": lambda: RandomForestClassifier(n_estimators=300, max_depth=4, min_samples_leaf=20,
                                                    random_state=42, n_jobs=-1),
    "XGBoost": _xgb,
}


def walk_forward_proba(X: pd.DataFrame, y: pd.Series, make, splits: int = 5):
    """Out-of-sample P(up) for every test block; returns (probabilities, last fitted model)."""
    p = pd.Series(np.nan, index=X.index)
    model = None
    for tr, te in TimeSeriesSplit(n_splits=splits, gap=1).split(X):
        model = make().fit(X.iloc[tr], y.iloc[tr])
        p.iloc[te] = model.predict_proba(X.iloc[te])[:, 1]
    return p.dropna(), model


def position_from_probability(prob: pd.Series, threshold: float, index=None) -> pd.Series:
    """Target position decided at close t: long when P(up) > threshold."""
    pos = (prob > threshold).astype(float)
    return pos.reindex(index).fillna(0.0) if index is not None else pos


def run(symbol: str = "SPY", threshold: float = 0.55, models: list[str] | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    bars = load_bars(symbol, cfg["data"]["start"], cfg["data"]["end"])
    data = build_features(bars)
    X, y = data.drop(columns="target"), data["target"]
    out(f"\nSamples {len(X)} | features {X.shape[1]} | base rate (share of up days) {y.mean():.1%}")
    out("Walk-forward folds (train on the past, test on the next block, gap 1 day):")
    for k, (tr, te) in enumerate(TimeSeriesSplit(n_splits=5, gap=1).split(X), 1):
        out(f"  fold {k}: train {X.index[tr[0]].date()}..{X.index[tr[-1]].date()}  "
            f"test {X.index[te[0]].date()}..{X.index[te[-1]].date()}")
    probs, scores, importance = {}, [], None
    for name in models or MODELS:
        p, model = walk_forward_proba(X, y, MODELS[name])
        yt, pred = y.loc[p.index], (p > 0.5).astype(int)
        scores.append({"model": name, "accuracy": accuracy_score(yt, pred),
                       "precision": precision_score(yt, pred, zero_division=0), "AUC": roc_auc_score(yt, p),
                       "share predicted up": pred.mean()})
        probs[name] = p
        if name == "XGBoost" and hasattr(model, "feature_importances_"):
            importance = pd.Series(model.feature_importances_, X.columns)
    oos_idx = next(iter(probs.values())).index
    out("\nOut-of-sample classification metrics:")
    out(pd.DataFrame(scores).set_index("model").round(3).to_string())
    out(f"  (always predicting 'up' scores accuracy {y.loc[oos_idx].mean():.3f}, AUC 0.500)")

    test_bars = bars.loc[oos_idx[0]:]
    costs = cost_model(cfg)
    bh = backtest(test_bars, pd.Series(1.0, test_bars.index), costs=costs)
    rows, curves = {f"Buy & hold {symbol}": bh.metrics()}, {f"Buy & hold {symbol}": bh.equity}
    for name, p in probs.items():
        res = backtest(test_bars, position_from_probability(p, threshold, test_bars.index), costs=costs)
        rows[name] = res.metrics(benchmark=bh.returns)
        curves[name] = res.equity
    table = M.format_table(rows).loc[["CAGR", "Sharpe", "Max drawdown", "Exposure", "Trades", "Turnover"]]
    out(f"\nML signal backtest {test_bars.index[0].date()}..{test_bars.index[-1].date()} "
        f"(long if P(up) > {threshold}, next-open fills, {costs.name}):")
    out(table.to_string())
    best_auc = max(s["AUC"] for s in scores)
    verdict = ("NO EDGE - AUC within noise of 0.5; keep the ML signal out of the live strategy"
               if best_auc < 0.53 else "possible edge - run diagnose and A/B test before promoting")
    out(f"  VERDICT: {verdict}")
    path = output_path("Lab11_ml_probabilities.csv")
    pd.DataFrame(probs).round(4).to_csv(path)
    out(f"  Out-of-sample probabilities -> _outputs/{path.name}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1.6, 1]})
    for name, eq in curves.items():
        ax1.plot(eq.index, eq / eq.iloc[0], label=name, lw=1.3)
    ax1.set_title("Walk-forward ML signals vs buy & hold (net of costs)")
    ax1.legend()
    if importance is not None:
        importance.sort_values().plot.barh(ax=ax2, color="#1f4e79")
        ax2.set_title("XGBoost feature importance (last fold)")
    save(fig, "Lab11_ml_strategy.png")
    return {"samples": len(X), "auc": {s["model"]: round(s["AUC"], 3) for s in scores}, "verdict": verdict}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline ml", description="Stage 11 - walk-forward ML signal")
    ap.add_argument("--symbol", default="SPY")
    ap.add_argument("--threshold", type=float, default=0.55)
    ap.add_argument("--models", nargs="+", default=None, choices=list(MODELS), metavar="MODEL",
                    help=f"subset of: {', '.join(MODELS)}")
    a = ap.parse_args(argv)
    stage_banner(11, "ML signal: walk-forward classifier -> probability -> position")
    run(a.symbol.upper(), a.threshold, a.models)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
