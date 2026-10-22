"""
Lab 20 - Capstone: the whole pipeline end to end (A7, A10, K1)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/e2e.py. Identical to:
    python -m pipeline e2e --execute
Run from the labs folder:
    python3 Lab20-agentic-capstone/e2e_stage.py --execute
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.e2e import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
