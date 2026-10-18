"""
Lab 17 - Event-driven automation: TradingView webhook -> signal -> risk -> execution (A7, K5, K7)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/webhook.py. Identical to:
    python -m pipeline webhook --port 8080
Run from the labs folder:
    python3 Lab17-tradingview-webhook/webhook_stage.py --port 8080
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.webhook import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
