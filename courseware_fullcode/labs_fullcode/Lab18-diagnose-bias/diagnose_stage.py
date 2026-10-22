"""
Lab 18 - Diagnostics: automated bias checks (A9, K8)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/diagnose.py. Identical to:
    python -m pipeline diagnose
Run from the labs folder:
    python3 Lab18-diagnose-bias/diagnose_stage.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.diagnose import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
