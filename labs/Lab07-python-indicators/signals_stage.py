"""
Lab 07 - Signal library -> target positions (A2, K3, K7)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/signals.py. Identical to:
    python -m pipeline signals --symbol SPY
Run from the labs folder:
    python3 Lab07-python-indicators/signals_stage.py --symbol SPY
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.signals import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
