"""
pipeline/execution.py - Stage 08: the order manager (PAPER trading only).

Target vs actual -> orders:
  1. read the market clock and pick the order style for the session
       regular              market (or limit / bracket) orders
       pre / after / overnight  LIMIT orders, time_in_force DAY, extended_hours=True (Alpaca 24/5)
       closed               GTC LIMIT order that queues for the next session
  2. price limit orders off the latest QUOTE (ask + buffer to buy, bid - buffer to sell)
  3. plan: target weight x equity / price -> target shares; minus shares held and
     shares already on open orders -> the order to send (long only)
  4. idempotency: every order gets a deterministic client_order_id
     (lcc-<tag>-<symbol>-<side>-<qty>); a re-run finds the existing order instead of
     sending a duplicate
  5. submit, then poll and print the order lifecycle (new -> filled), the position
     and where to see it in the Alpaca paper dashboard
  6. if an extended-hours order is rejected: explain, fall back to a GTC limit order
     that queues for the next session, and optionally run a BTC/USD crypto demo
     (24/7 market) purely to show the fill loop working live

    python -m pipeline execute --reset                         # offline simulator, session from the clock
    python -m pipeline execute --session regular --reset       # teaching override (offline)
    python -m pipeline execute --live-paper --targets SPY=0.05 # Alpaca paper account, any time of day
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import math
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime

from alpaca.trading.enums import OrderClass, OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.requests import (GetOrdersRequest, LimitOrderRequest, MarketOrderRequest,
                                     StopLossRequest, TakeProfitRequest)

from common.broker import OPEN_STATES, describe_order, enum_str, get_broker
from common.config import get_keys, is_online
from pipeline.clock import describe, market_status
from pipeline.config import load_config, stage_banner

TERMINAL = {"filled", "canceled", "expired", "rejected", "done_for_day"}
DASHBOARD = "https://app.alpaca.markets/paper/dashboard/overview  (Orders and Positions pages)"


@dataclass
class OrderPlan:
    symbol: str
    side: str            # buy | sell
    qty: float
    current_qty: float
    pending_qty: float   # signed shares already on open orders
    target_qty: float
    price: float
    reason: str


class OrderManager:
    """Turns target weights into idempotent, session-aware PAPER orders."""

    def __init__(self, broker, cfg: dict, session: str | None = None, quiet: bool = False):
        self.broker, self.cfg = broker, cfg
        self.out = print if not quiet else (lambda *a, **k: None)
        self.session_override = session
        self.buffer = cfg["live_paper"]["limit_buffer_bps"] / 1e4

    # ---------------- state
    def status(self) -> dict:
        online_clock = self.broker if getattr(self.broker, "mode", "") == "alpaca-paper" else None
        sim = self.broker if getattr(self.broker, "mode", "") == "offline-sim" and self.broker.state.get("now") else None
        st = market_status(online_clock or sim, override=self.session_override)
        if getattr(self.broker, "mode", "") == "offline-sim":     # make the simulator honour the session
            self.broker.state["market_open"] = st["session"] != "closed"
        return st

    def positions(self) -> dict[str, float]:
        return {p.symbol: float(p.qty) for p in self.broker.get_all_positions()}

    def pending(self) -> dict[str, float]:
        """Signed shares on open orders (+ buys, - sells), so a re-run does not double up."""
        out: dict[str, float] = {}
        for o in self.broker.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)):
            if o.order_class and enum_str(o.order_class) not in ("simple", "bracket"):
                continue
            q = float(o.qty) - float(o.filled_qty or 0)
            out[o.symbol] = out.get(o.symbol, 0.0) + (q if enum_str(o.side) == "buy" else -q)
        return out

    def quote(self, symbol: str, session: str) -> dict:
        """Latest bid/ask (online) or the simulator's last price +/- half a basis point (offline)."""
        if getattr(self.broker, "mode", "") != "alpaca-paper":
            last = float(self.broker.latest_price(symbol))
            return {"bid": last * (1 - 0.5e-4), "ask": last * (1 + 0.5e-4), "last": last, "source": "simulator last price"}
        from alpaca.data.enums import DataFeed
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest
        key, secret = get_keys()
        client = StockHistoricalDataClient(api_key=key, secret_key=secret)
        feeds = [DataFeed.OVERNIGHT, DataFeed.IEX] if session == "overnight" else [DataFeed.IEX]
        for feed in feeds:
            try:
                q = client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=symbol, feed=feed))[symbol]
                if q.bid_price and q.ask_price and q.ask_price >= q.bid_price > 0:
                    return {"bid": float(q.bid_price), "ask": float(q.ask_price),
                            "last": (float(q.bid_price) + float(q.ask_price)) / 2, "source": f"latest quote ({feed.value})"}
            except Exception:
                continue
        t = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol, feed=DataFeed.IEX))[symbol]
        px = float(t.price)
        return {"bid": px, "ask": px, "last": px, "source": "latest trade (no live quote)"}

    # ---------------- planning
    def plan(self, targets: dict[str, float], session: str, units: str = "weight") -> list[OrderPlan]:
        """units='weight': targets are fractions of equity; units='shares': targets are share counts."""
        equity = float(self.broker.get_account().equity)
        held, pend = self.positions(), self.pending()
        plans = []
        for sym, weight in targets.items():
            px = self.quote(sym, session)["last"]
            target_qty = (math.floor(max(weight, 0.0)) if units == "shares"
                          else math.floor(max(weight, 0.0) * equity / px))    # whole shares, long only
            cur, pq = held.get(sym, 0.0), pend.get(sym, 0.0)
            delta = target_qty - cur - pq
            if delta > 0:
                plans.append(OrderPlan(sym, "buy", float(delta), cur, pq, target_qty, px, f"target {target_qty} shares"))
            elif delta < 0 and cur + pq > 0:
                plans.append(OrderPlan(sym, "sell", float(min(-delta, cur + pq)), cur, pq, target_qty, px,
                                       f"target {target_qty} shares"))
            else:
                self.out(f"    {sym:<5} at target ({target_qty} shares; held {cur:g}, pending {pq:+g}) - no order")
        return sorted(plans, key=lambda p: p.side != "sell")             # sells first: exits free cash for buys

    @staticmethod
    def client_id(plan: OrderPlan, tag: str) -> str:
        cid = f"lcc-{tag}-{plan.symbol}-{plan.side}-{plan.qty:g}"
        return re.sub(r"[^A-Za-z0-9-]", "", cid)[:48]

    def request(self, plan: OrderPlan, order_type: str, st: dict, cid: str, quote: dict,
                take_profit: float = 0.05, stop_loss: float = 0.03):
        side = OrderSide.BUY if plan.side == "buy" else OrderSide.SELL
        limit = round(quote["ask"] * (1 + self.buffer) if plan.side == "buy" else quote["bid"] * (1 - self.buffer), 2)
        if st["session"] == "regular" and order_type == "market":
            return MarketOrderRequest(symbol=plan.symbol, qty=plan.qty, side=side, time_in_force=TimeInForce.DAY,
                                      client_order_id=cid)
        if st["session"] == "regular" and order_type == "bracket" and plan.side == "buy":
            return MarketOrderRequest(symbol=plan.symbol, qty=plan.qty, side=side, time_in_force=TimeInForce.GTC,
                                      order_class=OrderClass.BRACKET, client_order_id=cid,
                                      take_profit=TakeProfitRequest(limit_price=round(plan.price * (1 + take_profit), 2)),
                                      stop_loss=StopLossRequest(stop_price=round(plan.price * (1 - stop_loss), 2)))
        if st["session"] == "closed":
            return LimitOrderRequest(symbol=plan.symbol, qty=plan.qty, side=side, time_in_force=TimeInForce.GTC,
                                     limit_price=limit, client_order_id=cid)
        return LimitOrderRequest(symbol=plan.symbol, qty=plan.qty, side=side, time_in_force=TimeInForce.DAY,
                                 limit_price=limit, extended_hours=st["extended_hours"], client_order_id=cid)

    # ---------------- submission
    def cancel_protective(self, symbol: str) -> int:
        """Cancel open SELL orders (stops, bracket exit legs) that reserve shares we now want to sell."""
        n = 0
        req = GetOrdersRequest(status=QueryOrderStatus.OPEN, nested=True, symbols=[symbol])
        for o in self.broker.get_orders(filter=req):
            for leg in [o] + list(o.legs or []):
                if enum_str(leg.side) == "sell" and enum_str(leg.status) in OPEN_STATES | {"held"}:
                    try:
                        self.broker.cancel_order_by_id(leg.id)
                        n += 1
                    except Exception:
                        pass
        if n:
            self.out(f"    cancelled {n} protective exit order(s) on {symbol} that reserved the shares")
        return n

    def existing(self, cid: str):
        try:
            return self.broker.get_order_by_client_id(cid)
        except Exception:
            return None

    def submit(self, plan: OrderPlan, st: dict, tag: str, order_type: str = "auto", **kw) -> dict:
        order_type = ("market" if st["session"] == "regular" else "limit") if order_type == "auto" else order_type
        cid = self.client_id(plan, tag)
        dup = self.existing(cid)
        if dup is not None:
            self.out(f"    DUPLICATE {cid}: already submitted (status {enum_str(dup.status)}) - not sent again")
            return {**asdict(plan), "client_order_id": cid, "order_id": str(dup.id), "status": enum_str(dup.status),
                    "fill_price": dup.filled_avg_price, "note": "duplicate skipped"}
        if plan.side == "sell":
            self.cancel_protective(plan.symbol)
        q = self.quote(plan.symbol, st["session"])
        req = self.request(plan, order_type, st, cid, q, **kw)
        kind = (f"{enum_str(req.type).upper()} {enum_str(req.time_in_force).upper()}"
                + (" extended_hours" if getattr(req, "extended_hours", False) else "")
                + (" BRACKET" if getattr(req, "order_class", None) == OrderClass.BRACKET else ""))
        lim = f" limit {req.limit_price}" if getattr(req, "limit_price", None) else ""
        self.out(f"    -> {plan.side.upper()} {plan.qty:g} {plan.symbol} | {kind}{lim} | quote bid {q['bid']:.2f} / "
                 f"ask {q['ask']:.2f} ({q['source']}) | {cid}")
        note = ""
        try:
            order = self.broker.submit_order(req)
        except Exception as exc:
            if not getattr(req, "extended_hours", False):
                self.out(f"    REJECTED: {exc}")
                return {**asdict(plan), "client_order_id": cid, "order_id": "", "status": "rejected",
                        "fill_price": None, "note": str(exc)[:120]}
            self.out(f"    REJECTED extended-hours order: {exc}")
            self.out("    Why: the asset or account may not be enabled for overnight / extended-hours trading, the limit\n"
                     "    may be outside the allowed price band, or the session just changed. Falling back to a GTC\n"
                     "    LIMIT order that queues for the next regular session.")
            cid = (cid + "-q")[:48]
            order = self.broker.submit_order(LimitOrderRequest(
                symbol=plan.symbol, qty=plan.qty, side=req.side, time_in_force=TimeInForce.GTC,
                limit_price=req.limit_price, client_order_id=cid))
            note = "fallback GTC queued"
        return {**asdict(plan), "client_order_id": cid, "order_id": str(order.id), "status": enum_str(order.status),
                "fill_price": order.filled_avg_price, "note": note, "_order": order}

    def poll(self, order, seconds: int) -> object:
        """Poll an order and print each status change until it is terminal or time runs out."""
        seen, deadline = [enum_str(order.status)], time.time() + seconds
        while enum_str(order.status) not in TERMINAL and time.time() < deadline:
            time.sleep(2)
            order = self.broker.get_order_by_id(order.id)
            if enum_str(order.status) != seen[-1]:
                seen.append(enum_str(order.status))
        self.out(f"       lifecycle: {' -> '.join(seen)}" + ("" if enum_str(order.status) in TERMINAL
                                                           else "  (still working - it stays on the book)"))
        self.out(f"       {describe_order(order)}")
        return order

    def rebalance(self, targets: dict[str, float], tag: str | None = None, order_type: str = "auto",
                  poll_seconds: int = 0, units: str = "weight", **kw) -> list[dict]:
        st = self.status()
        tag = tag or datetime.now().strftime("%Y%m%d")
        results = []
        for plan in self.plan(targets, st["session"], units):
            res = self.submit(plan, st, tag, order_type, **kw)
            if "_order" in res:
                final = self.poll(res.pop("_order"), poll_seconds)
                res.update(status=enum_str(final.status), fill_price=final.filled_avg_price)
            results.append(res)
        return results


def crypto_demo(broker, cfg, out=print) -> None:
    """Live demonstration of the fill loop on a 24/7 market. NOT part of the stock strategy."""
    if getattr(broker, "mode", "") != "alpaca-paper":
        out("  Crypto demo needs Alpaca paper keys (online mode) - skipped offline.")
        return
    from alpaca.data.historical import CryptoHistoricalDataClient
    from alpaca.data.requests import CryptoLatestQuoteRequest
    sym = cfg["live_paper"]["crypto_demo_symbol"]
    q = CryptoHistoricalDataClient().get_crypto_latest_quote(CryptoLatestQuoteRequest(symbol_or_symbols=sym))[sym]
    buf = cfg["live_paper"]["limit_buffer_bps"] / 1e4
    qty = round(cfg["live_paper"]["crypto_demo_notional"] / float(q.ask_price), 6)
    out(f"  DEMO ONLY (the course is stock-focused): {sym} trades 24/7, so this shows a live fill right now.")
    om = OrderManager(broker, cfg)
    for side, px in (("buy", float(q.ask_price) * (1 + buf)), ("sell", float(q.bid_price) * (1 - buf))):
        req = LimitOrderRequest(symbol=sym, qty=qty, side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
                                time_in_force=TimeInForce.GTC, limit_price=round(px, 2),
                                client_order_id=f"lcc-demo-{side}-{datetime.now():%H%M%S%f}"[:48])
        out(f"    -> {side.upper()} {qty} {sym} LIMIT GTC {req.limit_price}")
        order = om.poll(broker.submit_order(req), cfg["live_paper"]["poll_seconds"])
        if side == "buy" and enum_str(order.status) != "filled":
            out("    buy not filled yet - cancelling the demo order")
            broker.cancel_order_by_id(order.id)
            return


def parse_targets(items: list[str]) -> dict[str, float]:
    out = {}
    for it in items:
        sym, _, w = it.partition("=")
        out[sym.upper()] = float(w)
    return out


def run(targets: dict[str, float] | None = None, session: str | None = None, order_type: str = "auto",
        live_paper: bool = False, reset: bool = False, crypto: bool = False, flatten: bool = False,
        tag: str | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    if live_paper and not is_online():
        out("--live-paper needs Alpaca PAPER keys in labs/.env (APCA_API_KEY_ID, APCA_API_SECRET_KEY).\n"
            "No keys found, so this run uses the offline simulator instead.")
    broker = get_broker(state_file="exec_sim.json", reset=reset)
    if is_online() and session:
        out(f"  (--session {session} is ignored online: the real Alpaca clock decides)")
        session = None
    om = OrderManager(broker, cfg, session=session, quiet=quiet)
    st = om.status()
    out(f"\n[1] Market clock: {describe(st)}")
    out(f"    allowed now: {', '.join(st['order_types'])} | time_in_force {'/'.join(st['time_in_force'])} | "
        f"extended_hours={st['extended_hours']}")
    targets = targets or {"SPY": 0.30, "AAPL": 0.10}
    if flatten:
        targets = {s: 0.0 for s in om.positions()}
    if live_paper or is_online():
        cap = cfg["live_paper"]["max_position_pct"]
        capped = {s: min(w, cap) for s, w in targets.items()}
        if capped != targets:
            out(f"    live paper: each weight capped at {cap:.0%} of equity -> {capped}")
        targets = capped
    acct = broker.get_account()
    out(f"\n[2] Account {acct.account_number} ({broker.mode}): equity USD {float(acct.equity):,.2f}, "
        f"cash USD {float(acct.cash):,.2f}; targets {targets}")
    out("\n[3] Plan (target vs actual) -> orders:")
    tag = tag or datetime.now().strftime("%Y%m%d")
    results = om.rebalance(targets, tag=tag, order_type=order_type,
                           poll_seconds=cfg["live_paper"]["poll_seconds"] if is_online() else 0)
    out("\n[4] Idempotency check - the same decision run again:")
    again = om.rebalance(targets, tag=tag, order_type=order_type, poll_seconds=0)
    if not again:
        out("    no new orders: positions plus pending orders already match the targets")
    sent = next((r for r in results if r.get("order_id")), None)        # an order the broker accepted
    if sent:
        dup = om.submit(OrderPlan(**{k: sent[k] for k in OrderPlan.__dataclass_fields__}), om.status(), tag)
        if dup["note"] != "duplicate skipped":
            out("    WARNING: a duplicate order was sent - check client_order_id logic")
    out("\n[5] Positions:")
    for p in broker.get_all_positions():
        out(f"    {p.symbol:<6} qty {float(p.qty):g}  avg entry {float(p.avg_entry_price):.2f}  "
            f"market value USD {float(p.market_value):,.2f}  unrealised P&L {float(p.unrealized_pl):+,.2f}")
    if not broker.get_all_positions():
        out("    none (orders may still be queued or working)")
    opens = broker.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN))
    out(f"    open orders: {len(opens)}" + "".join(
        f"\n      {describe_order(o)}" + "".join(f"\n        leg {describe_order(leg)}" for leg in (o.legs or []))
        for o in opens))
    if crypto:
        out("\n[6] Crypto fill-loop demonstration:")
        crypto_demo(broker, cfg, out)
    if broker.mode == "alpaca-paper":
        out(f"\nSee the orders and fills in the Alpaca PAPER dashboard: {DASHBOARD}")
    acct = broker.get_account()
    filled = sum(r["status"] == "filled" for r in results)
    queued = sum(r["status"] in OPEN_STATES for r in results)
    out(f"\nRESULT: {len(results)} orders ({filled} filled, {queued} working/queued), "
        f"equity USD {float(acct.equity):,.2f}, session {st['session']}")
    return {"session": st["session"], "orders": [{k: v for k, v in r.items() if not k.startswith("_")} for r in results],
            "filled": filled, "queued": queued, "equity": float(acct.equity)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline execute", description="Stage 08 - order manager (paper)")
    ap.add_argument("--targets", nargs="+", default=None, help="SYMBOL=weight, e.g. SPY=0.30 AAPL=0.10")
    ap.add_argument("--order-type", default="auto", choices=["auto", "market", "limit", "bracket"])
    ap.add_argument("--session", default=None, choices=["regular", "pre", "after", "overnight", "closed"],
                    help="offline teaching override of the market session")
    ap.add_argument("--live-paper", action="store_true", help="use the Alpaca paper account (needs keys)")
    ap.add_argument("--crypto-demo", action="store_true", help="also run the BTC/USD fill-loop demo (online)")
    ap.add_argument("--flatten", action="store_true", help="target 0 for every position held")
    ap.add_argument("--tag", default=None, help="decision tag used in client_order_id (default: today)")
    ap.add_argument("--reset", action="store_true", help="reset the offline simulated account")
    a = ap.parse_args(argv)
    stage_banner(8, "execution: target vs actual -> paper orders")
    run(parse_targets(a.targets) if a.targets else None, a.session, a.order_type, a.live_paper, a.reset,
        a.crypto_demo, a.flatten, a.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
