"""
pipeline/indicators.py - Stage 05: Python twins of the desk's Pine Script indicators.

Every function mirrors a Pine Script v6 built-in so the values in the pipeline
match the values on the TradingView chart (Lab05 lcc_trend_bands.pine and
lcc_rsi.pine):

    ta_sma(src, n)        = ta.sma        ta_ema(src, n)      = ta.ema
    ta_rsi(src, n)        = ta.rsi        ta_bb(src, n, k)    = ta.bb   -> (middle, upper, lower)
    ta_atr(bars, n)       = ta.atr        ta_macd(src, f, s, g) = ta.macd
    ta_crossover(a, b)    = ta.crossover  ta_crossunder(a, b) = ta.crossunder

All values at bar t use data up to and including bar t only.

    python -m pipeline indicators --symbol AAPL --date 2025-12-31
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys
from pathlib import Path

import pandas as pd

from common import indicators as I
from common.config import LAB_ROOT, output_path
from common.plotting import plt, save
from pipeline.config import load_config, stage_banner
from pipeline.ingest import load_bars

DEFAULT_TV_FILE = LAB_ROOT / "Lab05-pine-indicators" / "tradingview_indicator_values.csv"


# ------------------------------------------------------------------ Pine built-in twins
def ta_sma(src: pd.Series, length: int) -> pd.Series:
    return I.sma(src, length)


def ta_ema(src: pd.Series, length: int) -> pd.Series:
    return I.ema(src, length)


def ta_rsi(src: pd.Series, length: int = 14) -> pd.Series:
    return I.rsi(src, length)


def ta_bb(src: pd.Series, length: int = 20, mult: float = 2.0):
    bb = I.bollinger(src, length, mult)
    return bb["middle"], bb["upper"], bb["lower"]


def ta_atr(bars: pd.DataFrame, length: int = 14) -> pd.Series:
    return I.atr(bars, length)


def ta_macd(src: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    m = I.macd(src, fast, slow, signal)
    return m["macd"], m["signal"], m["hist"]


def ta_crossover(a: pd.Series, b: pd.Series) -> pd.Series:
    """True on the bar where a moves from <= b to > b."""
    return (a > b) & (a.shift(1) <= b.shift(1))


def ta_crossunder(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a < b) & (a.shift(1) >= b.shift(1))


# ------------------------------------------------------------------ the two desk indicators
def lcc_trend_bands(bars: pd.DataFrame, fast: int = 20, slow: int = 50, bb_len: int = 20,
                    bb_mult: float = 2.0) -> pd.DataFrame:
    """Twin of lcc_trend_bands.pine: EMA fast/slow, Bollinger Bands, crossover flags."""
    c = bars["close"]
    out = pd.DataFrame({"close": c, "ema_fast": ta_ema(c, fast), "ema_slow": ta_ema(c, slow)})
    out["bb_middle"], out["bb_upper"], out["bb_lower"] = ta_bb(c, bb_len, bb_mult)
    out["bull_cross"] = ta_crossover(out["ema_fast"], out["ema_slow"])
    out["bear_cross"] = ta_crossunder(out["ema_fast"], out["ema_slow"])
    return out


def lcc_rsi(bars: pd.DataFrame, length: int = 14, overbought: int = 70, oversold: int = 30) -> pd.DataFrame:
    """Twin of lcc_rsi.pine: RSI and its two alertcondition() events."""
    r = ta_rsi(bars["close"], length)
    return pd.DataFrame({"rsi": r, "alert_oversold": ta_crossunder(r, pd.Series(oversold, index=r.index)),
                         "alert_overbought": ta_crossover(r, pd.Series(overbought, index=r.index))})


def indicator_table(bars: pd.DataFrame) -> pd.DataFrame:
    return lcc_trend_bands(bars).join(lcc_rsi(bars))


SNAPSHOT_FIELDS = ["close", "ema_fast", "ema_slow", "bb_upper", "bb_middle", "bb_lower", "rsi"]


def run(symbol: str = "AAPL", date: str = "2025-12-31", tv_file: Path | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    adj = indicator_table(load_bars(symbol, cfg["data"]["start"], date))
    series = {"Python ADJUSTED": adj}
    try:                                                       # TradingView shows RAW prices by default
        from pipeline.validate import reference_bars
        raw = reference_bars(symbol).loc[:date]
        series["Python RAW (TV default)"] = indicator_table(raw)
    except FileNotFoundError:
        pass
    d = pd.Timestamp(date)
    snap = pd.DataFrame({name: t.loc[d, SNAPSHOT_FIELDS] for name, t in series.items()}).astype(float)
    tv_file = Path(tv_file or DEFAULT_TV_FILE)
    if tv_file.exists():
        tv = pd.read_csv(tv_file, comment="#")
        tv = tv[(tv["symbol"] == symbol) & (pd.to_datetime(tv["date"]) == d)]
        if len(tv):
            snap["TradingView (you)"] = tv.iloc[0][SNAPSHOT_FIELDS].astype(float).values
            base = "Python RAW (TV default)" if "Python RAW (TV default)" in snap else "Python ADJUSTED"
            snap["diff vs " + base.split(" (")[0].replace("Python ", "")] = (snap["TradingView (you)"] / snap[base] - 1)

    out(f"\n{symbol} on {date} - lcc_trend_bands.pine (EMA 20/50, BB 20/2) and lcc_rsi.pine (RSI 14):")
    fmt = snap.copy().astype(object)
    for col in snap:
        fmt[col] = snap[col].map((lambda v: f"{v:+.3%}") if col.startswith("diff") else (lambda v: f"{v:.2f}"))
    out(fmt.to_string())
    last = adj.loc[:d].iloc[-1]
    out(f"  trend {'UP' if last.ema_fast > last.ema_slow else 'DOWN'} (EMA20 {'>' if last.ema_fast > last.ema_slow else '<'} EMA50)"
        f" | close {'inside' if last.bb_lower <= last.close <= last.bb_upper else 'outside'} the bands | RSI {last.rsi:.1f}")
    view = adj.loc["2024-06-01":date]
    out(f"  Since 2024-06-01: {int(view.bull_cross.sum())} bullish and {int(view.bear_cross.sum())} bearish EMA crosses, "
        f"{int(view.alert_oversold.sum())} RSI-oversold and {int(view.alert_overbought.sum())} RSI-overbought alert events")
    if "TradingView (you)" in snap:
        worst = snap.filter(like="diff").abs().max().max()
        out(f"  -> largest gap to TradingView {worst:.3%}: "
            + ("PASS (<= 0.5%, warm-up/rounding only)" if worst <= 0.005 else "CHECK settings, price adjustment and warm-up"))
    csv = output_path(f"Lab05_{symbol}_indicators.csv")
    adj.loc["2024-01-01":date].round(4).to_csv(csv)
    out(f"  Indicator table -> _outputs/{csv.name}")

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True, gridspec_kw={"height_ratios": [3, 1.2]})
    ax.plot(view.index, view.close, color="#333333", lw=1, label="Close")
    ax.plot(view.index, view.ema_fast, color="tab:blue", lw=1.6, label="EMA 20")
    ax.plot(view.index, view.ema_slow, color="tab:orange", lw=1.6, label="EMA 50")
    ax.fill_between(view.index, view.bb_lower, view.bb_upper, color="gray", alpha=0.12, label="Bollinger (20, 2)")
    ax.scatter(view.index[view.bull_cross], view.ema_fast[view.bull_cross] * 0.97, marker="^", color="green", s=60,
               label="ta.crossover")
    ax.scatter(view.index[view.bear_cross], view.ema_fast[view.bear_cross] * 1.03, marker="v", color="red", s=60,
               label="ta.crossunder")
    ax.set_title(f"{symbol}: pipeline twin of 'LCC Trend & Bollinger Bands' (Pine Script v6)")
    ax.legend(loc="upper left", ncol=3)
    ax2.plot(view.index, view.rsi, color="purple", lw=1.2)
    ax2.axhline(70, color="red", ls="--", lw=0.8)
    ax2.axhline(30, color="green", ls="--", lw=0.8)
    ax2.set_ylabel("RSI(14)")
    save(fig, "Lab05_pine_preview.png")
    return {"snapshot": snap.round(4).to_dict(), "bull": int(view.bull_cross.sum()), "bear": int(view.bear_cross.sum())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline indicators", description="Stage 05 - indicator twins")
    ap.add_argument("--symbol", default="AAPL")
    ap.add_argument("--date", default="2025-12-31")
    ap.add_argument("--tv", default=None, help="CSV of indicator values read from TradingView")
    a = ap.parse_args(argv)
    stage_banner(5, "indicators: Python twins of the Pine Script indicators")
    run(a.symbol.upper(), a.date, Path(a.tv) if a.tv else None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
