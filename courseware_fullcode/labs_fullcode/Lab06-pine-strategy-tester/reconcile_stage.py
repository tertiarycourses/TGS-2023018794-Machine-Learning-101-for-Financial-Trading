"""
Lab 06 - Reconcile the TradingView Strategy Tester with the pipeline (A2, A3, K3, K7)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/reconcile.py. Identical to:
    python -m pipeline reconcile --symbol SPY --fast 50 --slow 200
Run from the labs folder:
    python3 Lab06-pine-strategy-tester/reconcile_stage.py --symbol SPY --fast 50 --slow 200
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.reconcile import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
