"""
Lab 13 - A/B test two strategy variants (A5, K2)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/abtest.py. Identical to:
    python -m pipeline abtest --a trend_filter --b dip_buy
Run from the labs folder:
    python3 Lab13-ab-testing/abtest_stage.py --a trend_filter --b dip_buy
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.abtest import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
