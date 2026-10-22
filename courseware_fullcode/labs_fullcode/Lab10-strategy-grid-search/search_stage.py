"""
Lab 10 - Strategy search: grid, in/out-of-sample decay (A2, A4, K2)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/search.py. Identical to:
    python -m pipeline search --symbol SPY
Run from the labs folder:
    python3 Lab10-strategy-grid-search/search_stage.py --symbol SPY
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.search import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
