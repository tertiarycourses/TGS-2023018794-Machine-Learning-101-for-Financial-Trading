"""
Lab 14 - Pairs trading: hedged statistical arbitrage (A4, K6)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/pairs.py. Identical to:
    python -m pipeline pairs
Run from the labs folder:
    python3 Lab14-pairs-trading/pairs_stage.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.pairs import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
