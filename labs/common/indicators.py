"""
indicators.py - classic technical indicators written with plain pandas.

Every function only uses data up to and including bar t to compute the value at
bar t (no centred windows, no shift(-1)), so the values are safe to use as
signals that are then traded on the NEXT bar.

The definitions match TradingView's built-ins (ta.sma, ta.ema, ta.rsi, ta.macd,
ta.bb, ta.atr, ta.vwap, ta.obv) so learners can cross-check Python against
their Pine Script charts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average: mean of the last `window` values."""
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential moving average with alpha = 2 / (span + 1) (TradingView ta.ema)."""
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index using Wilder's smoothing (alpha = 1 / window).

    RS  = Wilder-average(gains) / Wilder-average(losses)
    RSI = 100 - 100 / (1 + RS)        -> 0..100; <30 'oversold', >70 'overbought'
    """
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    return out.where(avg_loss != 0.0, 100.0).where(avg_gain.notna())


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """MACD line = EMA(fast) - EMA(slow); signal = EMA(signal) of MACD; hist = MACD - signal."""
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def bollinger(close: pd.Series, window: int = 20, k: float = 2.0) -> pd.DataFrame:
    """Bollinger Bands: middle = SMA(window); upper/lower = middle +/- k * stdev.

    Uses the population standard deviation (ddof=0) like TradingView.
    pct_b  = (close - lower) / (upper - lower)   (0 = on lower band, 1 = on upper band)
    width  = (upper - lower) / middle
    """
    mid = sma(close, window)
    sd = close.rolling(window, min_periods=window).std(ddof=0)
    upper, lower = mid + k * sd, mid - k * sd
    return pd.DataFrame({"middle": mid, "upper": upper, "lower": lower,
                         "pct_b": (close - lower) / (upper - lower),
                         "width": (upper - lower) / mid})


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range (Wilder). True range = max(H-L, |H-prevC|, |L-prevC|)."""
    prev_close = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - prev_close).abs(),
                    (df["low"] - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()


def vwap(df: pd.DataFrame, window: int | None = None) -> pd.Series:
    """Volume-weighted average price using the typical price (H+L+C)/3.

    Intraday bars (tz-aware index): resets every trading session, like ta.vwap.
    Daily bars: rolling `window`-day VWAP (default 20) because a daily session
    VWAP would just equal the typical price.
    """
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = typical * df["volume"]
    if window is None and df.index.tz is not None:
        session = df.index.date
        return pv.groupby(session).cumsum() / df["volume"].groupby(session).cumsum()
    window = window or 20
    return pv.rolling(window).sum() / df["volume"].rolling(window).sum()


def obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume: running total of +volume on up days and -volume on down days."""
    direction = np.sign(df["close"].diff()).fillna(0.0)
    return (direction * df["volume"]).cumsum()


def add_all(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of an OHLCV frame with the standard lab indicator columns added."""
    out = df.copy()
    out["sma_50"], out["sma_200"] = sma(out["close"], 50), sma(out["close"], 200)
    out["ema_20"], out["ema_50"] = ema(out["close"], 20), ema(out["close"], 50)
    out["rsi_14"] = rsi(out["close"], 14)
    out = out.join(macd(out["close"]))
    out = out.join(bollinger(out["close"]).add_prefix("bb_"))
    out["atr_14"] = atr(out, 14)
    out["vwap_20"] = vwap(out, 20)
    out["obv"] = obv(out)
    return out
