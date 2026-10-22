"""
pipeline/evaluate.py - Stage 09: metrics and a benchmark table for every strategy.

Runs every signal in the library through the backtester (next-bar-open fills,
config cost preset), measures each over the SAME window (from the first day every
signal is warm) and compares it with buy and hold:

  return    total return, CAGR
  risk      volatility, max drawdown
  per-risk  Sharpe, Sortino, Calmar
  trading   trades, win rate, profit factor, exposure, turnover
  market    alpha, beta versus the benchmark

    python -m pipeline evaluate --symbol SPY
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

from common import metrics as M
from common.backtest import backtest, buy_and_hold
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.indicators import ta_sma
from pipeline.ingest import load_bars
from pipeline.signals import SIGNALS, target_position

COLUMNS = ["CAGR", "Ann. volatility", "Sharpe", "Sortino", "Max drawdown", "Calmar", "Trades", "Win rate",
           "Profit factor", "Exposure", "Turnover", "Alpha", "Beta"]


def evaluate_strategy(bars, name, costs, start, bench_ret, **params) -> tuple[dict, object]:
    res = backtest(bars, target_position(name, bars, **params), costs=costs)
    r = res.returns.loc[start:]
    m = M.summary(r, res.position.loc[start:], res.trades["net_return"] if len(res.trades) else None, benchmark=bench_ret)
    return m, res


def run(symbol: str = "SPY", quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    bars = load_bars(symbol, cfg["data"]["start"], cfg["data"]["end"])
    costs = cost_model(cfg)
    start = ta_sma(bars["close"], 200).first_valid_index()        # slowest indicator warm -> common window
    bench = buy_and_hold(bars, costs)
    b_ret = bench.returns.loc[start:]
    rows = {f"{symbol} buy & hold": M.summary(b_ret, bench.position.loc[start:], None, benchmark=b_ret)}
    curves = {f"{symbol} buy & hold": bench.equity.loc[start:]}
    for name in SIGNALS:
        m, res = evaluate_strategy(bars, name, costs, start, b_ret)
        rows[name] = m
        curves[name] = res.equity.loc[start:]
    df = pd.DataFrame(rows).T[COLUMNS]
    df = df.sort_values("Sharpe", ascending=False)
    fmt = M.format_table(df.T.to_dict()).T[COLUMNS]
    out(f"\n{symbol} {start.date()} to {bars.index[-1].date()} | next-bar-open fills | costs: {costs.name} | ranked by Sharpe")
    out(fmt.to_string())
    bh = rows[f"{symbol} buy & hold"]
    better = df[(df["Sharpe"] > bh["Sharpe"]) & (df.index != f"{symbol} buy & hold")]
    lower_dd = df[(df["Max drawdown"] > bh["Max drawdown"] + 1e-4) & (df.index != f"{symbol} buy & hold")]
    out(f"\n  Beat buy & hold on Sharpe: {', '.join(better.index) or 'none'}")
    out(f"  Smaller max drawdown than buy & hold: {len(lower_dd)} of {len(SIGNALS)} strategies")

    # One metric by hand, so there is no black box (the 200-day trend filter)
    _, tf = evaluate_strategy(bars, "trend_filter", costs, start, b_ret)
    r = tf.returns.loc[start:]
    out(f"\n  Sharpe by hand (trend_filter): mean {r.mean():.5f} / stdev {r.std():.5f} x sqrt(252) = "
        f"{r.mean() / r.std() * np.sqrt(252):.2f}")
    out(f"  Worst trend_filter day {r.idxmin().date()} ({r.min():+.2%}); worst {symbol} day {b_ret.idxmin().date()} "
        f"({b_ret.min():+.2%}); {symbol} drawdown trough {M.drawdown_series(b_ret).idxmin().date()}")
    csv = output_path("Lab09_metrics.csv")
    fmt.to_csv(csv)
    out(f"  Metrics table -> _outputs/{csv.name}")

    top = list(df.index[:4]) + ([f"{symbol} buy & hold"] if f"{symbol} buy & hold" not in df.index[:4] else [])
    from common.plotting import plot_equity_and_drawdown
    plot_equity_and_drawdown({k: curves[k] for k in top}, f"{symbol}: top strategies by Sharpe vs buy & hold (net)",
                             "Lab09_metrics.png")
    return {"start": str(start.date()), "table": df.round(4).to_dict("index"), "best": df.index[0]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline evaluate", description="Stage 09 - evaluation")
    ap.add_argument("--symbol", default="SPY")
    a = ap.parse_args(argv)
    stage_banner(9, "evaluation: metrics and benchmark table")
    run(a.symbol.upper())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
