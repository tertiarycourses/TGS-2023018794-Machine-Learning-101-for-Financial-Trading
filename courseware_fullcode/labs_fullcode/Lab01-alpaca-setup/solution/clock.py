"""
pipeline/clock.py - which US trading session is it, and which orders are allowed?

Alpaca 24/5 trading (US equities), New York time (ET), Monday-Friday:
    overnight  20:00 Sun -> 04:00 Fri  (each night 20:00 -> 04:00)
    pre        04:00 -> 09:30
    regular    09:30 -> 16:00
    after      16:00 -> 20:00
    closed     20:00 Fri -> 20:00 Sun (and exchange holidays)
Outside the regular session Alpaca accepts only LIMIT orders with
time_in_force DAY or GTC and extended_hours=True.

Singapore (SGT) is 12 hours ahead of New York in US summer time and 13 hours
ahead in US winter time, so a 09:00-18:30 SGT class sits in the US overnight
and pre-market sessions.
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

import pandas as pd

ET = ZoneInfo("America/New_York")
SGT = ZoneInfo("Asia/Singapore")

RULES = {
    "regular": {"order_types": ["market", "limit", "stop", "bracket"], "time_in_force": ["day", "gtc"],
                "extended_hours": False, "note": "all order types accepted"},
    "pre": {"order_types": ["limit"], "time_in_force": ["day", "gtc"], "extended_hours": True,
            "note": "extended hours: LIMIT orders only, extended_hours=True"},
    "after": {"order_types": ["limit"], "time_in_force": ["day", "gtc"], "extended_hours": True,
              "note": "extended hours: LIMIT orders only, extended_hours=True"},
    "overnight": {"order_types": ["limit"], "time_in_force": ["day", "gtc"], "extended_hours": True,
                  "note": "24/5 overnight session: LIMIT orders only, extended_hours=True"},
    "closed": {"order_types": ["limit"], "time_in_force": ["gtc"], "extended_hours": False,
               "note": "market closed: a GTC limit order queues for the next session"},
}


def session_at(ts: datetime) -> str:
    """Session name for a New York timestamp (naive timestamps are treated as ET)."""
    ts = pd.Timestamp(ts)
    ts = ts.tz_localize(ET) if ts.tzinfo is None else ts.tz_convert(ET)
    wd, t = ts.weekday(), ts.time()                     # Monday = 0 ... Sunday = 6
    if wd < 5 and time(9, 30) <= t < time(16, 0):
        return "regular"
    if wd < 5 and time(4, 0) <= t < time(9, 30):
        return "pre"
    if wd < 5 and time(16, 0) <= t < time(20, 0):
        return "after"
    if (t >= time(20, 0) and wd in (6, 0, 1, 2, 3)) or (t < time(4, 0) and wd in (0, 1, 2, 3, 4)):
        return "overnight"
    return "closed"


def broker_now(broker=None) -> datetime:
    """'Now' in ET: the simulator's replay clock if it has one, otherwise the real clock."""
    sim_now = getattr(broker, "state", {}).get("now") if broker is not None else None
    if sim_now:
        return pd.Timestamp(sim_now).tz_localize(ET).to_pydatetime()
    return datetime.now(timezone.utc).astimezone(ET)


def market_status(broker=None, now: datetime | None = None, override: str | None = None) -> dict:
    """Clock snapshot used by check, execution and the runner.

    override - force a session name (teaching aid, e.g. --session regular) when offline."""
    now = now or broker_now(broker)
    session = override or session_at(now)
    holiday = False
    if broker is not None and getattr(broker, "mode", "") == "alpaca-paper" and override is None:
        try:
            if session == "regular" and not broker.get_clock().is_open:
                session, holiday = "closed", True          # exchange holiday or early close
        except Exception:
            pass
    return {"now_et": now.astimezone(ET), "now_sgt": now.astimezone(SGT), "session": session,
            "holiday": holiday, **RULES[session]}


def describe(status: dict) -> str:
    return (f"{status['now_et']:%a %Y-%m-%d %H:%M} New York = {status['now_sgt']:%a %H:%M} Singapore | "
            f"session: {status['session'].upper()} ({status['note']})")


if __name__ == "__main__":
    print(describe(market_status()))
