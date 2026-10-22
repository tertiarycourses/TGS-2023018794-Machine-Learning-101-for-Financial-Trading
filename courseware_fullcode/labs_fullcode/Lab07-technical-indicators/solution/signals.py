"""
pipeline/signals.py - Stage 07: the signal library.

Every signal function takes OHLCV bars and returns a TARGET POSITION series
(1 = long, 0 = flat) decided with information available at the CLOSE of bar t.
The position is only HELD from bar t+1 (next-bar alignment) - the backtester,
the order manager and the runner all apply that rule, and next_bar_position()
shows it explicitly.

Families
  trend          ema_cross, sma_cross, trend_filter
  mean reversion rsi_reversion, dip_buy
  momentum       momentum
  breakout       donchian_breakout, bollinger_breakout

    from pipeline.signals import target_position
    tgt = target_position("ema_cross", bars, fast=10, slow=30)

    python -m pipeline signals --symbol SPY
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

from common.config import output_path
from common.plotting import plt, save
from pipeline.config import load_config, stage_banner
from pipeline.indicators import ta_bb, ta_ema, ta_rsi, ta_sma
from pipeline.ingest import load_bars


def _flat_until_ready(cond: pd.Series, *inputs: pd.Series) -> pd.Series:
    """1.0 where cond is true, 0.0 otherwise and during indicator warm-up (NaN inputs)."""
    ready = pd.concat(inputs, axis=1).notna().all(axis=1)
    return cond.astype(float).where(ready, 0.0)


def enter_exit(entry: pd.Series, exit_: pd.Series) -> pd.Series:
    """Stateful long/flat: 1 from an entry bar until the next exit bar (entry wins a tie)."""
    state = pd.Series(np.nan, index=entry.index)
    state[exit_.fillna(False).astype(bool)] = 0.0
    state[entry.fillna(False).astype(bool)] = 1.0
    return state.ffill().fillna(0.0)


# ------------------------------------------------------------------ trend
def ema_cross(bars, fast: int = 10, slow: int = 30) -> pd.Series:
    """Long while EMA(fast) > EMA(slow)."""
    f, s = ta_ema(bars["close"], fast), ta_ema(bars["close"], slow)
    return _flat_until_ready(f > s, f, s)


def sma_cross(bars, fast: int = 50, slow: int = 200) -> pd.Series:
    """Long while SMA(fast) > SMA(slow) (golden cross / death cross)."""
    f, s = ta_sma(bars["close"], fast), ta_sma(bars["close"], slow)
    return _flat_until_ready(f > s, f, s)


def trend_filter(bars, window: int = 200) -> pd.Series:
    """Long while close > SMA(window)."""
    m = ta_sma(bars["close"], window)
    return _flat_until_ready(bars["close"] > m, m)


# ------------------------------------------------------------------ mean reversion
def rsi_reversion(bars, n: int = 2, entry: float = 10, exit: float = 70) -> pd.Series:
    """Buy when RSI(n) < entry, sell when RSI(n) > exit."""
    r = ta_rsi(bars["close"], n)
    return enter_exit(r < entry, r > exit)


def dip_buy(bars, n_down: int = 3, hold: int = 3) -> pd.Series:
    """Long for `hold` bars after a bar that completes >= n_down consecutive down closes."""
    down = bars["close"].diff() < 0
    streak = down.groupby((~down).cumsum()).cumsum()
    return (streak >= n_down).astype(float).rolling(hold, min_periods=1).max()


# ------------------------------------------------------------------ momentum
def momentum(bars, lookback: int = 126, threshold: float = 0.0) -> pd.Series:
    """Time-series momentum: long while the past `lookback`-bar return is above threshold."""
    ret = bars["close"].pct_change(lookback)
    return _flat_until_ready(ret > threshold, ret)


# ------------------------------------------------------------------ breakout
def donchian_breakout(bars, entry: int = 55, exit: int = 20) -> pd.Series:
    """Buy a close above the prior `entry`-bar high; sell a close below the prior `exit`-bar low."""
    hi = bars["high"].rolling(entry).max().shift(1)
    lo = bars["low"].rolling(exit).min().shift(1)
    return enter_exit(bars["close"] > hi, bars["close"] < lo)


def bollinger_breakout(bars, window: int = 20, k: float = 2.0) -> pd.Series:
    """Buy a close above the upper band; sell a close below the middle band."""
    mid, up, _ = ta_bb(bars["close"], window, k)
    return enter_exit(bars["close"] > up, bars["close"] < mid)


SIGNALS = {
    "ema_cross": (ema_cross, "trend", {"fast": 10, "slow": 30}),
    "sma_cross": (sma_cross, "trend", {"fast": 50, "slow": 200}),
    "trend_filter": (trend_filter, "trend", {"window": 200}),
    "rsi_reversion": (rsi_reversion, "mean reversion", {"n": 2, "entry": 10, "exit": 70}),
    "dip_buy": (dip_buy, "mean reversion", {"n_down": 3, "hold": 3}),
    "momentum": (momentum, "momentum", {"lookback": 126, "threshold": 0.0}),
    "donchian_breakout": (donchian_breakout, "breakout", {"entry": 55, "exit": 20}),
    "bollinger_breakout": (bollinger_breakout, "breakout", {"window": 20, "k": 2.0}),
}


def target_position(name: str, bars: pd.DataFrame, **params) -> pd.Series:
    """Target position (decided at the close of bar t) for a named signal; params override defaults."""
    fn, _, defaults = SIGNALS[name]
    return fn(bars, **{**defaults, **params}).rename(name)


def next_bar_position(target: pd.Series) -> pd.Series:
    """The position actually HELD during each bar: the target decided one bar earlier."""
    return target.shift(1).fillna(0.0)


def lookahead_test(name: str, bars: pd.DataFrame, checks: int = 25, seed: int = 0, fn=None, **params) -> int:
    """Look-ahead detector. For random dates t it (1) recomputes the signal on data up to t only and
    (2) recomputes it after SHOCKING every bar after t (prices x 1.5 and x 0.5). A signal that uses
    only the past gives identical values up to t in every case; any difference = look-ahead.
    Returns the number of dates that failed."""
    fn = fn or (lambda b: target_position(name, b, **params))
    full = fn(bars)
    rng = np.random.default_rng(seed)
    idx = rng.choice(np.arange(len(bars) // 3, len(bars) - 5), size=min(checks, len(bars) // 2), replace=False)
    price_cols = [c for c in ("open", "high", "low", "close") if c in bars]
    bad = 0
    for i in sorted(idx):
        t = bars.index[i]
        variants = [bars.loc[:t]]
        for k in (1.5, 0.5):
            shocked = bars.copy()
            shocked.iloc[i + 1:, [bars.columns.get_loc(c) for c in price_cols]] *= k
            variants.append(shocked)
        same = all(np.allclose(fn(v).loc[:t].values, full.loc[:t].values, equal_nan=True) for v in variants)
        bad += int(not same)
    return bad


def describe_signal(tgt: pd.Series) -> dict:
    changes = tgt.diff().fillna(tgt).ne(0)
    entries = int(((tgt > 0) & (tgt.shift(1, fill_value=0) == 0)).sum())
    last_change = tgt.index[changes][-1] if changes.any() else None
    return {"latest_target": int(tgt.iloc[-1]), "entries": entries, "exposure": float((tgt != 0).mean()),
            "avg_hold_bars": float((tgt != 0).sum() / entries) if entries else float("nan"),
            "last_change": str(last_change.date()) if last_change is not None else "-"}


def latest_targets(symbols: list[str], name: str, params: dict, start: str, end: str) -> pd.DataFrame:
    rows = []
    for s in symbols:
        b = load_bars(s, start, end)
        t = target_position(name, b, **params)
        rows.append({"symbol": s, "as_of": str(b.index[-1].date()), "close": float(np.round(b["close"].iloc[-1], 2)),
                     "target": int(t.iloc[-1]), "last_change": describe_signal(t)["last_change"]})
    return pd.DataFrame(rows)


def run(symbol: str = "SPY", quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    d = cfg["data"]
    bars = load_bars(symbol, d["start"], d["end"])
    rows, targets = [], {}
    for name, (_, family, defaults) in SIGNALS.items():
        tgt = target_position(name, bars)
        targets[name] = tgt
        rows.append({"signal": name, "family": family, "params": defaults, **describe_signal(tgt),
                     "lookahead_mismatches": lookahead_test(name, bars)})
    df = pd.DataFrame(rows)
    out(f"\nSignal library on {symbol} {bars.index[0].date()} to {bars.index[-1].date()} "
        f"(target decided at close t, held from bar t+1):")
    show = df.assign(exposure=df.exposure.map("{:.0%}".format), avg_hold_bars=df.avg_hold_bars.round(1),
                     lookahead=df.lookahead_mismatches.map(lambda x: "PASS" if x == 0 else f"FAIL ({x})"))
    out(show[["signal", "family", "params", "latest_target", "entries", "exposure", "avg_hold_bars",
              "last_change", "lookahead"]].to_string(index=False))
    t = targets["ema_cross"]
    held = next_bar_position(t)
    flip = t.index[t.diff().fillna(0) != 0][-1]
    i = t.index.get_loc(flip)
    out(f"\nNext-bar alignment, ema_cross: target changes to {int(t.loc[flip])} at the close of {flip.date()}; "
        f"the position is held from {t.index[i + 1].date() if i + 1 < len(t) else 'the next bar'} "
        f"(held on {flip.date()} = {int(held.loc[flip])})")

    s = cfg["strategy"]
    tg = latest_targets(cfg["universe"]["trade"], s["name"], s["params"], d["start"], d["end"])
    path = output_path("Lab07_targets.csv")
    tg.to_csv(path, index=False)
    out(f"\nTarget positions for the configured strategy {s['name']} {s['params']} across the universe:")
    out(tg.to_string(index=False))
    out(f"  -> {int(tg.target.sum())} of {len(tg)} symbols long. Targets -> _outputs/{path.name} (input to the execution stage)")

    view = bars.loc["2024-01-01":]
    pick = ["ema_cross", "rsi_reversion", "momentum", "donchian_breakout"]
    fig, axes = plt.subplots(len(pick), 1, figsize=(11, 8.5), sharex=True)
    for ax, name in zip(axes, pick):
        pos = targets[name].loc[view.index]
        ax.plot(view.index, view["close"], color="#333333", lw=0.9)
        ax.fill_between(view.index, view["close"].min(), view["close"].max(), where=pos > 0, color="#4f9a3b", alpha=0.15)
        ax.set_title(f"{symbol} {name} ({SIGNALS[name][1]}): green = target long", fontsize=9)
    save(fig, "Lab07_signals.png")
    return {"table": df.drop(columns="params").to_dict("records"), "targets": tg.to_dict("records"),
            "lookahead_fail": int((df.lookahead_mismatches > 0).sum())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline signals", description="Stage 07 - signal library")
    ap.add_argument("--symbol", default="SPY")
    a = ap.parse_args(argv)
    stage_banner(7, "signals: trend, mean reversion, momentum, breakout -> target positions")
    return 1 if run(a.symbol.upper())["lookahead_fail"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
