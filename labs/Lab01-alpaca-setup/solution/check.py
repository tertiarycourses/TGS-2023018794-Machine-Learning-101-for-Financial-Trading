"""
pipeline/check.py - Stage 01: `python -m pipeline check`

Pre-flight check that every later stage relies on:
  [1] config.yaml loads and passes validation (paper only, no secrets in the file)
  [2] Python libraries are installed
  [3] secrets are found in the environment (values are never printed)
  [4] the PAPER broker answers (Alpaca paper account online, PaperBrokerSim offline)
  [5] the market clock: US session now, Singapore time, which order types are allowed
  [6] the market-data path returns bars
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import importlib
import sys
from pathlib import Path

from common.broker import get_broker
from common.config import LAB_ROOT, is_online
from common.data import data_source, get_bars
from pipeline.clock import describe, market_status
from pipeline.config import load_config, secret, stage_banner

def rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(LAB_ROOT))
    except ValueError:
        return str(path)


LIBRARIES = ["pandas", "numpy", "scipy", "sklearn", "xgboost", "matplotlib", "yaml", "alpaca"]


def run(reset: bool = False, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config(strict=False)
    problems = list(cfg["_problems"])

    out(f"\n[1] Configuration  {rel(cfg['_path'])}")
    out(f"    firm {cfg.get('firm')} | mode {cfg.get('mode')} | broker {cfg['broker']['name']} paper={cfg['broker']['paper']}")
    out(f"    universe {len(cfg['universe']['trade'])} symbols: {' '.join(cfg['universe']['trade'])}")
    s = cfg["strategy"]
    out(f"    strategy {s['name']} {s['params']} on {s['symbol']} | execution {s['execution']} | costs {cfg['costs']['preset']}")
    r = cfg["risk"]
    out(f"    risk: max position {r['max_position_pct']:.0%}, max daily loss {r['max_daily_loss_pct']:.0%}, "
        f"max order USD {r['max_order_value']:,}, kill switch file {r['kill_switch_file']}")
    out("    validation: " + ("OK" if not problems else "; ".join(problems)))

    out("\n[2] Libraries")
    for name in LIBRARIES:
        try:
            mod = importlib.import_module(name)
            out(f"    OK   {name:<11} {getattr(mod, '__version__', '')}")
        except ImportError:
            problems.append(f"library {name} missing")
            out(f"    MISSING {name} -> pip install -r requirements.txt")

    out("\n[3] Secrets (names from config.yaml, values from the environment / .env)")
    for name, env in cfg["secrets_from_env"].items():
        val = secret(cfg, name)
        shown = "not set" if not val else (f"found ({val[:4]}...)" if name == "alpaca_key" else "found (hidden)")
        out(f"    {env:<20} {shown}")

    broker = get_broker(state_file=cfg["broker"]["sim_state_file"], reset=reset)
    acct = broker.get_account()
    out(f"\n[4] Paper broker ({broker.mode}) - {'Alpaca paper API' if is_online() else 'offline simulator'}")
    out(f"    account {acct.account_number} | status {acct.status} | equity USD {float(acct.equity):,.2f} | "
        f"cash USD {float(acct.cash):,.2f} | buying power USD {float(acct.buying_power):,.2f} | "
        f"positions {len(broker.get_all_positions())}")

    status = market_status(broker if is_online() else None)
    out("\n[5] Market clock")
    out("    " + describe(status))

    bars = get_bars(cfg["strategy"]["symbol"], "2025-12-01", cfg["data"]["end"])
    out(f"\n[6] Market data - {data_source()}")
    out("    " + bars.tail(3).round(2).to_string().replace("\n", "\n    "))

    ready = not problems
    out(f"\nRESULT: {'PIPELINE READY - paper trading only' if ready else 'NOT READY - ' + '; '.join(problems)}")
    return {"ready": ready, "problems": problems, "mode": broker.mode, "equity": float(acct.equity),
            "account": acct.account_number, "session": status["session"],
            "last_close": float(bars["close"].iloc[-1]), "last_date": str(bars.index[-1].date())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline check", description="Stage 01 - pre-flight check")
    ap.add_argument("--reset", action="store_true", help="reset the offline simulated account to USD 100,000")
    a = ap.parse_args(argv)
    stage_banner(1, "pipeline check (config, keys, paper broker, clock, data)")
    return 0 if run(reset=a.reset)["ready"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
