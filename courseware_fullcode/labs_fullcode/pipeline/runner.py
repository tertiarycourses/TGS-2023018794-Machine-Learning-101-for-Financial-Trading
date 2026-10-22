"""
pipeline/runner.py - Stage 16: automation - the scheduled forward test.

One decision cycle = clock -> completed bars -> signal -> risk checks -> order
manager -> poll -> position -> trade-log row. Modes:

  python -m pipeline run --once                      one cycle (cron / launchd / Task Scheduler call this)
  python -m pipeline run --loop                      OFFLINE: forward-test replay of 2025, day by day
  python -m pipeline run --loop --interval 60 --live-paper --max-cycles 5
                                                     LIVE on the Alpaca PAPER account, any session
                                                     (24/5 extended-hours limit orders when the US
                                                     regular session is closed)
  python -m pipeline kill --on                       kill switch: the next cycle halts
  python -m pipeline schedule                        print cron / launchd / Windows Task Scheduler entries

The replay is a true forward test: each day the runner sees only bars up to the
previous close, and its market orders fill at that day's open in the simulator.
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import csv
import shlex
import sys
import time
from datetime import datetime, timedelta

import pandas as pd

from common.broker import enum_str, get_broker
from common.config import LAB_ROOT, is_online, output_path
from common.plotting import plt, save
from pipeline.clock import ET, SGT, describe, market_status
from pipeline.config import load_config, stage_banner
from pipeline.execution import DASHBOARD, OrderManager
from pipeline.indicators import ta_ema
from pipeline.ingest import load_bars
from pipeline.risk import RiskManager
from pipeline.signals import target_position

TRADE_LOG = output_path("trade_log.csv")
EQUITY_LOG = output_path("Lab16_equity_log.csv")
LIVE_LOG = output_path("live_paper_log.csv")
LOG_FIELDS = ["run_time", "bar_date", "symbol", "close", "ema_fast", "ema_slow", "signal", "position_before",
              "action", "qty", "order_id", "status", "fill_price", "equity", "checks"]


def decide(bars: pd.DataFrame, cfg: dict) -> dict:
    """Signal from COMPLETED bars only."""
    s = cfg["strategy"]
    tgt = target_position(s["name"], bars, **s["params"])
    row = {"bar_date": bars.index[-1].date(), "close": round(float(bars["close"].iloc[-1]), 4),
           "signal": int(tgt.iloc[-1]), "ema_fast": "", "ema_slow": ""}
    if s["name"] == "ema_cross":
        row["ema_fast"] = round(float(ta_ema(bars["close"], s["params"]["fast"]).iloc[-1]), 4)
        row["ema_slow"] = round(float(ta_ema(bars["close"], s["params"]["slow"]).iloc[-1]), 4)
    return row


def run_cycle(broker, om: OrderManager, risk: RiskManager, bars, run_time: str, cfg: dict,
              weight: float, allow_queue: bool = False, poll_seconds: int = 0) -> dict:
    sym = cfg["strategy"]["symbol"]
    d = decide(bars, cfg)
    qty_now = om.positions().get(sym, 0.0)
    pend = om.pending().get(sym, 0.0)
    row = {**d, "run_time": run_time, "symbol": sym, "position_before": qty_now, "action": "HOLD", "qty": 0,
           "order_id": "", "status": "", "fill_price": ""}
    wants_buy = d["signal"] == 1 and qty_now + pend == 0
    wants_sell = d["signal"] == 0 and qty_now > 0
    st = om.status()
    ok_trade, ok_buy, notes = risk.check(broker, st, sym, wants_buy, allow_queue=allow_queue)
    results = []
    tag = str(d["bar_date"]).replace("-", "")                 # one decision per bar -> idempotent client ids
    if ok_trade and wants_buy and ok_buy:
        results = om.rebalance({sym: weight}, tag=tag, poll_seconds=poll_seconds)
    elif ok_trade and wants_sell:
        results = om.rebalance({sym: 0.0}, tag=tag, poll_seconds=poll_seconds)
    elif wants_buy or wants_sell:
        row["action"] = "BLOCKED"
    if results:
        r = results[0]
        q = r["qty"]
        row.update(action=r["side"].upper(), qty=int(q) if float(q).is_integer() else q, order_id=r["order_id"][:8],
                   status=r["status"], fill_price=r["fill_price"] or "")
    elif d["signal"] == 1 and pend > 0:
        notes = notes + [f"buy order for {pend:g} shares still working"]
    row["equity"] = round(float(broker.get_account().equity), 2)
    row["checks"] = "; ".join(notes)
    return row


def append_log(path, rows, fresh=False):
    new = fresh or not path.exists()
    with open(path, "w" if fresh else "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerows(rows)


def print_row(r, out=print):
    ema = f"  EMA {r['ema_fast']:>8} / {r['ema_slow']:>8}" if r["ema_fast"] != "" else ""
    out(f"  {r['bar_date']}  close {r['close']:8.2f}{ema}  -> {r['action']:<7} {r['qty'] or '':>4} "
        f"{r['status']:<8} equity {r['equity']:>11,.2f}  [{r['checks']}]")


def replay(cfg: dict, start: str, end: str, interval: float = 0.0, quiet: bool = False) -> dict:
    """OFFLINE forward test: each day the runner sees bars up to yesterday's close and fills at today's open."""
    out = print if not quiet else (lambda *a, **k: None)
    sym, s = cfg["strategy"]["symbol"], cfg["strategy"]
    broker = get_broker(state_file="bot_sim.json", reset=True)
    om, risk = OrderManager(broker, cfg, quiet=True), RiskManager(cfg)
    bars = load_bars(sym, cfg["data"]["start"], end)
    days = bars.loc[start:end].index
    out(f"Forward-test replay {s['name']} {s['params']} on {sym}, {days[0].date()} to {days[-1].date()} "
        f"(max position {cfg['risk']['max_position_pct']:.0%}, whole shares, fills at the open):")
    rows, eq_rows = [], []
    for day in days:
        today = bars.loc[day]
        broker.set_clock(day + timedelta(hours=9, minutes=35), is_open=True)
        broker.mark(sym, today["open"])                       # orders now fill at today's open
        row = run_cycle(broker, om, risk, bars.loc[:day - timedelta(days=1)], f"{day.date()} 09:35", cfg,
                        cfg["risk"]["max_position_pct"])
        rows.append(row)
        if row["action"] != "HOLD":
            print_row(row, out)
        broker.process_bar(sym, today["open"], today["high"], today["low"], today["close"], day)
        eq_rows.append({"date": day.date(), "equity": float(broker.get_account().equity),
                        "position": om.positions().get(sym, 0.0), "close": today["close"]})
        broker.end_of_day()
        if risk.kill_switch_on():
            out("KILL_SWITCH found - stopping the replay.")
            break
        time.sleep(interval)
    append_log(TRADE_LOG, rows, fresh=True)
    pd.DataFrame(eq_rows).to_csv(EQUITY_LOG, index=False)
    first, last = eq_rows[0]["equity"], eq_rows[-1]["equity"]
    bh = bars.loc[days[-1], "close"] / bars.loc[days[0], "open"] - 1
    orders = sum(r["action"] in ("BUY", "SELL") for r in rows)
    out(f"\nForward test {days[0].date()} to {days[-1].date()}: {len(days)} sessions, {orders} orders")
    out(f"  Equity: USD {first:,.2f} -> USD {last:,.2f}  ({last / 100_000 - 1:+.2%})")
    out(f"  {sym} buy & hold over the same days: {bh:+.2%}")
    out(f"  Decision log -> _outputs/{TRADE_LOG.name} ({len(rows)} rows); equity -> _outputs/{EQUITY_LOG.name}")
    df = pd.DataFrame(eq_rows).set_index("date")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["equity"] / df["equity"].iloc[0], label="Runner (paper, forward test)")
    ax.plot(df.index, df["close"] / df["close"].iloc[0], label=f"{sym} buy & hold", alpha=0.8)
    ax.fill_between(df.index, 0.8, 1.3, where=df["position"] > 0, color="green", alpha=0.07, label="In position")
    ax.set_ylim(min(0.8, (df["equity"] / df["equity"].iloc[0]).min() - 0.02), None)
    ax.set_title(f"Lab 16 forward test: {s['name']} {s['params']} on {sym}")
    ax.legend(loc="upper left")
    save(fig, "Lab16_forward_test.png")
    return {"sessions": len(days), "orders": orders, "final_equity": last, "return": last / 100_000 - 1, "bh": float(bh),
            "trades": [{"date": str(r["bar_date"]), "action": r["action"], "qty": r["qty"]} for r in rows
                       if r["action"] in ("BUY", "SELL")]}


def completed_bars(cfg: dict) -> pd.DataFrame:
    sym = cfg["strategy"]["symbol"]
    if is_online():
        bars = load_bars(sym, (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"), None)
        return bars[bars.index.date < datetime.now(ET).date()]          # drop today's unfinished bar
    return load_bars(sym, "2024-01-01", cfg["data"]["end"])


def once(cfg: dict, quiet: bool = False) -> dict:
    """One cycle - what the scheduler calls. Offline it acts at the open after the last bundled bar."""
    out = print if not quiet else (lambda *a, **k: None)
    broker = get_broker(state_file="bot_sim.json")
    om, risk = OrderManager(broker, cfg, quiet=quiet), RiskManager(cfg)
    bars = completed_bars(cfg)
    if broker.mode == "offline-sim":
        nxt = bars.index[-1] + pd.offsets.BDay(1)
        broker.set_clock(nxt + timedelta(hours=9, minutes=35), is_open=True)
        broker.mark(cfg["strategy"]["symbol"], float(bars["close"].iloc[-1]))
    out(f"Clock: {describe(om.status())}")
    row = run_cycle(broker, om, risk, bars, datetime.now().isoformat(timespec="seconds"), cfg,
                    cfg["risk"]["max_position_pct"] if broker.mode == "offline-sim" else cfg["live_paper"]["max_position_pct"],
                    allow_queue=broker.mode == "alpaca-paper")
    append_log(TRADE_LOG if broker.mode == "offline-sim" else LIVE_LOG, [row])
    print_row(row, out)
    out(f"Logged to _outputs/{(TRADE_LOG if broker.mode == 'offline-sim' else LIVE_LOG).name}")
    return row


def live_loop(cfg: dict, interval: float, max_cycles: int, quiet: bool = False) -> list[dict]:
    """Repeated cycles on the Alpaca PAPER account (or the simulator if no keys), until the kill switch."""
    out = print if not quiet else (lambda *a, **k: None)
    if not is_online():
        out("No Alpaca paper keys found: running the live loop against the offline simulator instead.\n"
            "Add APCA_API_KEY_ID / APCA_API_SECRET_KEY to labs/.env to trade the real paper account.")
    broker = get_broker(state_file="live_sim.json", reset=not is_online())
    om, risk = OrderManager(broker, cfg), RiskManager(cfg)
    weight = cfg["live_paper"]["max_position_pct"]
    poll = cfg["live_paper"]["poll_seconds"] if is_online() else 0
    out(f"Live paper loop: {cfg['strategy']['name']} {cfg['strategy']['params']} on {cfg['strategy']['symbol']}, "
        f"target {weight:.0%} of equity, every {interval:g} s, up to {max_cycles} cycles. "
        f"Halt with: python -m pipeline kill --on")
    rows = []
    for i in range(1, max_cycles + 1):
        out(f"\n--- cycle {i} | {describe(om.status())}")
        if risk.kill_switch_on():
            out("KILL SWITCH ON - no orders sent; loop stopped. Positions are left as they are; flatten with "
                "python -m pipeline execute --flatten" + (" --live-paper" if is_online() else ""))
            break
        row = run_cycle(broker, om, risk, completed_bars(cfg), datetime.now().isoformat(timespec="seconds"), cfg,
                        weight, allow_queue=True, poll_seconds=poll)
        append_log(LIVE_LOG, [row])
        rows.append(row)
        print_row(row, out)
        for p in broker.get_all_positions():
            out(f"  position {p.symbol} {float(p.qty):g} @ {float(p.avg_entry_price):.2f}  "
                f"unrealised P&L {float(p.unrealized_pl):+,.2f}")
        if i < max_cycles:
            time.sleep(interval)
    out(f"\nLive log -> _outputs/{LIVE_LOG.name}" + (f" | dashboard: {DASHBOARD}" if is_online() else ""))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline run", description="Stage 16 - automated forward test (PAPER)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true", help="one decision cycle")
    g.add_argument("--loop", action="store_true", help="offline replay, or live loop with --live-paper")
    ap.add_argument("--live-paper", action="store_true", help="run cycles on the Alpaca PAPER account")
    ap.add_argument("--interval", type=float, default=None, help="seconds between cycles")
    ap.add_argument("--max-cycles", type=int, default=5)
    ap.add_argument("--start", default="2025-01-02")
    ap.add_argument("--end", default="2025-12-31")
    a = ap.parse_args(argv)
    cfg = load_config()
    stage_banner(16, f"automation: {cfg['strategy']['name']} on {cfg['strategy']['symbol']} (paper only)")
    if a.loop and a.live_paper:
        live_loop(cfg, a.interval or 60, a.max_cycles)
    elif a.loop and not is_online():
        replay(cfg, a.start, a.end, a.interval or 0.0)
    elif a.loop:
        live_loop(cfg, a.interval or 300, a.max_cycles)
    else:
        once(cfg)
    return 0


# ------------------------------------------------------------------ scheduling
def schedule_main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline schedule", description="print scheduler entries")
    ap.parse_args(argv)
    cfg = load_config()
    stage_banner(16, "schedule the runner (cron / launchd / Windows Task Scheduler)")
    hh, mm = map(int, cfg["schedule"]["run_at_exchange_time"].split(":"))
    py, lab = sys.executable, str(LAB_ROOT)
    summer = datetime(2026, 7, 6, hh, mm, tzinfo=ET).astimezone(SGT)
    winter = datetime(2026, 1, 5, hh, mm, tzinfo=ET).astimezone(SGT)
    cmd = f"cd {shlex.quote(lab)} && {shlex.quote(py)} -m pipeline run --once >> _outputs/scheduler.log 2>&1"
    folder = output_path("Lab16_schedule")
    folder.mkdir(exist_ok=True)
    cron = (f"# Lion City Capital pipeline - one cycle at {hh:02d}:{mm:02d} New York time, Mon-Fri\n"
            f"# Singapore time: {summer:%H:%M} (US summer time) / {winter:%H:%M} (US winter time)\n"
            f"CRON_TZ=America/New_York\n{mm} {hh} * * 1-5 {cmd}\n"
            f"# macOS cron ignores CRON_TZ - use local Singapore time instead and change it twice a year:\n"
            f"# {summer.minute} {summer.hour} * * 1-5 {cmd}\n")
    days = "".join(f"\n      <dict><key>Weekday</key><integer>{d}</integer><key>Hour</key><integer>{summer.hour}</integer>"
                   f"<key>Minute</key><integer>{summer.minute}</integer></dict>" for d in range(1, 6))
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.lioncitycapital.pipeline</string>
  <key>ProgramArguments</key>
  <array><string>{py}</string><string>-m</string><string>pipeline</string><string>run</string><string>--once</string></array>
  <key>WorkingDirectory</key><string>{lab}</string>
  <key>StartCalendarInterval</key>
  <array>{days}
  </array>
  <key>StandardOutPath</key><string>{lab}/_outputs/scheduler.log</string>
  <key>StandardErrorPath</key><string>{lab}/_outputs/scheduler.log</string>
</dict>
</plist>
"""
    schtasks = (f'schtasks /Create /TN "LCC Pipeline" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST {summer:%H:%M} '
                f'/TR "cmd /c cd /d \\"{lab}\\" && python -m pipeline run --once >> _outputs\\scheduler.log 2>&1"\n')
    (folder / "crontab.txt").write_text(cron)
    (folder / "com.lioncitycapital.pipeline.plist").write_text(plist)
    (folder / "schtasks.cmd").write_text(schtasks)
    print(f"Run time {hh:02d}:{mm:02d} New York = {summer:%H:%M} Singapore (US summer) / {winter:%H:%M} (US winter)\n")
    print("1) cron (Linux; macOS see note)  ->  crontab -e, paste:\n" + cron)
    print("2) launchd (macOS)  ->  cp the plist to ~/Library/LaunchAgents/ and run: "
          "launchctl load ~/Library/LaunchAgents/com.lioncitycapital.pipeline.plist")
    print("3) Windows Task Scheduler  ->  run in a Command Prompt:\n" + schtasks)
    print(f"Files written to _outputs/{folder.name}/ (nothing was installed). The runner checks the clock and the kill "
          f"switch itself, so a double-fired job cannot double-trade: client_order_id is unique per decision bar.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
