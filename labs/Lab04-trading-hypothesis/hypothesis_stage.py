"""
Lab 04 - Hypothesis card -> automated statistical test (A1, A6, K1)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/hypothesis.py. Identical to:
    python -m pipeline hypothesis
Run from the labs folder:
    python3 Lab04-trading-hypothesis/hypothesis_stage.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.hypothesis import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
