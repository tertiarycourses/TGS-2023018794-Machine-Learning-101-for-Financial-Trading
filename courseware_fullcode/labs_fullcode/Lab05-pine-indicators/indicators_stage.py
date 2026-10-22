"""
Lab 05 - Indicators: Python twins of the Pine Script indicators (A3, K3, K7)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/indicators.py. Identical to:
    python -m pipeline indicators --symbol AAPL
Run from the labs folder:
    python3 Lab05-pine-indicators/indicators_stage.py --symbol AAPL
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.indicators import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
