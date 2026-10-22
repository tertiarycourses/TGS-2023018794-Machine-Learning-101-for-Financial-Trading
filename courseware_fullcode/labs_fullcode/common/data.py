"""
data.py - one function to get OHLCV bars, online (Alpaca) or offline (CSV).

    df = get_bars("SPY", "2018-01-01", "2025-12-31", timeframe="1Day")

Returns a DataFrame indexed by `timestamp` with columns open, high, low, close,
volume. Daily bars are tz-naive dates; intraday bars are US/Eastern timestamps.

Online : alpaca-py StockHistoricalDataClient + StockBarsRequest
         (adjustment=ALL so splits and dividends are adjusted, feed=IEX which is
         free on every Alpaca account).
Offline: labs/data/<SYMBOL>.csv (daily) or <SYMBOL>_1Hour.csv (hourly),
         downloaded from Yahoo Finance with yfinance (auto_adjust=True).
         Weekly / monthly bars are resampled from the daily file.
"""
from __future__ import annotations

import re

import pandas as pd

from common.config import DATA_DIR, get_keys, is_online

COLUMNS = ["open", "high", "low", "close", "volume"]
RESAMPLE_RULES = {"1Week": "W-FRI", "1Month": "ME"}


def _alpaca_timeframe(timeframe: str):
    """Translate '1Day', '1Hour', '15Min', '1Week', '1Month' to an alpaca TimeFrame."""
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

    units = {"Min": TimeFrameUnit.Minute, "Hour": TimeFrameUnit.Hour, "Day": TimeFrameUnit.Day,
             "Week": TimeFrameUnit.Week, "Month": TimeFrameUnit.Month}
    for suffix, unit in units.items():
        if timeframe.endswith(suffix):
            amount = int(timeframe[: -len(suffix)] or 1)
            return TimeFrame(amount, unit)
    raise ValueError(f"Unsupported timeframe: {timeframe}")


def _bars_from_alpaca(symbol, start, end, timeframe) -> pd.DataFrame:
    from alpaca.data.enums import Adjustment, DataFeed
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest

    key, secret = get_keys()
    client = StockHistoricalDataClient(api_key=key, secret_key=secret)
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=_alpaca_timeframe(timeframe),
        start=pd.Timestamp(start).to_pydatetime(),
        end=pd.Timestamp(end).to_pydatetime() if end else None,
        adjustment=Adjustment.ALL,
        feed=DataFeed.IEX,
    )
    df = client.get_stock_bars(request).df            # MultiIndex (symbol, timestamp)
    if df.empty:
        raise RuntimeError(f"Alpaca returned no bars for {symbol}")
    df = df.xs(symbol, level="symbol")[COLUMNS]
    if timeframe.endswith(("Day", "Week", "Month")):
        df.index = df.index.tz_convert("America/New_York").tz_localize(None).normalize()
    else:
        df.index = df.index.tz_convert("America/New_York")
    df.index.name = "timestamp"
    return df


def _bars_from_csv(symbol, start, end, timeframe) -> pd.DataFrame:
    if timeframe.endswith(("Min", "Hour")):
        path = DATA_DIR / f"{symbol}_{timeframe}.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"No offline {timeframe} file for {symbol} ({path.name}). "
                "Offline intraday data is bundled for SPY 1Hour only.")
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("America/New_York")
        df = df.set_index("timestamp")
        tz = "America/New_York"
    else:
        path = DATA_DIR / f"{symbol}.csv"
        if not path.exists():
            raise FileNotFoundError(f"No offline data for {symbol}: expected {path}")
        df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
        tz = None
    if start:
        df = df[df.index >= pd.Timestamp(start, tz=tz)]
    if end:
        df = df[df.index <= pd.Timestamp(end, tz=tz) + pd.Timedelta(hours=23, minutes=59)]
    if timeframe in RESAMPLE_RULES:
        df = df.resample(RESAMPLE_RULES[timeframe]).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()
    return df[COLUMNS].astype(float)


def get_bars(symbol: str, start: str | None = "2018-01-01", end: str | None = None,
             timeframe: str = "1Day") -> pd.DataFrame:
    """OHLCV bars for one symbol from Alpaca (online) or bundled CSV (offline)."""
    if is_online():
        try:
            return _bars_from_alpaca(symbol, start, end, timeframe)
        except Exception as exc:                       # keep the class moving
            short = " ".join(re.sub(r"<[^>]+>", " ", str(exc)).split())[:100]   # strip HTML error pages
            print(f"[data] Alpaca request failed ({short}); falling back to bundled CSV.")
    return _bars_from_csv(symbol, start, end, timeframe)


def get_closes(symbols: list[str], start="2018-01-01", end=None) -> pd.DataFrame:
    """Daily close prices for several symbols side by side (inner-joined dates)."""
    closes = {s: get_bars(s, start, end)["close"] for s in symbols}
    return pd.DataFrame(closes).dropna()


def data_source() -> str:
    return "Alpaca Market Data API (IEX feed)" if is_online() else "Bundled CSV (Yahoo Finance via yfinance)"
