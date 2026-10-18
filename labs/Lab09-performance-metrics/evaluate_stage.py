"""
Lab 09 - Evaluation: metrics and benchmark table (A3, K3)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/evaluate.py. Identical to:
    python -m pipeline evaluate --symbol SPY
Run from the labs folder:
    python3 Lab09-performance-metrics/evaluate_stage.py --symbol SPY
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.evaluate import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
