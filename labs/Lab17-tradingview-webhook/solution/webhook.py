"""
pipeline/webhook.py - Stage 17: event-driven automation.

  TradingView alert --HTTPS POST JSON--> [tunnel] --> this receiver
      -> validate (shared secret, JSON, allow-list, qty limit, duplicate alert id)
      -> pipeline signal (the configured strategy's own view of the symbol, logged; optional veto)
      -> risk checks (kill switch, session, daily loss)          pipeline/risk.py
      -> order manager (session-aware PAPER order, idempotent)    pipeline/execution.py
      -> audit log  _outputs/Lab17_webhook_log.csv

Alert message (TradingView alert dialog, see Lab17 tradingview_alert_message.json):
  {"secret": "...", "id": "{{timenow}}-{{strategy.order.id}}", "ticker": "{{ticker}}",
   "action": "{{strategy.order.action}}", "qty": "{{strategy.order.contracts}}"}

    python -m pipeline webhook --port 8080            # run the receiver (Ctrl+C to stop)
    python -m pipeline alert-sim --url http://127.0.0.1:8080/webhook
    python -m pipeline webhook --selftest             # receiver + simulated alerts in one command
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import csv
import hashlib
import hmac
import json
import sys
import threading
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from common.broker import get_broker
from common.config import is_online, output_path
from pipeline.config import load_config, secret, stage_banner
from pipeline.execution import OrderManager
from pipeline.ingest import load_bars
from pipeline.risk import RiskManager
from pipeline.signals import target_position

LOG = output_path("Lab17_webhook_log.csv")
LOG_FIELDS = ["time", "client", "alert_id", "ticker", "action", "qty", "http", "result", "pipeline_signal",
              "order_id", "status", "detail"]
DEMO_SECRET = "lcc-demo-secret"


class Gateway:
    """Holds the broker, order manager, risk manager and the set of alert ids already processed."""

    def __init__(self, cfg: dict, session: str | None = None):
        self.cfg = cfg
        self.secret = secret(cfg, "webhook_secret") or DEMO_SECRET
        self.broker = get_broker(state_file="webhook_sim.json", reset=True)
        self.om = OrderManager(self.broker, cfg, session=session)
        self.risk = RiskManager(cfg)
        self.seen: set[str] = set()
        self.require_agreement = bool(cfg.get("webhook", {}).get("require_signal_agreement", False))

    def pipeline_signal(self, ticker: str) -> int | None:
        s = self.cfg["strategy"]
        try:
            bars = load_bars(ticker, self.cfg["data"]["start"], None if is_online() else self.cfg["data"]["end"])
            return int(target_position(s["name"], bars, **s["params"]).iloc[-1])
        except Exception:
            return None

    def handle(self, payload: dict) -> tuple[int, dict]:
        if not hmac.compare_digest(str(payload.get("secret", "")), self.secret):
            return 401, {"result": "rejected", "detail": "bad or missing secret"}
        ticker = str(payload.get("ticker", "")).upper().split(":")[-1]          # "NASDAQ:AAPL" -> "AAPL"
        action = str(payload.get("action", "")).lower()
        r = self.cfg["risk"]
        if ticker not in r["allowed_symbols"]:
            return 422, {"result": "rejected", "detail": f"{ticker or '?'} not on the allow-list"}
        if action not in ("buy", "sell"):
            return 422, {"result": "rejected", "detail": f"unknown action '{action}'"}
        try:
            qty = float(payload.get("qty", 0))
        except (TypeError, ValueError):
            return 422, {"result": "rejected", "detail": "qty is not a number"}
        if not 0 < qty <= r["max_order_qty"]:
            return 422, {"result": "rejected", "detail": f"qty must be between 0 and {r['max_order_qty']}"}
        alert_id = str(payload.get("id") or hashlib.sha1(json.dumps(
            {k: payload.get(k) for k in ("ticker", "action", "qty", "time")}, sort_keys=True).encode()).hexdigest()[:12])
        if alert_id in self.seen:
            return 200, {"result": "duplicate ignored", "alert_id": alert_id,
                         "detail": "alert already processed (TradingView retries are safe)"}
        sig = self.pipeline_signal(ticker)
        agrees = sig is None or (sig == 1) == (action == "buy")
        if self.require_agreement and not agrees:
            return 409, {"result": "rejected", "alert_id": alert_id, "pipeline_signal": sig,
                         "detail": f"pipeline signal for {ticker} is {sig}: it disagrees with the alert"}
        held = self.om.positions().get(ticker, 0.0)
        if action == "sell" and held <= 0:
            return 422, {"result": "rejected", "detail": f"no {ticker} position to sell (long-only)"}
        st = self.om.status()
        ok_trade, ok_buy, notes = self.risk.check(self.broker, st, ticker, action == "buy", allow_queue=is_online())
        if not ok_trade or (action == "buy" and not ok_buy):
            return 423, {"result": "blocked by risk", "detail": "; ".join(notes)}
        target = held + qty if action == "buy" else max(held - qty, 0.0)
        self.seen.add(alert_id)
        try:
            res = self.om.rebalance({ticker: target}, tag=f"tv{alert_id[-10:]}", units="shares",
                                    poll_seconds=self.cfg["live_paper"]["poll_seconds"] if is_online() else 0)
        except Exception as exc:
            return 502, {"result": "broker error", "detail": str(exc)[:200]}
        if not res:
            return 200, {"result": "no order needed", "alert_id": alert_id, "detail": "already at target"}
        o = res[0]
        return 200, {"result": "order submitted", "alert_id": alert_id, "pipeline_signal": sig,
                     "signal_agrees": agrees, "order_id": o["order_id"], "status": o["status"], "symbol": ticker,
                     "side": o["side"], "qty": o["qty"], "filled_avg_price": o["fill_price"]}


def make_handler(gw: Gateway, path: str = "/webhook"):
    class Handler(BaseHTTPRequestHandler):
        def _reply(self, code: int, body: dict) -> None:
            data = json.dumps(body, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._reply(200, {"status": "ok", "mode": gw.broker.mode, "kill_switch": gw.risk.kill_switch_on()})
            else:
                self._reply(404, {"detail": f"use POST {path}"})

        def do_POST(self):
            self.server.request_count += 1
            if self.path != path:
                return self._reply(404, {"detail": f"use POST {path}"})
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
            try:
                payload = json.loads(raw or b"{}")        # TradingView may send text/plain - parse anyway
                if not isinstance(payload, dict):
                    raise json.JSONDecodeError("not an object", "", 0)
                code, body = gw.handle(payload)
            except json.JSONDecodeError:
                payload, code, body = {}, 400, {"result": "rejected", "detail": "body is not valid JSON"}
            with open(LOG, "a", newline="") as fh:
                csv.DictWriter(fh, fieldnames=LOG_FIELDS, extrasaction="ignore").writerow({
                    "time": datetime.now().isoformat(timespec="seconds"), "client": self.client_address[0],
                    "alert_id": body.get("alert_id", ""), "ticker": payload.get("ticker", ""),
                    "action": payload.get("action", ""), "qty": payload.get("qty", ""), "http": code,
                    "result": body.get("result"), "pipeline_signal": body.get("pipeline_signal", ""),
                    "order_id": body.get("order_id", ""), "status": body.get("status", ""),
                    "detail": body.get("detail", "")})
            print(f"  [{code}] {body}")
            self._reply(code, body)

        def log_message(self, *args):
            pass
    return Handler


def serve(cfg: dict, host: str, port: int, max_requests: int = 0, session: str | None = None, ready=None):
    gw = Gateway(cfg, session)
    with open(LOG, "w", newline="") as fh:
        csv.DictWriter(fh, fieldnames=LOG_FIELDS).writeheader()
    server = HTTPServer((host, port), make_handler(gw, cfg["webhook"]["path"]))
    server.request_count = 0
    if gw.secret == DEMO_SECRET:
        print("WARNING: demo secret in use. Set WEBHOOK_SECRET in labs/.env before exposing this server.")
    print(f"Listening on http://{host}:{server.server_port}{cfg['webhook']['path']} (health: /health) | broker "
          f"{gw.broker.mode} | session {gw.om.status()['session']} | kill switch "
          f"{'ON' if gw.risk.kill_switch_on() else 'off'}")
    if ready is not None:
        ready(server)
    try:
        while max_requests == 0 or server.request_count < max_requests:
            server.handle_request()
    except KeyboardInterrupt:
        pass
    server.server_close()
    acct = gw.broker.get_account()
    print(f"Receiver stopped after {server.request_count} alerts. Paper equity USD {float(acct.equity):,.2f}, positions "
          f"{[(p.symbol, p.qty) for p in gw.broker.get_all_positions()]}. Audit log -> _outputs/{LOG.name}")
    return gw


def test_alerts(secret_value: str) -> list[tuple[str, object, int]]:
    """What TradingView sends after substituting its placeholders, plus the expected HTTP code."""
    return [
        ("1. valid BUY 5 SPY", {"secret": secret_value, "id": "t1", "ticker": "SPY", "action": "buy", "qty": "5"}, 200),
        ("2. valid SELL 5 SPY", {"secret": secret_value, "id": "t2", "ticker": "AMEX:SPY", "action": "sell", "qty": "5"}, 200),
        ("3. wrong secret", {"secret": "guess", "id": "t3", "ticker": "SPY", "action": "buy", "qty": "5"}, 401),
        ("4. symbol not allowed", {"secret": secret_value, "id": "t4", "ticker": "TSLA", "action": "buy", "qty": "5"}, 422),
        ("5. qty above limit", {"secret": secret_value, "id": "t5", "ticker": "AAPL", "action": "buy", "qty": "5000"}, 422),
        ("6. malformed message", "ticker=SPY action=buy", 400),
        ("7. TradingView retry of alert 1", {"secret": secret_value, "id": "t1", "ticker": "SPY", "action": "buy",
                                             "qty": "5"}, 200),
    ]


def post(url: str, body) -> tuple[int, str]:
    data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


def send_test_alerts(url: str, secret_value: str) -> list[dict]:
    rows = []
    for title, body, expected in test_alerts(secret_value):
        code, text = post(url, body)
        ok = code == expected
        print(f"{title:<34} -> HTTP {code} (expected {expected}) {'OK' if ok else 'MISMATCH'}: {text[:110]}")
        rows.append({"test": title, "http": code, "expected": expected, "ok": ok})
    return rows


def selftest(cfg: dict) -> dict:
    """Start the receiver on a free local port, fire the simulated alerts, stop, summarise."""
    started = threading.Event()
    holder = {}

    def ready(server):
        holder["port"] = server.server_port
        started.set()
    n = len(test_alerts(""))
    t = threading.Thread(target=serve, args=(cfg, "127.0.0.1", 0, n, None if is_online() else "regular", ready),
                         daemon=True)
    t.start()
    started.wait(30)
    url = f"http://127.0.0.1:{holder['port']}{cfg['webhook']['path']}"
    rows = send_test_alerts(url, secret(cfg, "webhook_secret") or DEMO_SECRET)
    t.join(30)
    passed = sum(r["ok"] for r in rows)
    print(f"\nRESULT: {passed}/{len(rows)} alerts handled as expected")
    return {"passed": passed, "total": len(rows), "rows": rows}


def main(argv=None) -> int:
    cfg = load_config()
    ap = argparse.ArgumentParser(prog="python -m pipeline webhook", description="Stage 17 - TradingView webhook receiver")
    ap.add_argument("--host", default=cfg["webhook"]["host"])
    ap.add_argument("--port", type=int, default=cfg["webhook"]["port"])
    ap.add_argument("--max-requests", type=int, default=0, help="stop after N alerts (0 = run until Ctrl+C)")
    ap.add_argument("--selftest", action="store_true", help="run the receiver and the alert simulator together")
    a = ap.parse_args(argv)
    stage_banner(17, "event-driven automation: TradingView webhook -> signal -> risk -> execution")
    if a.selftest:
        return 0 if selftest(cfg)["passed"] == len(test_alerts("")) else 1
    serve(cfg, a.host, a.port, a.max_requests, None if is_online() else "regular")
    print("Expose it to TradingView with an HTTPS tunnel, e.g.  ngrok http 8080")
    return 0


def alert_sim_main(argv=None) -> int:
    cfg = load_config()
    ap = argparse.ArgumentParser(prog="python -m pipeline alert-sim", description="send simulated TradingView alerts")
    ap.add_argument("--url", default=f"http://127.0.0.1:{cfg['webhook']['port']}{cfg['webhook']['path']}")
    ap.add_argument("--secret", default=secret(cfg, "webhook_secret") or DEMO_SECRET)
    a = ap.parse_args(argv)
    rows = send_test_alerts(a.url, a.secret)
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
