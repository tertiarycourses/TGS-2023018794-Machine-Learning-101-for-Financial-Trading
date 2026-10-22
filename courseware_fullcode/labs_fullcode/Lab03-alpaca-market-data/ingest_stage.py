"""
Lab 03 - Ingestion: multi-timeframe bars, headlines, data quality (A6, K9)
Lion City Capital (fictitious) | PAPER trading only | not investment advice

Runs the pipeline stage you build in pipeline/ingest.py. Identical to:
    python -m pipeline ingest
Run from the labs folder:
    python3 Lab03-alpaca-market-data/ingest_stage.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))       # make labs importable

from pipeline.config import apply_cli_flags                         # noqa: E402
from pipeline.ingest import main                                 # noqa: E402

if __name__ == "__main__":
    sys.exit(main(apply_cli_flags(sys.argv[1:])))
