"""
Lab 11 - ML signal: walk-forward classifier -> position (A4, K4, K6)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/ml.py. Identical to:
    python -m pipeline ml --threshold 0.55
Run from the labs folder:
    python3 Lab11-ml-signal-classifier/ml_stage.py --threshold 0.55
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.ml import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
