"""
python -m pipeline <command> [options]      (run from the labs folder)

Global flags (any position): --offline  force bundled data + simulator
                             --config PATH  use another config.yaml
"""
from __future__ import annotations

if __package__ in (None, ""):                      # allow: python3 path/to/__main__.py
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import importlib
import sys

from pipeline.config import apply_cli_flags

# command -> (lab, module, function, description)
COMMANDS = {
    "check":      (1, "pipeline.check", "main", "config, secrets, paper broker, market clock, data"),
    "validate":   (2, "pipeline.validate", "main", "cross-check pipeline bars with TradingView (adjusted vs unadjusted)"),
    "ingest":     (3, "pipeline.ingest", "main", "fetch + cache multi-timeframe bars and headlines, data-quality report"),
    "hypothesis": (4, "pipeline.hypothesis", "main", "test a YAML hypothesis card statistically"),
    "indicators": (5, "pipeline.indicators", "main", "Python twins of the Pine Script indicators"),
    "reconcile":  (6, "pipeline.reconcile", "main", "reconcile the TradingView Strategy Tester with the pipeline backtest"),
    "signals":    (7, "pipeline.signals", "main", "signal library -> target positions (next-bar aligned)"),
    "execute":    (8, "pipeline.execution", "main", "order manager: target vs actual -> paper orders"),
    "evaluate":   (9, "pipeline.evaluate", "main", "metrics and benchmark table for every strategy"),
    "search":     (10, "pipeline.search", "main", "parameter grid search, in/out-of-sample decay"),
    "ml":         (11, "pipeline.ml", "main", "walk-forward ML classifier -> probability -> position"),
    "regime":     (12, "pipeline.regime", "main", "PCA + K-means regime gate on signals"),
    "abtest":     (13, "pipeline.abtest", "main", "A/B test two strategy variants"),
    "pairs":      (14, "pipeline.pairs", "main", "hedged pairs / statistical-arbitrage stage"),
    "backtest":   (15, "pipeline.backtest", "main", "backtest engine: cost scenarios and break-even"),
    "run":        (16, "pipeline.runner", "main", "automated forward test: --once | --loop [--live-paper]"),
    "schedule":   (16, "pipeline.runner", "schedule_main", "print cron / launchd / Task Scheduler entries"),
    "kill":       (16, "pipeline.risk", "kill_main", "kill switch: --on | --off | --status"),
    "webhook":    (17, "pipeline.webhook", "main", "TradingView webhook -> signal -> risk -> execution"),
    "alert-sim":  (17, "pipeline.webhook", "alert_sim_main", "send simulated TradingView alerts"),
    "diagnose":   (18, "pipeline.diagnose", "main", "automated bias checks"),
    "report":     (19, "pipeline.report", "main", "tearsheet + backtest-vs-forward report"),
    "agents":     (20, "pipeline.agents", "main", "analyst / trader / risk agents with human approval"),
    "e2e":        (20, "pipeline.e2e", "main", "run the whole pipeline end to end"),
}


def usage() -> None:
    print(__doc__)
    print(f"{'Lab':<4} {'command':<11} what it does")
    for cmd, (lab, _, _, desc) in COMMANDS.items():
        print(f"{lab:<4} {cmd:<11} {desc}")


def main(argv: list[str] | None = None) -> int:
    argv = apply_cli_flags(list(sys.argv[1:] if argv is None else argv))
    if not argv or argv[0] in ("-h", "--help", "list", "help"):
        usage()
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd not in COMMANDS:
        print(f"unknown command '{cmd}'")
        usage()
        return 2
    _, module, func, _ = COMMANDS[cmd]
    code = getattr(importlib.import_module(module), func)(rest)
    return int(code or 0)


if __name__ == "__main__":
    sys.exit(main())
