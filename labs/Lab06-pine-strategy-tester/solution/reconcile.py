"""
pipeline/reconcile.py - Stage 06: reconcile the TradingView Strategy Tester with the pipeline.

A strategy prototyped in Pine Script is only promoted into the pipeline when an
independent Python backtest reproduces it. This stage:

  1. parses the Pine strategy file (inputs and strategy() settings)
  2. checks the settings match the pipeline's assumptions (next-bar-open fills,
     commission per order, slippage, 100% of equity, long only)
  3. runs the same rules through the pipeline backtester with the same costs
  4. prints the Strategy Tester equivalents and the trade list
  5. compares them with the numbers you copied from TradingView
     (Lab06-pine-strategy-tester/tv_strategy_results.yaml) and explains gaps

    python -m pipeline reconcile --symbol SPY --fast 50 --slow 200
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import re
import sys
from pathlib import Path

import yaml

from common import metrics as M
from common.backtest import backtest, buy_and_hold, cross_signal
from common.config import LAB_ROOT, output_path
from common.plotting import plot_equity_and_drawdown
from pipeline.config import load_config, stage_banner, tradingview_cost_model
from pipeline.indicators import ta_sma
from pipeline.ingest import load_bars

LAB06 = LAB_ROOT / "Lab06-pine-strategy-tester"
PINE_FILE = LAB06 / "lcc_ma_crossover_strategy.pine"
TV_RESULTS = LAB06 / "tv_strategy_results.yaml"
CAUSES = ["adjusted (pipeline) vs unadjusted (TradingView default) prices",
          "history start: the pipeline data begins 2018-01-02, so SMA 200 is only warm from Oct 2018",
          "whole shares on TradingView vs fractional equity in the pipeline",
          "slippage in ticks (TradingView) vs basis points (pipeline)"]


def parse_pine(path: Path) -> dict:
    """Read input defaults and strategy() keyword settings from a Pine v6 strategy file."""
    text = path.read_text()
    settings = dict(re.findall(r"(\w+)\s*=\s*([\w.]+)\s*[,)]", text.split("strategy(", 1)[1].split(")\n", 1)[0]))
    inputs = dict(re.findall(r"(\w+)\s*=\s*input\.int\((\d+)", text))
    return {"version": re.search(r"//@version=(\d+)", text).group(1), "settings": settings,
            "inputs": {k: int(v) for k, v in inputs.items()}}


def settings_checks(pine: dict, cfg: dict) -> list[tuple[str, bool, str]]:
    s, tv = pine["settings"], cfg["costs"]["tradingview"]
    return [
        ("Pine Script version 6", pine["version"] == "6", f"//@version={pine['version']}"),
        ("next-bar-open fills (process_orders_on_close = false)", s.get("process_orders_on_close") == "false",
         f"process_orders_on_close = {s.get('process_orders_on_close')}; pipeline execution = {cfg['strategy']['execution']}"),
        ("commission per order matches config", s.get("commission_type") == "strategy.commission.cash_per_order"
         and float(s.get("commission_value", 0)) == float(tv["commission_per_order"]),
         f"{s.get('commission_type')} {s.get('commission_value')} vs config {tv['commission_per_order']}"),
        ("slippage set", int(s.get("slippage", 0)) > 0, f"slippage = {s.get('slippage')} ticks vs config {tv['slippage_bps']} bps"),
        ("100% of equity per trade", s.get("default_qty_value") == "100", f"default_qty_value = {s.get('default_qty_value')}"),
        ("no pyramiding (one position at a time)", s.get("pyramiding") == "0", f"pyramiding = {s.get('pyramiding')}"),
    ]


def run(symbol: str = "SPY", fast: int | None = None, slow: int | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    pine = parse_pine(PINE_FILE)
    fast = fast or pine["inputs"].get("fastLen", 50)
    slow = slow or pine["inputs"].get("slowLen", 200)
    out(f"\n[1] Pine strategy {PINE_FILE.name}: inputs {pine['inputs']}")
    out("[2] Settings reconciliation (Pine strategy() vs pipeline):")
    checks = settings_checks(pine, cfg)
    for name, ok, detail in checks:
        out(f"    {'PASS' if ok else 'FAIL'}  {name:<55} {detail}")

    bars = load_bars(symbol, cfg["data"]["start"], cfg["data"]["end"])
    costs = tradingview_cost_model(cfg)
    signal = cross_signal(ta_sma(bars["close"], fast), ta_sma(bars["close"], slow))
    res = backtest(bars, signal, initial_capital=100_000, costs=costs, execution="next_open")
    bh = buy_and_hold(bars, costs)
    m = res.metrics(benchmark=bh.returns)
    closed = res.trades[~res.trades["side"].str.contains("open")] if len(res.trades) else res.trades
    net = res.equity.iloc[-1] - res.initial_capital
    py = {"net_profit_usd": round(net, 0), "net_profit_pct": round(net / res.initial_capital * 100, 2),
          "closed_trades": int(len(closed)), "open_trades": int(len(res.trades) - len(closed)),
          "percent_profitable": round(M.win_rate(closed["net_return"]) * 100, 1) if len(closed) else None,
          "profit_factor": round(M.profit_factor(closed["net_return"]), 2) if len(closed) else None,
          "max_drawdown_pct": round(m["Max drawdown"] * 100, 2), "sharpe": round(m["Sharpe"], 2),
          "sortino": round(m["Sortino"], 2), "commission_paid_usd": round(res.cost_summary()["commission"], 2),
          "buy_hold_pct": round(M.total_return(bh.returns) * 100, 2)}
    py = {k: (v if v is None or isinstance(v, int) else float(v)) for k, v in py.items()}   # plain numbers for YAML
    out(f"\n[3] Pipeline backtest: {symbol} SMA {fast}/{slow}, {bars.index[0].date()} to {bars.index[-1].date()}, "
        f"next-bar-open fills, {costs.name}")
    tv = yaml.safe_load(TV_RESULTS.read_text()) if TV_RESULTS.exists() else {}
    labels = {"net_profit_usd": "Net profit (USD)", "net_profit_pct": "Net profit (%)", "closed_trades": "Closed trades",
              "open_trades": "Open trades", "percent_profitable": "Percent profitable", "profit_factor": "Profit factor",
              "max_drawdown_pct": "Max drawdown (%)", "sharpe": "Sharpe ratio", "sortino": "Sortino ratio",
              "commission_paid_usd": "Commission paid (USD)", "buy_hold_pct": "Buy & hold return (%)"}
    entered = {k: v for k, v in (tv or {}).items() if k in labels and v is not None}
    out(f"    {'Strategy Tester metric':<24}{'pipeline':>12}{'TradingView':>14}{'difference':>12}")
    for k, lab in labels.items():
        t = entered.get(k)
        diff = f"{float(t) - float(py[k]):+.2f}" if t is not None and py[k] is not None else ""
        out(f"    {lab:<24}{str(py[k]):>12}{(str(t) if t is not None else '-'):>14}{diff:>12}")
    if not entered:
        out(f"    -> copy the Performance Summary into {TV_RESULTS.relative_to(LAB_ROOT)} and re-run to reconcile")
    out("\n[4] Trade list (compare with the 'List of Trades' tab):")
    show = res.trades.copy()
    show["entry_date"], show["exit_date"] = show["entry_date"].dt.date, show["exit_date"].dt.date
    out("    " + show[["entry_date", "exit_date", "side", "entry_price", "exit_price", "net_return"]]
        .round(4).to_string(index=False).replace("\n", "\n    "))
    out("\n[5] If the numbers differ, check in this order:")
    for i, c in enumerate(CAUSES, 1):
        out(f"    {i}. {c}")
    ok = all(c[1] for c in checks)
    out(f"\nRESULT: settings {'reconciled' if ok else 'NOT reconciled'}; pipeline net profit USD {py['net_profit_usd']:,.0f} "
        f"({py['net_profit_pct']:+.2f}%) vs buy and hold {py['buy_hold_pct']:+.2f}%")
    path = output_path("Lab06_reconciliation.yaml")
    path.write_text(yaml.safe_dump({"pipeline": py, "tradingview": entered,
                                    "settings": [{"check": n, "pass": bool(o), "detail": d} for n, o, d in checks]},
                                   sort_keys=False))
    out(f"Reconciliation -> _outputs/{path.name}")
    plot_equity_and_drawdown({f"SMA {fast}/{slow} strategy": res.equity, "Buy & hold": bh.equity},
                             f"{symbol}: pipeline reconciliation of the Pine strategy", "Lab06_crosscheck.png")
    return {"settings_ok": ok, **py}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline reconcile", description="Stage 06 - Strategy Tester reconciliation")
    ap.add_argument("--symbol", default="SPY")
    ap.add_argument("--fast", type=int, default=None)
    ap.add_argument("--slow", type=int, default=None)
    a = ap.parse_args(argv)
    stage_banner(6, "reconcile TradingView Strategy Tester with the pipeline backtest")
    return 0 if run(a.symbol.upper(), a.fast, a.slow)["settings_ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
