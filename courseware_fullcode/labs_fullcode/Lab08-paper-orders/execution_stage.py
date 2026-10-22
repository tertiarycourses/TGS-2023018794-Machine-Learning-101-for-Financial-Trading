"""
Lab 08 - Execution: order manager, target vs actual -> paper orders (A3, K5)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/execution.py. Identical to:
    python -m pipeline execute --reset
Run from the labs folder:
    python3 Lab08-paper-orders/execution_stage.py --reset
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.execution import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
