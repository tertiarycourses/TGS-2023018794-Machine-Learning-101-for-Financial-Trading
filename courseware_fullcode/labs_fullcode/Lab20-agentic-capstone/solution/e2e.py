"""
pipeline/e2e.py - Stage 20: one command runs the whole pipeline end to end.

  check -> validate -> ingest -> hypothesis -> indicators -> reconcile -> signals
  -> evaluate -> search -> ml -> regime -> abtest -> pairs -> backtest
  -> run (forward test) -> webhook self-test -> diagnose -> report -> agents -> [human approval] -> paper orders

Gates (the pipeline stops sending orders, but keeps reporting, when a gate fails):
  check not ready | ingest quality FAIL | diagnose BLOCK | report monitoring ALERT | kill switch ON
Every stage's full output goes to _outputs/Lab20_e2e_log.txt; the console shows one line per stage.

    python -m pipeline e2e                    # research + forward test + agents propose-only
    python -m pipeline e2e --execute          # ... then ask a human to approve paper orders
    python -m pipeline e2e --execute --yes    # scripted approval (classroom demo only)
    python -m pipeline e2e --fast             # skip the slower research stages (search, ml, pairs)
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import contextlib
import json
import sys
import time
import traceback
from datetime import datetime

from common.config import is_online, mode_label, output_path
from common.plotting import plt, save
from pipeline.config import load_config, stage_banner


def stages(cfg, fast: bool):
    from pipeline import (abtest, agents, backtest, check, diagnose, evaluate, execution, hypothesis, indicators,
                          ingest, ml, pairs, reconcile, regime, report, runner, search, signals, validate, webhook)
    s = cfg["strategy"]
    shared = {}

    def signals_stage():
        shared["signals"] = r = signals.run()
        return r

    def execution_stage():
        longs = [t["symbol"] for t in shared.get("signals", {}).get("targets", []) if t["target"] == 1]
        w = min(cfg["risk"]["max_position_pct"] / max(len(longs), 1), 0.20)
        return execution.run({sym: w for sym in longs} or None, session=None if is_online() else "regular", reset=True)
    plan = [
        (1, "check", lambda: check.run(reset=True),
         lambda r: (r["ready"], f"{r['mode']}, equity USD {r['equity']:,.0f}, session {r['session']}")),
        (2, "validate", lambda: validate.run(),
         lambda r: (True, f"{r['passed']}/{len(r['rows'])} watch-list symbols match TradingView")),
        (3, "ingest", lambda: ingest.run(),
         lambda r: (r["failed"] == 0, f"{r['files']} files cached, {r['failed']} quality FAIL, {r['headlines']} headlines")),
        (4, "hypothesis", lambda: hypothesis.run(),
         lambda r: (True, f"{r['signal_days']} signal days, t {r['welch_t']:.2f}, p {r['p_value']:.3f} -> "
                          f"{r['decision'].split(' - ')[0]}")),
        (5, "indicators", lambda: indicators.run(),
         lambda r: (True, f"{r['bull']} bull / {r['bear']} bear EMA crosses since 2024-06")),
        (6, "reconcile", lambda: reconcile.run(),
         lambda r: (r["settings_ok"], f"Pine settings reconciled; net profit USD {r['net_profit_usd']:,.0f}")),
        (7, "signals", signals_stage,
         lambda r: (r["lookahead_fail"] == 0, f"{sum(t['target'] for t in r['targets'])}/{len(r['targets'])} "
                                              f"universe targets long, look-ahead tests pass")),
        (8, "execute", execution_stage,
         lambda r: (True, f"equal-weight targets -> {len(r['orders'])} paper orders ({r['filled']} filled, "
                          f"{r['queued']} queued), idempotent re-run sent 0, session {r['session']}")),
        (9, "evaluate", lambda: evaluate.run(), lambda r: (True, f"best Sharpe: {r['best']}")),
        (10, "search", lambda: search.run(),
         lambda r: (True, f"{r['n_sets']} sets, IS/OOS rank corr {r['rank_corr']:.2f}, top-5 decay {r['top5_decay']:+.2f}")),
        (11, "ml", lambda: ml.run(), lambda r: (True, f"AUC {r['auc']} -> {r['verdict'].split(' - ')[0]}")),
        (12, "regime", lambda: regime.run(), lambda r: (True, f"PC1 {r['pc1']:.1%}, latest regime {r['latest_regime']}")),
        (13, "abtest", lambda: abtest.run(), lambda r: (True, r["decision"].split(" - ")[0])),
        (14, "pairs", lambda: pairs.run(),
         lambda r: (True, f"KO/PEP beta {r['beta']:.3f}, net {r['net_return']:+.1%}, beta to SPY {r['beta_spy']:+.2f}")),
        (15, "backtest", lambda: backtest.run(), lambda r: (True, f"break-even bps {r['break_even_bps']}")),
        (16, "run", lambda: runner.replay(cfg, "2025-01-02", "2025-12-31"),
         lambda r: (True, f"forward test {r['sessions']} sessions, {r['orders']} orders, {r['return']:+.2%} vs "
                          f"buy & hold {r['bh']:+.2%}")),
        (17, "webhook", lambda: webhook.selftest(cfg),
         lambda r: (r["passed"] == r["total"], f"{r['passed']}/{r['total']} simulated alerts handled as expected")),
        (18, "diagnose", lambda: diagnose.run(), lambda r: (not r["verdict"].startswith("BLOCK"), r["verdict"].split(" - ")[0])),
        (19, "report", lambda: report.run(),
         lambda r: (r["monitoring_ok"] == 5, f"forward {r['fwd_return']:+.2%} vs backtest {r['bt_return']:+.2%}, "
                                              f"{r['monitoring_ok']}/5 monitoring OK")),
    ]
    if fast:
        plan = [p for p in plan if p[1] not in ("search", "ml", "pairs")]
    return plan, agents, s


def run(execute_orders: bool = False, yes: bool = False, fast: bool = False) -> dict:
    cfg = load_config()
    from pipeline.risk import RiskManager
    plan, agents, s = stages(cfg, fast)
    log_path = output_path("Lab20_e2e_log.txt")
    results, gates_ok, t0 = [], True, time.time()
    print(f"End-to-end run: strategy {s['name']} {s['params']} on {s['symbol']} | {mode_label()} | log -> _outputs/{log_path.name}\n")
    print(f"{'Lab':<4}{'stage':<12}{'status':<8}{'secs':>6}  result")
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Lion City Capital (fictitious) - pipeline e2e run {datetime.now().isoformat(timespec='seconds')}\n")
        for lab, name, fn, summarise in plan:
            t = time.time()
            log.write(f"\n{'=' * 30} stage {lab:02d} {name} {'=' * 30}\n")
            try:
                with contextlib.redirect_stdout(log):
                    res = fn()
                ok, msg = summarise(res)
                status = "OK" if ok else "GATE"
            except Exception as exc:
                log.write(traceback.format_exc())
                ok, msg, status = False, f"{type(exc).__name__}: {exc}"[:110], "ERROR"
            if name in ("check", "ingest", "diagnose", "report") and not ok:
                gates_ok = False
            results.append({"lab": lab, "stage": name, "status": status, "seconds": round(time.time() - t, 1), "result": msg})
            print(f"{lab:<4}{name:<12}{status:<8}{time.time() - t:>6.1f}  {msg}")
        if RiskManager(cfg).kill_switch_on():
            gates_ok = False
        log.write(f"\n{'=' * 30} stage 20 agents {'=' * 30}\n")
        t = time.time()
        allow = execute_orders and gates_ok
        if execute_orders and not gates_ok:
            print("     gates failed (see GATE / ERROR above or the kill switch): agents run in propose-only mode")
        with contextlib.redirect_stdout(log):
            ag = agents.run(execute_orders=allow and yes, yes=yes, reset=True)
        if allow and not yes:                              # ask the human on the real console, not the log file
            approved = ", ".join(ag["approved"]) or "none"
            print(f"     agents approved: {approved}")
            try:
                answer = input("     Human oversight - type YES to send these PAPER orders: ").strip() if ag["approved"] else ""
            except EOFError:
                answer = ""
            if answer == "YES":
                with contextlib.redirect_stdout(log):
                    ag = agents.run(execute_orders=True, yes=True, reset=True)
            else:
                ag["approval"] = "declined"
        msg = (f"{ag['brain']}; {', '.join(f'{k} {v}' for k, v in ag['decisions'].items())}; approval {ag['approval']}, "
               f"{ag['orders']} paper orders")
        results.append({"lab": 20, "stage": "agents", "status": "OK", "seconds": round(time.time() - t, 1), "result": msg})
        print(f"{20:<4}{'agents':<12}{'OK':<8}{time.time() - t:>6.1f}  {msg}")

    errors = sum(r["status"] == "ERROR" for r in results)
    summary = {"run_time": datetime.now().isoformat(timespec="seconds"), "mode": "online" if is_online() else "offline",
               "strategy": s, "gates_ok": gates_ok, "errors": errors, "seconds": round(time.time() - t0, 1),
               "stages": results}
    path = output_path("Lab20_e2e_summary.json")
    path.write_text(json.dumps(summary, indent=2, default=str))
    draw(results)
    print(f"\nRESULT: {len(results)} stages in {summary['seconds']:.0f} s, {errors} errors, gates "
          f"{'passed' if gates_ok else 'FAILED (no orders)'} | summary -> _outputs/{path.name}")
    return summary


def draw(results: list[dict]) -> None:
    colours = {"OK": "#d9ead3", "GATE": "#fff2cc", "ERROR": "#f4cccc"}
    n = len(results)
    cols = 5
    rows = (n + cols - 1) // cols
    fig, ax = plt.subplots(figsize=(14, 1.6 * rows + 0.8))
    ax.axis("off")
    for i, r in enumerate(results):
        x, y = i % cols, rows - i // cols
        ax.text(x * 2.8, y, f"Lab {r['lab']:02d}\n{r['stage']}\n{r['status']} ({r['seconds']}s)", ha="center", va="center",
                fontsize=9, bbox=dict(boxstyle="round,pad=0.5", fc=colours.get(r["status"], "#dde7f3"), ec="#1f4e79"))
        if i < n - 1 and x < cols - 1:
            ax.annotate("", xy=(x * 2.8 + 1.85, y), xytext=(x * 2.8 + 0.95, y), arrowprops=dict(arrowstyle="->", color="#1f4e79"))
    ax.set_xlim(-1.2, (cols - 1) * 2.8 + 1.2)
    ax.set_ylim(0.3, rows + 0.7)
    ax.set_title("Lion City Capital (fictitious) - end-to-end algorithmic trading pipeline (paper only)")
    save(fig, "Lab20_e2e_pipeline.png")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline e2e", description="Stage 20 - end-to-end run")
    ap.add_argument("--execute", action="store_true", help="let the agents send approved PAPER orders (human YES)")
    ap.add_argument("--yes", action="store_true", help="pre-approve (scripted classroom demo only)")
    ap.add_argument("--fast", action="store_true", help="skip search, ml and pairs")
    a = ap.parse_args(argv)
    stage_banner(20, "end-to-end pipeline run")
    return 1 if run(a.execute, a.yes, a.fast)["errors"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
