"""
backtest.py - a small, transparent daily backtester with realistic costs.

    from common.backtest import backtest, COST_PRESETS
    res = backtest(bars, signal, costs=COST_PRESETS["alpaca_retail"])
    res.metrics(benchmark=spy_returns)

`signal` is the position you WANT (1 = long, 0 = flat, -1 = short) decided with
information available at the CLOSE of bar t. To avoid look-ahead bias the trade
is executed on the NEXT bar:

    execution="next_open"  (default) fill at the open of bar t+1 - matches the
                           TradingView Strategy Tester default and the Lab 16 bot
    execution="next_close" fill at the close of bar t+1

Gross returns are computed in a vectorised way; a short loop then charges
costs on each trade (needed because a minimum commission or a per-share fee
depends on the account equity and share price at the time of the trade).

Costs modelled on every trade:
    commission  = max(min_commission, shares x commission_per_share + notional x commission_bps)
    spread      = notional x spread_bps / 2        (you cross half the quoted spread)
    slippage    = notional x slippage_bps          (market impact / delay)
    reg fees    = SELL notional x sec_fee_rate + min(shares sold x taf_per_share, taf_max)
                  (US SEC Section 31 fee and FINRA Trading Activity Fee style charges;
                   rates change - check the current published rates before using live)
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

from common import metrics as M


@dataclass
class CostModel:
    name: str = "zero cost"
    commission_per_share: float = 0.0
    commission_bps: float = 0.0
    min_commission: float = 0.0
    spread_bps: float = 0.0
    slippage_bps: float = 0.0
    sec_fee_rate: float = 0.0          # fraction of sell notional, e.g. 27.80 / 1e6
    taf_per_share: float = 0.0         # per share sold
    taf_max: float = 8.30              # cap per trade

    def trade_cost(self, notional: float, price: float, is_sell: bool) -> dict:
        """Cost breakdown in dollars for one trade of `notional` dollars at `price`."""
        if notional <= 0:
            return {"commission": 0.0, "spread": 0.0, "slippage": 0.0, "reg_fees": 0.0}
        shares = notional / price
        commission = shares * self.commission_per_share + notional * self.commission_bps / 1e4
        if self.commission_per_share or self.commission_bps or self.min_commission:
            commission = max(commission, self.min_commission)
        reg = 0.0
        if is_sell:
            reg = notional * self.sec_fee_rate + min(shares * self.taf_per_share, self.taf_max)
        return {"commission": commission,
                "spread": notional * self.spread_bps / 2 / 1e4,
                "slippage": notional * self.slippage_bps / 1e4,
                "reg_fees": reg}

    def scaled(self, factor: float) -> "CostModel":
        """Same cost model with every rate multiplied by `factor` (for sensitivity tests)."""
        return replace(self, name=f"{self.name} x{factor:g}",
                       commission_per_share=self.commission_per_share * factor,
                       commission_bps=self.commission_bps * factor,
                       min_commission=self.min_commission * factor,
                       spread_bps=self.spread_bps * factor, slippage_bps=self.slippage_bps * factor,
                       sec_fee_rate=self.sec_fee_rate * factor, taf_per_share=self.taf_per_share * factor)


SEC_FEE = 27.80 / 1e6        # illustrative Section 31 rate ($ per $ of sell notional)
FINRA_TAF = 0.000166         # illustrative TAF per share sold

COST_PRESETS = {
    "zero": CostModel(),
    # Alpaca: commission-free US equities; you still pay spread, slippage and reg fees on sells
    "alpaca_retail": CostModel("Alpaca commission-free", spread_bps=1.0, slippage_bps=1.0,
                               sec_fee_rate=SEC_FEE, taf_per_share=FINRA_TAF),
    # A per-share institutional broker (illustrative)
    "per_share_broker": CostModel("Per-share broker", commission_per_share=0.005, min_commission=1.0,
                                  spread_bps=2.0, slippage_bps=2.0,
                                  sec_fee_rate=SEC_FEE, taf_per_share=FINRA_TAF),
    # A high-cost retail/offshore route (illustrative)
    "high_cost": CostModel("High-cost route", commission_bps=10.0, spread_bps=5.0, slippage_bps=5.0,
                           sec_fee_rate=SEC_FEE, taf_per_share=FINRA_TAF),
}


@dataclass
class BacktestResult:
    equity: pd.Series
    equity_gross: pd.Series
    returns: pd.Series
    returns_gross: pd.Series
    position: pd.Series                 # position held during each bar (after that bar's fill)
    trades: pd.DataFrame
    costs: pd.DataFrame                 # per-bar dollar costs by type
    initial_capital: float
    cost_model: CostModel = field(default_factory=CostModel)

    def metrics(self, benchmark: pd.Series | None = None, gross: bool = False) -> dict:
        r = self.returns_gross if gross else self.returns
        col = "gross_return" if gross else "net_return"
        tr = self.trades[col] if len(self.trades) else pd.Series(dtype=float)
        return M.summary(r, self.position, tr, benchmark)

    def cost_summary(self) -> dict:
        totals = self.costs.sum()
        out = {k: float(totals.get(k, 0.0)) for k in ["commission", "spread", "slippage", "reg_fees"]}
        out["total"] = float(sum(out.values()))
        out["total_pct_of_capital"] = out["total"] / self.initial_capital
        out["gross_cagr"] = M.cagr(self.returns_gross)
        out["net_cagr"] = M.cagr(self.returns)
        out["cost_drag_cagr"] = out["gross_cagr"] - out["net_cagr"]
        out["n_trades"] = int((self.costs["traded_notional"] > 0).sum())
        return out


def backtest(bars: pd.DataFrame, signal: pd.Series, initial_capital: float = 100_000.0,
             costs: CostModel | None = None, execution: str = "next_open",
             allow_short: bool = False) -> BacktestResult:
    """Run a long/flat (or long/short) daily backtest with next-bar execution."""
    costs = costs or CostModel()
    bars = bars[["open", "close"]].astype(float)
    sig = signal.reindex(bars.index).astype(float).fillna(0.0)
    sig = sig.clip(-1, 1) if allow_short else sig.clip(0, 1)

    o, c = bars["open"].values, bars["close"].values
    prev_c = np.r_[np.nan, c[:-1]]
    if execution == "next_open":
        pos_new = sig.shift(1).fillna(0.0).values      # filled at today's open
        pos_old = sig.shift(2).fillna(0.0).values      # held overnight into today
        overnight = np.nan_to_num(o / prev_c - 1.0)
        intraday = c / o - 1.0
        gross = (1 + pos_old * overnight) * (1 + pos_new * intraday) - 1.0
        held, exec_px = pos_new, o
    elif execution == "next_close":
        pos_new = sig.shift(1).fillna(0.0).values      # filled at today's close
        pos_old = sig.shift(2).fillna(0.0).values      # held during today
        gross = pos_old * np.nan_to_num(c / prev_c - 1.0)
        held, exec_px = pos_old, c
    else:
        raise ValueError("execution must be 'next_open' or 'next_close'")

    # ---- cost loop: equity-dependent dollar costs on each trade
    eq_net, eq_gross = np.empty(len(c)), np.empty(len(c))
    cost_rows = []
    e, eg = initial_capital, initial_capital
    for i in range(len(c)):
        delta = pos_new[i] - pos_old[i]
        if execution == "next_open":
            e_at_trade = e * (1 + pos_old[i] * overnight[i])
        else:
            e_at_trade = e * (1 + gross[i])
        notional = abs(delta) * e_at_trade
        cb = costs.trade_cost(notional, exec_px[i], is_sell=delta < 0)
        total_cost = sum(cb.values())
        e = e * (1 + gross[i]) - total_cost
        eg = eg * (1 + gross[i])
        eq_net[i], eq_gross[i] = e, eg
        cost_rows.append({**cb, "traded_notional": notional})

    idx = bars.index
    equity = pd.Series(eq_net, idx, name="equity")
    equity_gross = pd.Series(eq_gross, idx, name="equity_gross")
    returns = equity.pct_change().fillna(equity.iloc[0] / initial_capital - 1.0)
    returns_gross = pd.Series(gross, idx).fillna(0.0)
    cost_df = pd.DataFrame(cost_rows, index=idx)
    cost_df["total"] = cost_df[["commission", "spread", "slippage", "reg_fees"]].sum(axis=1)
    position = pd.Series(held, idx, name="position")
    trades = _extract_trades(pd.Series(pos_new, idx), pd.Series(exec_px, idx), equity)
    return BacktestResult(equity, equity_gross, returns, returns_gross, position,
                          trades, cost_df, initial_capital, costs)


def _extract_trades(pos_after_fill: pd.Series, exec_px: pd.Series, equity: pd.Series) -> pd.DataFrame:
    """Round-trip trades from the position series (entry -> exit or flip)."""
    rows, side, entry_i = [], 0.0, None
    sign = np.sign(pos_after_fill.values)
    eq = equity.values
    for i in range(len(sign)):
        if sign[i] != side:
            if side != 0 and entry_i is not None:              # close the open trade
                e_before = eq[entry_i - 1] if entry_i > 0 else eq[0]
                rows.append({
                    "entry_date": pos_after_fill.index[entry_i], "exit_date": pos_after_fill.index[i],
                    "side": "long" if side > 0 else "short",
                    "entry_price": exec_px.iloc[entry_i], "exit_price": exec_px.iloc[i],
                    "bars_held": i - entry_i,
                    "gross_return": side * (exec_px.iloc[i] / exec_px.iloc[entry_i] - 1.0),
                    # equity-based, so it includes costs (approximate on a flip)
                    "net_return": eq[i] / e_before - 1.0})
            side, entry_i = sign[i], (i if sign[i] != 0 else None)
    if side != 0 and entry_i is not None:                       # still open at the end: mark to market
        last = len(sign) - 1
        e_before = eq[entry_i - 1] if entry_i > 0 else eq[0]
        rows.append({"entry_date": pos_after_fill.index[entry_i], "exit_date": pos_after_fill.index[last],
                     "side": ("long" if side > 0 else "short") + " (open)",
                     "entry_price": exec_px.iloc[entry_i], "exit_price": exec_px.iloc[last],
                     "bars_held": last - entry_i,
                     "gross_return": side * (exec_px.iloc[last] / exec_px.iloc[entry_i] - 1.0),
                     "net_return": eq[last] / e_before - 1.0})
    return pd.DataFrame(rows)


def buy_and_hold(bars: pd.DataFrame, costs: CostModel | None = None,
                 initial_capital: float = 100_000.0) -> BacktestResult:
    """Benchmark: buy at the first available next-bar open and hold to the end."""
    return backtest(bars, pd.Series(1.0, index=bars.index), initial_capital, costs)


def cross_signal(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """Long (1) while fast > slow, flat (0) otherwise; NaN warm-up treated as flat."""
    return (fast > slow).astype(float).where(fast.notna() & slow.notna(), 0.0)
