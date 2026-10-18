"""
Lab 02 - Data validation against TradingView (A3, K5, K9)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/validate.py. Identical to:
    python -m pipeline validate --date 2025-12-31
Run from the labs folder:
    python3 Lab02-tradingview-charts/validate_stage.py --date 2025-12-31
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.validate import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
