"""
Lab 18 - Diagnose Unintended Outcomes: Overfitting, Look-Ahead Bias and Cost Drag (A9, K8)

A junior quant at Lion City Capital sends this "smoothed momentum" backtest to
the investment committee with a note: "Sharpe ratio above 3 - let's go live!"

YOUR TASK: the result is too good to be true. Read the code, find at least
THREE problems (look at the lines marked CHECK), explain why each one inflates
the result, then run fixed_backtest_solution.py to compare.

Run:
    python3 Lab18-diagnose-bias/buggy_backtest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np                       # noqa: E402

from common.config import banner         # noqa: E402
from common.data import get_bars         # noqa: E402


def buggy_strategy_returns(bars):
    close = bars["close"]
    # CHECK 1: a 5-day moving average to "smooth out noise"
    smooth = close.rolling(5, center=True).mean()
    # Long when the smoothed price is rising
    signal = (smooth > smooth.shift(1)).astype(float)
    daily_ret = close.pct_change()
    # CHECK 2: strategy return = today's signal x today's return
    strat_ret = signal * daily_ret
    # CHECK 3: no commission, spread, slippage or fees anywhere
    return strat_ret.dropna(), signal


if __name__ == "__main__":
    banner("Lab 18 - The 'too good to be true' backtest")
    bars = get_bars("SPY", "2018-01-01", "2025-12-31")
    r, signal = buggy_strategy_returns(bars)
    sharpe = r.mean() / r.std() * np.sqrt(252)
    cagr = (1 + r).prod() ** (252 / len(r)) - 1
    trades = int((signal.diff().abs() > 0).sum())
    print(f"\nSPY 'smoothed momentum' 2018-2025 (as submitted by the junior quant)")
    print(f"  CAGR            : {cagr:8.2%}")
    print(f"  Sharpe ratio    : {sharpe:8.2f}")
    print(f"  Win rate (days) : {(r[r != 0] > 0).mean():8.1%}")
    print(f"  Position changes: {trades}  (~{trades / 8:.0f} per year)")
    print("\nIs this credible? Real SPY timing strategies rarely exceed a Sharpe of about 1.")
    print("Write down the problems you find, then run: python3 Lab18-diagnose-bias/fixed_backtest_solution.py")
