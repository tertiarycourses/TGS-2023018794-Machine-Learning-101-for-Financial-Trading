"""
Lab 15 - Backtest engine: cost scenarios and break-even (A7, A8, K7)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/backtest.py. Identical to:
    python -m pipeline backtest --strategies dip_buy trend_filter
Run from the labs folder:
    python3 Lab15-trading-costs/backtest_stage.py --strategies dip_buy trend_filter
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.backtest import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
