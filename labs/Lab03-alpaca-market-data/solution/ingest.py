"""
pipeline/ingest.py - Stage 03: `python -m pipeline ingest`

Fetch bars for every symbol in the universe at every configured timeframe
(1Day, 1Week, 1Month, 1Hour), run data-quality checks, and cache the clean
result in labs/_cache/ so every later stage reads the same data. A sample
UNSTRUCTURED source (news headlines) is ingested next to the structured bars.

Online : Alpaca Market Data API (IEX feed, adjusted) + Alpaca News API
Offline: bundled CSVs in labs/data + SYNTHETIC sample headlines

Later stages call load_bars() / load_closes(), which read the cache when it
exists and fall back to the data source when it does not.
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from common.config import get_keys, is_online, output_path
from common.data import data_source, get_bars
from common.plotting import plt, save
from pipeline.config import PIPELINE_DIR, lab_path, load_config, stage_banner

COLUMNS = ["open", "high", "low", "close", "volume"]

# Forms of data a desk can feed into the pipeline (structured -> unstructured)
DATA_FORMS = [
    ("Bars (OHLCV)", "structured", "Alpaca StockBarsRequest", "ingested here - every stage uses them"),
    ("Quotes (bid/ask)", "structured", "Alpaca StockLatestQuoteRequest", "spread -> execution cost (Lab 8)"),
    ("Trades (ticks)", "structured", "Alpaca StockTradesRequest", "VWAP, order flow; high velocity"),
    ("Corporate actions", "structured", "Alpaca corporate actions API", "splits / dividends -> adjustment (Lab 2)"),
    ("Fundamentals", "structured", "filings, data vendors", "earnings, valuation ratios"),
    ("News headlines", "unstructured text", "Alpaca NewsClient / NewsRequest", "ingested here - sentiment agent (Lab 20)"),
    ("Alternative data", "unstructured / mixed", "web, satellite, card spend, social", "big-data signals; needs governance"),
]


# ------------------------------------------------------------------ cache helpers used by later stages
def cache_dir() -> Path:
    return lab_path(load_config()["data"]["cache_dir"])


def cache_file(symbol: str, timeframe: str) -> Path:
    return cache_dir() / "bars" / f"{symbol}_{timeframe}.csv"


def _read_cache(path: Path, timeframe: str) -> pd.DataFrame:
    if timeframe.endswith(("Min", "Hour")):
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("America/New_York")
        df = df.set_index("timestamp")
    else:
        df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    return df[COLUMNS].astype(float)


def load_bars(symbol: str, start: str | None = None, end: str | None = None, timeframe: str = "1Day") -> pd.DataFrame:
    """Bars from the ingest cache (offline, or a fixed end date) else straight from the data source."""
    path = cache_file(symbol, timeframe)
    if path.exists() and not (is_online() and end is None):
        df = _read_cache(path, timeframe)
        tz = df.index.tz
        if start:
            df = df[df.index >= pd.Timestamp(start, tz=tz)]
        if end:                                  # weekly/monthly bars are labelled with the period END
            lag = {"1Week": pd.Timedelta(days=6), "1Month": pd.Timedelta(days=30)}.get(timeframe, pd.Timedelta(0))
            df = df[df.index - lag <= pd.Timestamp(end, tz=tz) + pd.Timedelta(hours=23, minutes=59)]
        if len(df):
            return df
    return get_bars(symbol, start, end, timeframe)


def load_closes(symbols: list[str], start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Daily closes side by side (inner join on dates) - same contract as common.data.get_closes."""
    return pd.DataFrame({s: load_bars(s, start, end)["close"] for s in symbols}).dropna()


def load_headlines(symbols: list[str] | None = None) -> list[dict]:
    path = cache_dir() / "news" / "headlines.json"
    data = json.loads(path.read_text()) if path.exists() else _fetch_headlines(symbols or [])
    return [h for h in data["headlines"] if not symbols or h["symbol"] in symbols]


# ------------------------------------------------------------------ quality checks
def quality_checks(df: pd.DataFrame, timeframe: str, end: str, max_move: float) -> dict:
    """Return a dict of check -> count (0 = clean) plus coverage facts."""
    idx = df.index
    rets = df["close"].pct_change()
    daily = timeframe == "1Day"
    gaps = idx.to_series().diff().dt.days if daily else pd.Series(dtype=float)
    end_ts = pd.Timestamp(end, tz=idx.tz) if len(idx) else None
    return {
        "rows": len(df), "first": str(idx[0])[:10 if daily else 16] if len(df) else "-",
        "last": str(idx[-1])[:10 if daily else 16] if len(df) else "-",
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_timestamps": int(idx.duplicated().sum()),
        "not_sorted": int(not idx.is_monotonic_increasing),
        "high_below_low": int((df["high"] < df["low"]).sum()),
        "close_outside_range": int(((df["close"] > df["high"] + 1e-9) | (df["close"] < df["low"] - 1e-9)).sum()),
        "zero_volume": int((df["volume"] == 0).sum()),
        "gaps_over_4_days": int((gaps > 4).sum()) if daily else 0,
        "big_moves": int((rets.abs() > max_move).sum()) if daily else 0,
        "stale": int(bool(daily and len(df) and idx[-1] < end_ts - pd.Timedelta(days=5))),
    }


BLOCKING = ["missing_values", "duplicate_timestamps", "not_sorted", "high_below_low", "close_outside_range", "stale"]


def _fetch_headlines(symbols: list[str]) -> dict:
    """Alpaca News online; bundled SYNTHETIC headlines offline (or if the API fails)."""
    if is_online():
        try:
            from alpaca.data.historical.news import NewsClient
            from alpaca.data.requests import NewsRequest
            key, secret = get_keys()
            client = NewsClient(api_key=key, secret_key=secret)
            rows = []
            for s in symbols:
                news = client.get_news(NewsRequest(symbols=s, start=datetime.now() - timedelta(days=7), limit=10))
                rows += [{"date": str(n.created_at)[:10], "symbol": s, "headline": n.headline}
                         for n in news.data.get("news", [])]
            return {"_source": "Alpaca News API", "headlines": rows}
        except Exception as exc:
            print(f"  [news] Alpaca News unavailable ({type(exc).__name__}); using bundled sample headlines")
    data = json.loads((PIPELINE_DIR / "reference" / "sample_headlines.json").read_text())
    data["_source"] = "bundled SYNTHETIC sample (training only - not real news)"
    return data


# ------------------------------------------------------------------ the stage
def run(symbols: list[str] | None = None, timeframes: list[str] | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    d = cfg["data"]
    uni = cfg["universe"]
    symbols = symbols or sorted(set(uni["trade"]) | {s for p in uni["pairs"] for s in p} | {uni["benchmark"]})
    timeframes = timeframes or d["timeframes"]
    (cache_dir() / "bars").mkdir(parents=True, exist_ok=True)
    (cache_dir() / "news").mkdir(parents=True, exist_ok=True)
    out(f"Source: {data_source()} | {len(symbols)} symbols x {len(timeframes)} timeframes -> {cache_dir().name}/")

    rows, manifest = [], {"ingested_at": datetime.now().isoformat(timespec="seconds"), "source": data_source(), "files": {}}
    for sym in symbols:
        for tf in timeframes:
            start, end = (d["hourly_window"] if tf == "1Hour" else (d["start"], d["end"]))
            try:
                df = get_bars(sym, start, end, tf)
            except FileNotFoundError:
                rows.append({"symbol": sym, "timeframe": tf, "rows": 0, "status": "not available offline"})
                continue
            q = quality_checks(df, tf, end, d["max_abs_daily_move"])
            status = "FAIL" if any(q[k] for k in BLOCKING) else ("CHECK" if q["big_moves"] or q["zero_volume"] else "OK")
            rows.append({"symbol": sym, "timeframe": tf, **q, "status": status})
            if status != "FAIL":
                path = cache_file(sym, tf)
                df.to_csv(path, index_label="timestamp")
                manifest["files"][path.name] = {"rows": q["rows"], "first": q["first"], "last": q["last"], "status": status}

    qdf = pd.DataFrame(rows)
    qpath = output_path("Lab03_data_quality.csv")
    qdf.to_csv(qpath, index=False)
    daily = qdf[qdf["timeframe"] == "1Day"]
    out("\nData-quality report, daily bars (0 = clean):")
    cols = ["symbol", "rows", "first", "last", "missing_values", "duplicate_timestamps", "gaps_over_4_days",
            "zero_volume", "big_moves", "high_below_low", "status"]
    out(daily[cols].astype({c: int for c in cols if c not in ("symbol", "first", "last", "status")}).to_string(index=False))
    per_tf = qdf.groupby("timeframe")["rows"].agg(["sum", "max"]).reindex(timeframes)
    out("\nBars cached per timeframe (all symbols / largest single file):")
    for tf, r in per_tf.iterrows():
        na = int((qdf[(qdf.timeframe == tf)].status == "not available offline").sum())
        out(f"  {tf:<7} {int(r['sum']):>7,} bars  (max {int(r['max']):,} per symbol)"
            + (f"  - {na} symbols not available offline" if na else ""))

    news = _fetch_headlines(uni["trade"])
    (cache_dir() / "news" / "headlines.json").write_text(json.dumps(news, indent=2))
    by_sym = pd.Series([h["symbol"] for h in news["headlines"]]).value_counts()
    out(f"\nUnstructured data: {len(news['headlines'])} headlines ({news['_source']}) "
        f"for {', '.join(f'{s} {n}' for s, n in by_sym.items())}")

    spy, aapl = load_bars("SPY", d["start"], d["end"]), load_bars("AAPL", d["start"], d["end"])
    rets = pd.DataFrame({"SPY": spy["close"].pct_change(), "AAPL": aapl["close"].pct_change()}).dropna()
    out("\nReturn statistics (daily, annualised):")
    for col in rets:
        r = rets[col]
        out(f"  {col:<5} mean {r.mean() * 252:7.2%}  vol {r.std() * np.sqrt(252):7.2%}  skew {r.skew():5.2f}  "
            f"excess kurtosis {r.kurt():5.2f}  moves > {d['max_abs_daily_move']:.0%}: {int((r.abs() > d['max_abs_daily_move']).sum())}")
    out(f"  correlation SPY-AAPL {rets.corr().iloc[0, 1]:.2f}  -> fat tails: never assume normal returns for risk")

    cells = int(qdf["rows"].fillna(0).sum()) * len(COLUMNS)
    out("\nForms of data and the 3 Vs of big data:")
    for form, kind, src, use in DATA_FORMS:
        out(f"  - {form:<18} {kind:<20} {src:<32} {use}")
    out(f"  Volume  : {int(qdf['rows'].fillna(0).sum()):,} bars = {cells:,} numbers cached today; 1-minute bars for 500 "
        f"stocks would add ~{500 * 390 * 252 / 1e6:.0f} million rows a year")
    out("  Velocity: daily bars arrive once a day, hourly 7 a day, ticks thousands a second")
    out("  Variety : structured bars + unstructured headlines -> different storage, cleaning and governance")

    manifest["headlines"] = len(news["headlines"])
    (cache_dir() / "manifest.json").write_text(json.dumps(manifest, indent=2))
    failed = int((qdf["status"] == "FAIL").sum())
    out(f"\nQuality report -> _outputs/{qpath.name} | manifest -> {cache_dir().name}/manifest.json")
    out(f"RESULT: {len(manifest['files'])} files cached, {failed} failed quality checks")

    hourly = load_bars("SPY", *d["hourly_window"], timeframe="1Hour")
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    closes = load_closes(uni["trade"], d["start"], d["end"])
    (100 * closes / closes.iloc[0]).plot(ax=axes[0, 0], lw=0.9, logy=True)
    axes[0, 0].set_title("Universe: growth of 100 (daily, adjusted, log)")
    axes[0, 0].legend(fontsize=7, ncol=3)
    axes[0, 1].hist(rets["SPY"], bins=80, alpha=0.7, label="SPY")
    axes[0, 1].hist(rets["AAPL"], bins=80, alpha=0.5, label="AAPL")
    axes[0, 1].set_title("Daily returns: fat tails")
    axes[0, 1].legend()
    (rets["SPY"].rolling(21).std() * np.sqrt(252)).plot(ax=axes[1, 0], color="#c0504d")
    axes[1, 0].set_title("SPY 21-day rolling volatility (annualised)")
    axes[1, 1].plot(range(len(hourly)), hourly["close"].values, lw=0.8)
    axes[1, 1].set_title(f"SPY hourly closes {d['hourly_window'][0]} to {d['hourly_window'][1]} ({len(hourly)} bars)")
    save(fig, "Lab03_market_data.png")
    return {"files": len(manifest["files"]), "failed": failed, "headlines": len(news["headlines"]),
            "spy_daily_rows": int(len(spy)), "spy_hourly_rows": int(len(hourly))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline ingest", description="Stage 03 - ingestion + data quality")
    ap.add_argument("--symbols", nargs="+", default=None)
    ap.add_argument("--timeframes", nargs="+", default=None)
    a = ap.parse_args(argv)
    stage_banner(3, "ingestion: multi-timeframe bars, headlines, data quality")
    res = run([s.upper() for s in a.symbols] if a.symbols else None, a.timeframes)
    return 1 if res["failed"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
