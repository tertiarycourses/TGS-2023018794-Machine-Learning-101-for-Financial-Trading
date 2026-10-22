"""
Lab 17 - simulate TradingView alerts locally (no paid TradingView plan needed).
Sends seven alerts to the running receiver - two valid orders, four that must be
rejected and one TradingView retry that must be ignored - and checks each HTTP code.
Identical to:  python -m pipeline alert-sim --url http://127.0.0.1:8080/webhook
Run in a SECOND terminal while webhook_stage.py is running (from labs):
    python3 Lab17-tradingview-webhook/send_test_alert.py --url http://127.0.0.1:8080/webhook
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.config import apply_cli_flags        # noqa: E402
from pipeline.webhook import alert_sim_main        # noqa: E402

if __name__ == "__main__":
    sys.exit(alert_sim_main(apply_cli_flags(sys.argv[1:])))
