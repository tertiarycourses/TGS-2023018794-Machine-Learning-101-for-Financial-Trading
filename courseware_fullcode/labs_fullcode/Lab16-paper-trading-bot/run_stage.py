"""
Lab 16 - Automation: scheduled forward test, risk checks, kill switch (A7, A8, K7)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/runner.py. Identical to:
    python -m pipeline run --loop
Run from the labs folder:
    python3 Lab16-paper-trading-bot/run_stage.py --loop
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.runner import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
