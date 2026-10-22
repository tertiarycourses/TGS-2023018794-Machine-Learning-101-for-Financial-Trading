"""
pipeline/backtest.py - Stage 15: the backtest engine with cost models and break-even.

Wraps common.backtest (next-bar execution, per-trade costs) for the pipeline:
  * any library signal x any cost scenario from config.yaml (or a custom one)
  * gross vs net CAGR, cost drag, Sharpe, and the cost breakdown in dollars
    (commission, half-spread, slippage, SEC/FINRA-style fees on sells)
  * break-even one-way cost: the bps at which net CAGR reaches 0
  * execution-timing sensitivity: next-bar OPEN vs next-bar CLOSE fills

    python -m pipeline backtest --strategies dip_buy trend_filter
    python -m pipeline backtest --custom spread_bps=3 slippage_bps=3
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys

import pandas as pd

from common import metrics as M
from common.backtest import COST_PRESETS, CostModel, backtest
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import load_config, stage_banner
from pipeline.ingest import load_bars
from pipeline.signals import SIGNALS, target_position


def run_backtest(bars, name: str, costs: CostModel | None = None, execution: str = "next_open", **params):
    """One backtest of a library signal - the single entry point later stages use."""
    return backtest(bars, target_position(name, bars, **params), costs=costs, execution=execution)


def break_even_bps(bars, signal, lo: float = 0.0, hi: float = 1000.0) -> float:
    """Bisection on a one-way cost (as slippage bps) until net CAGR = 0."""
    if M.cagr(backtest(bars, signal).returns) <= 0:
        return 0.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if M.cagr(backtest(bars, signal, costs=CostModel(slippage_bps=mid)).returns) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def parse_custom(items: list[str] | None) -> CostModel | None:
    if not items:
        return None
    kw = {k: float(v) for k, _, v in (i.partition("=") for i in items)}
    return CostModel("Custom route", **kw)


def run(strategies: list[str] | None = None, symbol: str = "SPY", custom: CostModel | None = None,
        quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    bars = load_bars(symbol, cfg["data"]["start"], cfg["data"]["end"])
    strategies = strategies or ["dip_buy", "trend_filter"]
    scenarios = [COST_PRESETS[k] for k in cfg["costs"]["scenarios"]] + ([custom] if custom else [])
    rows, curves, breakdown = [], {}, {}
    for name in strategies:
        sig = target_position(name, bars)
        for cm in scenarios:
            res = backtest(bars, sig, costs=cm)
            cs, m = res.cost_summary(), res.metrics()
            rows.append({"strategy": name, "cost scenario": cm.name, "gross CAGR": cs["gross_cagr"],
                         "net CAGR": cs["net_cagr"], "cost drag": cs["cost_drag_cagr"], "net Sharpe": m["Sharpe"],
                         "executions": cs["n_trades"], "commission $": cs["commission"], "spread $": cs["spread"],
                         "slippage $": cs["slippage"], "reg fees $": cs["reg_fees"], "total cost $": cs["total"]})
            if name == strategies[0]:
                curves[cm.name] = res.equity
                breakdown[cm.name] = {k: cs[k] for k in ["commission", "spread", "slippage", "reg_fees"]}
        if name == strategies[0]:
            curves["Gross (no costs)"] = backtest(bars, sig).equity_gross
    df = pd.DataFrame(rows)
    show = df.copy()
    for c in ["gross CAGR", "net CAGR", "cost drag"]:
        show[c] = (show[c].round(6) + 0.0).map("{:.2%}".format)
    for c in ["commission $", "spread $", "slippage $", "reg fees $", "total cost $"]:
        show[c] = show[c].map("{:,.0f}".format)
    show["net Sharpe"] = show["net Sharpe"].round(2)
    pd.set_option("display.width", 200)
    out(f"\n{symbol} {bars.index[0].date()} to {bars.index[-1].date()}, USD 100,000 start, next-bar-open fills:")
    out(show.to_string(index=False))

    out("\nBreak-even one-way cost (net CAGR = 0) vs the average gross trade:")
    be = {}
    for name in strategies:
        sig = target_position(name, bars)
        trades = backtest(bars, sig).trades
        be[name] = break_even_bps(bars, sig)
        out(f"  {name:<18} {be[name]:6.1f} bps per side | {len(trades)} round trips, average gross trade "
            f"{trades['gross_return'].mean() * 1e4:5.1f} bps")
    out("  -> a strategy whose average trade is only a few times its round-trip cost is fragile")

    out("\nExecution-timing sensitivity (Alpaca-style costs):")
    for name in strategies:
        sig = target_position(name, bars)
        o = backtest(bars, sig, costs=COST_PRESETS["alpaca_retail"], execution="next_open").metrics()
        c = backtest(bars, sig, costs=COST_PRESETS["alpaca_retail"], execution="next_close").metrics()
        out(f"  {name:<18} next-bar OPEN CAGR {o['CAGR']:6.2%} Sharpe {o['Sharpe']:.2f} | next-bar CLOSE CAGR "
            f"{c['CAGR']:6.2%} Sharpe {c['Sharpe']:.2f}")

    csv = output_path("Lab15_cost_scenarios.csv")
    df.round(6).to_csv(csv, index=False)
    out(f"Cost scenarios -> _outputs/{csv.name}")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1.6, 1]})
    for name, eq in curves.items():
        ax1.plot(eq.index, eq / 1e3, label=name, lw=1.5 if "Gross" in name else 1.1, ls="--" if "Gross" in name else "-")
    ax1.set_title(f"{strategies[0]}: equity by cost scenario (USD '000)")
    ax1.legend()
    pd.DataFrame(breakdown).T.plot.barh(stacked=True, ax=ax2)
    ax2.set_title("Where the costs go (USD)")
    save(fig, "Lab15_costs.png")
    return {"rows": df.round(6).to_dict("records"), "break_even_bps": {k: round(v, 1) for k, v in be.items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline backtest", description="Stage 15 - backtest engine")
    ap.add_argument("--strategies", nargs="+", default=None, choices=list(SIGNALS))
    ap.add_argument("--symbol", default="SPY")
    ap.add_argument("--custom", nargs="+", default=None,
                    help="extra cost scenario, e.g. spread_bps=3 slippage_bps=3 commission_per_share=0.005")
    a = ap.parse_args(argv)
    stage_banner(15, "backtest engine: cost scenarios and break-even")
    run(a.strategies, a.symbol.upper(), parse_custom(a.custom))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
