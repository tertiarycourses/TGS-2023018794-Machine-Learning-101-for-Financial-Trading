"""
pipeline/risk.py - Stage 16 (support): pre-trade risk checks and the kill switch.

Every automated order path (runner, webhook, agents) calls RiskManager.check()
before the order manager may send anything. The risk layer is deterministic code
driven by config.yaml - no model or AI agent can loosen it.

  kill switch      if labs/KILL_SWITCH exists, nothing trades
  session          closed market -> no new orders (unless queuing GTC is allowed)
  daily loss       equity down >= max_daily_loss_pct since the last close -> no new buys
  allow-list       only universe symbols may be bought
  account          trading_blocked -> no buys
  order size       qty x price capped at max_order_value

    python -m pipeline kill --on | --off | --status
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import math
import sys
from datetime import datetime

from common.config import STATE_DIR
from pipeline.config import kill_switch_path, load_config


class RiskManager:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or load_config()
        self.r = self.cfg["risk"]

    def kill_switch_on(self) -> bool:
        return kill_switch_path(self.cfg).exists()

    def check(self, broker, status: dict, symbol: str, wants_buy: bool, allow_queue: bool = False):
        """Return (ok_to_trade, ok_to_buy, notes). Exits stay allowed unless halted or closed."""
        if self.kill_switch_on():
            return False, False, ["KILL_SWITCH present - trading halted"]
        notes = []
        if status["session"] == "closed":
            if not allow_queue:
                return False, False, ["market closed"]
            notes.append("market closed - order will queue (GTC) for the next session")
        acct = broker.get_account()
        equity, last = float(acct.equity), float(acct.last_equity)
        day = equity / last - 1 if last else 0.0
        ok_buy = True
        if day <= -self.r["max_daily_loss_pct"]:
            ok_buy = False
            notes.append(f"daily loss {day:.2%} breaches {self.r['max_daily_loss_pct']:.0%} limit - no new buys")
        if wants_buy and symbol not in self.r["allowed_symbols"]:
            ok_buy = False
            notes.append(f"{symbol} not on the allow-list")
        if wants_buy and getattr(acct, "trading_blocked", False):
            ok_buy = False
            notes.append("account trading blocked")
        return True, ok_buy, notes or ["all checks passed"]

    def cap_weight(self, weight: float, equity: float, price: float) -> float:
        """Cap a target weight by max_position_pct and max_order_value."""
        w = min(weight, self.r["max_position_pct"])
        max_qty = math.floor(self.r["max_order_value"] / price) if price > 0 else 0
        return min(w, max_qty * price / equity) if equity > 0 else 0.0


def kill_main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline kill", description="Kill switch (stops all trading)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--on", action="store_true", help="halt: create the kill-switch file")
    g.add_argument("--off", action="store_true", help="resume: move the kill-switch file to the halt history")
    g.add_argument("--status", action="store_true", help="show whether trading is halted (default)")
    a = ap.parse_args(argv)
    path = kill_switch_path(load_config())
    if a.on:
        path.write_text(f"halted {datetime.now().isoformat(timespec='seconds')}\n")
        print(f"KILL SWITCH ON  -> {path.name} created. Every runner, webhook and agent order is now blocked.")
    elif a.off:
        if path.exists():
            hist = STATE_DIR / "kill_switch_history"
            hist.mkdir(parents=True, exist_ok=True)
            dest = hist / f"KILL_SWITCH.{datetime.now():%Y%m%d-%H%M%S}"
            path.rename(dest)                                  # kept as an audit record, never deleted
            print(f"KILL SWITCH OFF -> moved to _state/kill_switch_history/{dest.name}. Trading may resume.")
        else:
            print("KILL SWITCH already off.")
    else:
        print(f"KILL SWITCH {'ON (trading halted)' if path.exists() else 'OFF'}  ({path.name})")
    return 0


if __name__ == "__main__":
    sys.exit(kill_main(sys.argv[1:]))
