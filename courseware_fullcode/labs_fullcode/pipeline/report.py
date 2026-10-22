"""
pipeline/report.py - Stage 19: monitoring and reporting.

Builds the investment-committee pack for the configured strategy automatically:
  * research backtest 2018-2025 vs buy and hold (net of costs) and the cost breakdown
  * backtest vs FORWARD test (the runner's paper logs, Lab 16): return, Sharpe,
    drawdown, orders, fill slippage vs the model's open price, tracking difference
  * monitoring checks with thresholds (tracking, slippage, drawdown stop rule,
    kill switch, diagnostics verdict) -> OK / ALERT
  * one-page tearsheet PNG and a markdown report with insights and a recommendation

    python -m pipeline report
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys
from datetime import date

import numpy as np
import pandas as pd

from common import metrics as M
from common.backtest import backtest
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.ingest import load_bars
from pipeline.risk import RiskManager
from pipeline.runner import EQUITY_LOG, TRADE_LOG, replay
from pipeline.signals import target_position

FWD_START, FWD_END = "2025-01-02", "2025-12-31"
THRESHOLDS = {"tracking_abs": 0.02, "slippage_bps": 5.0, "drawdown_stop": 0.15}


def load_forward_test(cfg) -> tuple[pd.Series, pd.DataFrame]:
    if not EQUITY_LOG.exists() or not TRADE_LOG.exists():
        print("Forward-test logs not found - running the Lab 16 replay first ...")
        replay(cfg, FWD_START, FWD_END, quiet=True)
    eq = pd.read_csv(EQUITY_LOG, parse_dates=["date"], index_col="date")["equity"]
    trades = pd.read_csv(TRADE_LOG)
    in_window = pd.to_datetime(trades["run_time"].str[:10], errors="coerce").between(FWD_START, FWD_END)
    return eq, trades[trades["action"].isin(["BUY", "SELL"]) & in_window]


def run(quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    s = cfg["strategy"]
    sym = s["symbol"]
    label = f"{s['name']} {'/'.join(str(v) for v in s['params'].values())}"
    bars = load_bars(sym, cfg["data"]["start"], FWD_END)
    costs = cost_model(cfg)
    signal = target_position(s["name"], bars, **s["params"])
    full = backtest(bars, signal, costs=costs)
    bench = bars["close"].pct_change().fillna(0)
    bt25 = backtest(bars.loc["2024-12-31":FWD_END], signal, costs=costs)
    bt_ret = bt25.returns.loc[FWD_START:]
    fwd_eq, fills = load_forward_test(cfg)
    fwd_ret = fwd_eq.pct_change().fillna(fwd_eq.iloc[0] / 100_000 - 1)

    keys = ["Total return", "CAGR", "Ann. volatility", "Sharpe", "Sortino", "Max drawdown", "Calmar", "Win rate",
            "Profit factor", "Trades", "Exposure", "Alpha", "Beta"]
    m_full = M.format_table({f"{label} (net)": full.metrics(benchmark=bench),
                             f"{sym} buy & hold": M.summary(bench, benchmark=bench)}).loc[keys]
    cs = full.cost_summary()
    fills = fills.assign(fill_date=pd.to_datetime(fills["run_time"].str[:10]))
    fills["model_open"] = fills["fill_date"].map(bars["open"])
    sign = np.where(fills["action"] == "BUY", 1, -1)
    fills["slippage_bps"] = sign * (fills["fill_price"].astype(float) / fills["model_open"] - 1) * 1e4
    tracking = M.total_return(fwd_ret) - M.total_return(bt_ret)
    te = (fwd_ret - bt_ret.reindex(fwd_ret.index).fillna(0)).std() * np.sqrt(252)
    comp = pd.DataFrame({
        "Backtest 2025": [f"{M.total_return(bt_ret):.2%}", f"{M.sharpe_ratio(bt_ret):.2f}", f"{M.max_drawdown(bt_ret):.2%}",
                          int((bt25.costs["traded_notional"] > 0).sum()), "model open + costs"],
        "Forward test 2025 (paper)": [f"{fwd_eq.iloc[-1] / 100_000 - 1:.2%}", f"{M.sharpe_ratio(fwd_ret):.2f}",
                                      f"{M.max_drawdown(fwd_ret):.2%}", len(fills),
                                      f"avg slippage {fills['slippage_bps'].mean():.1f} bps"]},
        index=["Total return", "Sharpe", "Max drawdown", "Orders", "Execution"])
    out(f"\n[1] Research backtest 2018-2025, {label} on {sym}, net of {costs.name} costs:")
    out("  " + m_full.to_string().replace("\n", "\n  "))
    out(f"  Costs: total USD {cs['total']:,.0f} (spread {cs['spread']:,.0f}, slippage {cs['slippage']:,.0f}, "
        f"reg fees {cs['reg_fees']:,.0f}); cost drag {cs['cost_drag_cagr']:.2%} a year")
    out("\n[2] Backtest vs forward (paper) test, 2025:")
    out("  " + comp.to_string().replace("\n", "\n  "))
    out(f"  Tracking difference (forward - backtest) {tracking:+.2%}; tracking error {te:.2%} annualised")

    current_dd = float(fwd_eq.iloc[-1] / fwd_eq.cummax().iloc[-1] - 1)
    diag = output_path("Lab18_diagnostics.csv")
    diag_verdict = "not run"
    if diag.exists():
        d = pd.read_csv(diag)
        mine = d[d["subject"] == s["name"]]
        diag_verdict = ("not run" if mine.empty else "FAIL items" if (mine["status"] == "FAIL").any()
                        else f"{int((mine['status'] == 'WARN').sum())} WARN, no FAIL")
    checks = [
        ("tracking vs backtest", abs(tracking) <= THRESHOLDS["tracking_abs"], f"{tracking:+.2%} (limit +/-{THRESHOLDS['tracking_abs']:.0%})"),
        ("average fill slippage", fills["slippage_bps"].mean() <= THRESHOLDS["slippage_bps"],
         f"{fills['slippage_bps'].mean():.1f} bps (limit {THRESHOLDS['slippage_bps']:.0f} bps)"),
        ("drawdown stop rule", -current_dd < THRESHOLDS["drawdown_stop"],
         f"current {current_dd:.2%}, worst {M.max_drawdown(fwd_ret):.2%} (stop at -{THRESHOLDS['drawdown_stop']:.0%})"),
        ("kill switch", not RiskManager(cfg).kill_switch_on(), "off" if not RiskManager(cfg).kill_switch_on() else "ON"),
        ("diagnostics (Lab 18)", diag_verdict not in ("FAIL items", "not run"),
         diag_verdict if diag_verdict != "not run" else f"not run for {s['name']} - python -m pipeline diagnose"),
    ]
    mon = pd.DataFrame([{"check": c, "status": "OK" if ok else "ALERT", "value": v} for c, ok, v in checks])
    out("\n[3] Monitoring checks:")
    out("  " + mon.to_string(index=False).replace("\n", "\n  "))
    mon.to_csv(output_path("Lab19_monitoring.csv"), index=False)

    fig, ax = plt.subplots(3, 2, figsize=(13, 11))
    (full.equity / 1e5).plot(ax=ax[0, 0], label="Strategy (net)")
    M.equity_curve(bench).plot(ax=ax[0, 0], label=f"{sym} buy & hold", alpha=0.8)
    ax[0, 0].axvspan(pd.Timestamp(FWD_START), pd.Timestamp(FWD_END), color="orange", alpha=0.1, label="Forward-test year")
    ax[0, 0].set_title("Equity, growth of $1")
    ax[0, 0].legend()
    (M.drawdown_series(full.returns) * 100).plot(ax=ax[0, 1], color="#c0504d")
    (M.drawdown_series(bench) * 100).plot(ax=ax[0, 1], color="gray", alpha=0.6)
    ax[0, 1].set_title(f"Drawdown % (red = strategy, grey = {sym})")
    monthly = (1 + full.returns).resample("ME").prod() - 1
    heat = monthly.groupby([monthly.index.year, monthly.index.month]).first().unstack() * 100
    im = ax[1, 0].imshow(heat.values, cmap="RdYlGn", vmin=-8, vmax=8, aspect="auto")
    ax[1, 0].set_xticks(range(12), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax[1, 0].set_yticks(range(len(heat.index)), heat.index)
    for (i, j), v in np.ndenumerate(heat.values):
        if not np.isnan(v):
            ax[1, 0].text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7)
    ax[1, 0].set_title("Monthly returns % (strategy, net)")
    ax[1, 0].grid(False)
    fig.colorbar(im, ax=ax[1, 0], shrink=0.8)
    roll = full.returns.rolling(126).apply(lambda r: r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan)
    roll.plot(ax=ax[1, 1], color="#1f4e79")
    ax[1, 1].axhline(0, color="black", lw=0.7)
    ax[1, 1].set_title("Rolling 6-month Sharpe ratio")
    (bt25.equity.loc[FWD_START:] / 1e5).plot(ax=ax[2, 0], label="Backtest 2025")
    (fwd_eq / 1e5).plot(ax=ax[2, 0], label="Forward test 2025 (paper)", ls="--")
    ax[2, 0].set_title("Backtest vs forward test, 2025")
    ax[2, 0].legend()
    pd.Series({k: cs[k] for k in ["commission", "spread", "slippage", "reg_fees"]}).plot.bar(ax=ax[2, 1], color="#e2a400")
    ax[2, 1].set_title("Trading costs 2018-2025 (USD)")
    fig.suptitle(f"Lion City Capital (fictitious) - {label} on {sym}: tearsheet", fontsize=13)
    save(fig, "Lab19_tearsheet.png")

    m = full.metrics(benchmark=bench)
    insights = [
        f"Over 2018-2025 the strategy returned {m['CAGR']:.1%} a year versus {M.cagr(bench):.1%} for {sym}, with a maximum "
        f"drawdown of {m['Max drawdown']:.1%} versus {M.max_drawdown(bench):.1%} - it trades return for lower risk.",
        f"Beta to {sym} is {m['Beta']:.2f} with {m['Exposure']:.0%} exposure; the CAPM alpha of {m['Alpha']:+.1%} a year is an "
        "untested point estimate, not proof of skill.",
        f"Costs were small for this low-turnover rule (drag {cs['cost_drag_cagr']:.2%} a year) - turnover, not commission, drives cost.",
        f"The 2025 paper forward test tracked the backtest within {abs(tracking):.2%} of total return; differences come from "
        "whole-share sizing, the position cap and fill slippage.",
        f"Monitoring: {int((mon.status == 'OK').sum())} of {len(mon)} checks OK; diagnostics: {diag_verdict}.",
    ]
    alerts = mon[mon.status == "ALERT"]
    rec = ("CONTINUE PAPER TRADING for at least another quarter. The forward test confirms the implementation matches the "
           "research, but the strategy has not beaten buy and hold on return. Before any live allocation: add a second "
           "uncorrelated signal, keep the drawdown stop rule, and obtain risk-committee sign-off. Paper results only - not "
           "investment advice.") if alerts.empty else (
           f"PAUSE AND INVESTIGATE: monitoring alerts on {', '.join(alerts.check)}. Halt with the kill switch until resolved.")
    md = [f"# Lion City Capital (fictitious) - Strategy Performance Report",
          f"*{label} on {sym} | prepared {date.today()} | for training only*", "",
          "## 1. Research backtest 2018-2025 (net of costs)", m_full.to_markdown(), "",
          "## 2. Trading costs 2018-2025",
          pd.DataFrame({"USD": {k: f"{cs[k]:,.0f}" for k in ["commission", "spread", "slippage", "reg_fees", "total"]}}).to_markdown(),
          "", "## 3. Backtest vs forward (paper) test, 2025", comp.to_markdown(), "",
          "## 4. Monitoring checks", mon.to_markdown(index=False), "",
          "## 5. Key insights", *[f"- {x}" for x in insights], "",
          "## 6. Recommendation to the investment committee", rec, "", "![Tearsheet](Lab19_tearsheet.png)"]
    path = output_path("Lab19_report.md")
    path.write_text("\n".join(md), encoding="utf-8")
    out("\n[4] Key insights:")
    for x in insights:
        out(f"  - {x}")
    out(f"\nRecommendation: {rec}")
    out(f"Report -> _outputs/{path.name} | tearsheet -> _outputs/Lab19_tearsheet.png | monitoring -> _outputs/Lab19_monitoring.csv")
    return {"cagr": m["CAGR"], "sharpe": m["Sharpe"], "fwd_return": float(fwd_eq.iloc[-1] / 100_000 - 1),
            "bt_return": float(M.total_return(bt_ret)), "tracking": float(tracking),
            "monitoring_ok": int((mon.status == "OK").sum()), "recommendation": rec.split(".")[0]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline report", description="Stage 19 - monitoring and reporting")
    ap.parse_args(argv)
    stage_banner(19, "monitoring and reporting: tearsheet + backtest vs forward test")
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
