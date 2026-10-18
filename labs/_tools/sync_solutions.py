"""
_tools/sync_solutions.py - maintainer tool: copy each finished pipeline stage module into
the matching LabNN-*/solution/ folder (the reference solution learners can compare with or
restore from), or check that the copies are identical.

    python3 _tools/sync_solutions.py          # copy (overwrites only files inside solution/)
    python3 _tools/sync_solutions.py --check  # report differences, exit 1 if any
"""
import filecmp
import shutil
import sys
from pathlib import Path

LAB_SRC = Path(__file__).resolve().parents[1]
PIPE = LAB_SRC / "pipeline"
SOLUTIONS = {
    "Lab01-alpaca-setup": ["config.yaml", "config.py", "clock.py", "check.py", "__main__.py"],
    "Lab02-tradingview-charts": ["validate.py"],
    "Lab03-alpaca-market-data": ["ingest.py"],
    "Lab04-trading-hypothesis": ["hypothesis.py", "hypotheses/spy_dip_after_streak.yaml"],
    "Lab05-pine-indicators": ["indicators.py"],
    "Lab06-pine-strategy-tester": ["reconcile.py"],
    "Lab07-python-indicators": ["signals.py"],
    "Lab08-paper-orders": ["execution.py"],
    "Lab09-performance-metrics": ["evaluate.py"],
    "Lab10-strategy-grid-search": ["search.py"],
    "Lab11-ml-signal-classifier": ["ml.py"],
    "Lab12-market-regimes": ["regime.py"],
    "Lab13-ab-testing": ["abtest.py"],
    "Lab14-pairs-trading": ["pairs.py"],
    "Lab15-trading-costs": ["backtest.py"],
    "Lab16-paper-trading-bot": ["runner.py", "risk.py"],
    "Lab17-tradingview-webhook": ["webhook.py"],
    "Lab18-diagnose-bias": ["diagnose.py"],
    "Lab19-performance-report": ["report.py"],
    "Lab20-agentic-capstone": ["agents.py", "e2e.py"],
}

if __name__ == "__main__":
    check, diffs = "--check" in sys.argv, 0
    for lab, files in SOLUTIONS.items():
        dest = LAB_SRC / lab / "solution"
        dest.mkdir(exist_ok=True)
        for rel in files:
            src, dst = PIPE / rel, dest / Path(rel).name
            same = dst.exists() and filecmp.cmp(src, dst, shallow=False)
            if check:
                if not same:
                    diffs += 1
                    print(f"DIFFERS {lab}/solution/{dst.name}")
            elif not same:
                shutil.copy2(src, dst)
                print(f"copied pipeline/{rel} -> {lab}/solution/{dst.name}")
    print(f"{'check' if check else 'sync'} done, {diffs} differences" if check else "sync done")
    sys.exit(1 if diffs else 0)
