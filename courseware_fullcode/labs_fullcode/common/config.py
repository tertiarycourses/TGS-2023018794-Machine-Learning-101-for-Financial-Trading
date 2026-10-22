"""
config.py - paths, API keys and the online/offline switch shared by every lab.

Lion City Capital (fictitious, for training) keeps its Alpaca PAPER-trading keys
in environment variables or in a local `.env` file (never in code, never in git).

    APCA_API_KEY_ID=PK...
    APCA_API_SECRET_KEY=...

If the keys are missing, or a script is run with `--offline`, the labs switch to
OFFLINE mode: bundled CSV data in labs/data/ and a local simulated paper
broker (common/broker.py -> PaperBrokerSim). Nothing in these labs can place a
live (real-money) order: every Alpaca client is created with paper=True.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------- paths
LAB_ROOT = Path(__file__).resolve().parent.parent          # .../labs
DATA_DIR = LAB_ROOT / "data"
STATE_DIR = LAB_ROOT / "_state"                            # simulated broker state, logs
OUTPUT_DIR = LAB_ROOT / "_outputs"                         # charts and reports
ENV_FILE = LAB_ROOT / ".env"

KEY_ENV = "APCA_API_KEY_ID"
SECRET_ENV = "APCA_API_SECRET_KEY"


def load_env_file(path: Path = ENV_FILE) -> dict:
    """Very small .env parser: KEY=VALUE lines, '#' comments, optional quotes.

    Values already present in the real environment win (os.environ.setdefault)."""
    loaded = {}
    if not path.exists():
        return loaded
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ.setdefault(key, value)
            loaded[key] = value
    return loaded


load_env_file()


def get_keys() -> tuple[str | None, str | None]:
    """Return (api_key, secret_key) from the environment / .env file."""
    return os.environ.get(KEY_ENV), os.environ.get(SECRET_ENV)


def offline_requested() -> bool:
    """True if the learner passed --offline or set LAB_OFFLINE=1."""
    return "--offline" in sys.argv or os.environ.get("LAB_OFFLINE", "") == "1"


def is_online() -> bool:
    """Online = both Alpaca paper keys present AND offline not forced."""
    key, secret = get_keys()
    return bool(key and secret) and not offline_requested()


def mode_label() -> str:
    return "ONLINE  (Alpaca paper API)" if is_online() else "OFFLINE (bundled CSV + PaperBrokerSim)"


def output_path(filename: str) -> Path:
    """Path inside labs/_outputs/ (directory created on demand)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR / filename


def state_path(filename: str) -> Path:
    """Path inside labs/_state/ (directory created on demand)."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR / filename


def banner(title: str) -> None:
    """Print a consistent header so screenshots in the Learner Guide match."""
    print("=" * 72)
    print(f"{title}")
    print(f"Lion City Capital (fictitious, for training) | mode: {mode_label()}")
    print("=" * 72)
