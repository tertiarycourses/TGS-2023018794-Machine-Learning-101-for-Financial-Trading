"""
pipeline/validate.py - Stage 02: cross-check pipeline bars against TradingView.

A trading pipeline must prove its prices are right before anything is built on
them. For each watch-list symbol in config.yaml (AAPL and SGX:D05) this stage
compares three versions of the same daily bar:

  TV        what you read in TradingView's Data Window (entered in tradingview_values.csv)
  RAW       pipeline reference bar, split-adjusted only  = TradingView's default view
  ADJUSTED  pipeline research bar, split- AND dividend-adjusted (what the backtests use)

and writes a validation report. Expect TV to match RAW to the cent and to
differ from ADJUSTED by the dividend-adjustment factor - that is not an error,
but a model trained on adjusted prices must never be sent unadjusted live prices
(or vice versa) without converting.

    python -m pipeline validate --date 2025-12-31
    python -m pipeline validate --tv Lab02-tradingview-charts/tradingview_values.csv
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

from common.config import LAB_ROOT, output_path
from common.data import get_bars
from common.plotting import plt, save
from pipeline.config import PIPELINE_DIR, load_config, stage_banner

REFERENCE_DIR = PIPELINE_DIR / "reference"
DEFAULT_TV_FILE = LAB_ROOT / "Lab02-tradingview-charts" / "tradingview_values.csv"
PRICE_TOL, VOLUME_TOL = 0.001, 0.10          # 0.1% on prices, 10% on volume (venues report volume differently)
FIELDS = ["open", "high", "low", "close", "volume"]


def reference_bars(symbol: str) -> pd.DataFrame:
    """RAW (split-adjusted, dividend-unadjusted) bars with adj_close, from pipeline/reference/."""
    path = REFERENCE_DIR / f"{symbol}_1Day_raw.csv"
    if not path.exists():
        raise FileNotFoundError(f"no reference file {path.name}; add one or remove {symbol} from universe.watch")
    return pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")


def adjusted_bars(symbol: str, raw: pd.DataFrame) -> pd.DataFrame:
    """Research bars: the bundled/Alpaca adjusted file, else RAW x (adj_close / close)."""
    try:
        return get_bars(symbol, str(raw.index[0].date()), str(raw.index[-1].date()))
    except FileNotFoundError:                                  # e.g. D05.SI: no US data source
        factor = raw["adj_close"] / raw["close"]
        adj = raw[["open", "high", "low", "close"]].mul(factor, axis=0)
        adj["volume"] = raw["volume"]
        return adj


def load_tv_values(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    df["date"] = pd.to_datetime(df["date"])
    return df


def compare(tv_row: dict, bar: pd.Series) -> dict:
    """Percentage difference per field and whether all fields are inside tolerance."""
    diffs = {f: (float(tv_row[f]) / float(bar[f]) - 1.0) for f in FIELDS if pd.notna(tv_row.get(f))}
    ok = all(abs(d) <= (VOLUME_TOL if f == "volume" else PRICE_TOL) for f, d in diffs.items())
    return {"diffs": diffs, "match": ok}


def run(date: str = "2025-12-31", tv_file: Path | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    tv_file = Path(tv_file or DEFAULT_TV_FILE)
    tv = load_tv_values(tv_file) if tv_file.exists() else pd.DataFrame()
    out(f"TradingView values file: {tv_file.relative_to(LAB_ROOT) if tv_file.is_relative_to(LAB_ROOT) else tv_file}"
        f" ({len(tv)} rows)")
    rows, curves = [], {}
    for item in cfg["universe"]["watch"]:
        sym, tv_sym = item["symbol"], item["tradingview"]
        raw = reference_bars(sym)
        adj = adjusted_bars(sym, raw)
        d = pd.Timestamp(date)
        if d not in raw.index:
            out(f"\n{tv_sym}: {date} is not a trading day in the reference data")
            continue
        r, a = raw.loc[d], adj.loc[d]
        factor = a["close"] / r["close"]
        out(f"\n{tv_sym} ({sym}, {item['currency']}) bar for {date}")
        out(f"  {'':<26}{'open':>10}{'high':>10}{'low':>10}{'close':>10}{'volume':>14}")
        out(f"  {'RAW (TradingView default)':<26}" + "".join(f"{r[f]:>10.2f}" for f in FIELDS[:4]) + f"{r['volume']:>14,.0f}")
        out(f"  {'ADJUSTED (research)':<26}" + "".join(f"{a[f]:>10.2f}" for f in FIELDS[:4]) + f"{a['volume']:>14,.0f}")
        out(f"  dividend-adjustment factor {factor:.4f}: adjusted = raw x factor, because dividends paid AFTER "
            f"this bar (up to the data download date) are back-adjusted into history")
        hist = raw.loc[:d]
        out(f"  change vs prior close {r['close'] / hist['close'].iloc[-2] - 1:+.2%} | 52-week high/low "
            f"{hist['high'].tail(252).max():.2f} / {hist['low'].tail(252).min():.2f} (raw) | "
            f"20-day avg volume {hist['volume'].tail(20).mean():,.0f}")
        row = {"tradingview_symbol": tv_sym, "symbol": sym, "date": date, "raw_close": r["close"],
               "adjusted_close": round(float(a["close"]), 4), "adj_factor": round(float(factor), 4)}
        mine = tv[(tv["tradingview_symbol"] == tv_sym) & (tv["date"] == d)] if len(tv) else tv
        if len(mine):
            t = mine.iloc[0].to_dict()
            c_raw, c_adj = compare(t, r), compare(t, a)
            verdict = ("PASS - TradingView matches RAW (dividend-unadjusted) bars" if c_raw["match"] else
                       "PASS - TradingView matches ADJUSTED bars ('Adjust data for dividends' is ticked)" if c_adj["match"]
                       else "FAIL - TradingView matches neither series: check symbol, date, timeframe and session")
            out(f"  {'TradingView (you)':<26}" + "".join(f"{float(t[f]):>10.2f}" for f in FIELDS[:4])
                + f"{float(t['volume']):>14,.0f}")
            out("  diff vs RAW      " + "  ".join(f"{f} {v:+.3%}" for f, v in c_raw["diffs"].items()))
            out("  diff vs ADJUSTED " + "  ".join(f"{f} {v:+.3%}" for f, v in c_adj["diffs"].items()))
            out(f"  -> {verdict}")
            row.update({"tv_close": float(t["close"]), "match_raw": c_raw["match"], "match_adjusted": c_adj["match"],
                        "verdict": verdict.split(" - ")[0]})
        else:
            out("  -> no TradingView row for this symbol/date: read the Data Window and add it to the CSV")
            row["verdict"] = "MISSING"
        rows.append(row)
        curves[tv_sym] = (raw["close"].loc["2025-01-01":], adj["close"].loc["2025-01-01":], d)

    report = pd.DataFrame(rows)
    path = output_path("Lab02_validation_report.csv")
    report.to_csv(path, index=False)
    out(f"\nValidation report -> _outputs/{path.name}")
    passed = int((report.get("verdict", pd.Series(dtype=str)) == "PASS").sum())
    out(f"RESULT: {passed}/{len(report)} watch-list symbols validated against TradingView")

    fig, axes = plt.subplots(1, len(curves), figsize=(6 * len(curves), 4), squeeze=False)
    for ax, (name, (rc, ac, d)) in zip(axes[0], curves.items()):
        ax.plot(rc.index, rc, label="RAW = TradingView default", lw=1.3)
        ax.plot(ac.index, ac, label="ADJUSTED = research data", lw=1.3)
        ax.axvline(d, color="#7f7f7f", ls=":", lw=1)
        ax.set_title(f"{name}: raw vs dividend-adjusted close, 2025")
        ax.legend(loc="upper left")
    save(fig, "Lab02_validation.png")
    return {"rows": rows, "passed": passed, "report": str(path)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline validate", description="Stage 02 - TradingView data validation")
    ap.add_argument("--date", default="2025-12-31")
    ap.add_argument("--tv", default=None, help="CSV of values read from the TradingView Data Window")
    a = ap.parse_args(argv)
    stage_banner(2, "data validation against TradingView")
    run(a.date, Path(a.tv) if a.tv else None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
