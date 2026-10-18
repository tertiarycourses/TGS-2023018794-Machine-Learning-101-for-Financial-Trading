"""
broker.py - one `get_broker()` for both modes.

ONLINE : AlpacaPaperBroker - a thin wrapper around alpaca-py's
         TradingClient(paper=True). Every TradingClient method works on it
         (get_account, submit_order, get_orders, close_position, ...).
OFFLINE: PaperBrokerSim - a tiny local simulator that accepts the SAME alpaca-py
         request objects (MarketOrderRequest, LimitOrderRequest, StopOrderRequest,
         bracket orders, GetOrdersRequest ...) and returns objects with the same
         attribute names (status, filled_avg_price, qty ...). State is saved to
         labs/_state/<state_file>.json so positions survive between runs.

SAFETY: there is deliberately NO live-trading code path. paper=True is hard-coded.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace

import pandas as pd
from alpaca.trading.enums import (OrderClass, OrderSide, OrderStatus, OrderType,
                                  QueryOrderStatus, TimeInForce)

from common.config import get_keys, is_online, state_path

OPEN_STATES = {"new", "accepted", "held", "pending_new", "partially_filled"}


class SimAPIError(Exception):
    """Raised where the real Alpaca API would return an HTTP 4xx error."""


def enum_str(x) -> str:
    """'filled' for OrderStatus.FILLED or plain strings - works in both modes."""
    return str(getattr(x, "value", x)) if x is not None else "-"


def describe_order(o) -> str:
    """One-line summary of an Order object (real or simulated)."""
    px = getattr(o, "filled_avg_price", None)
    lim, stp = getattr(o, "limit_price", None), getattr(o, "stop_price", None)
    extra = (f" limit={float(lim):.2f}" if lim else "") + (f" stop={float(stp):.2f}" if stp else "")
    fill = f" filled@{float(px):.2f}" if px else ""
    return (f"{str(o.id)[:8]}  {o.symbol:<5} {enum_str(o.side):<4} {enum_str(o.order_type):<6} "
            f"qty={float(o.qty):g}{extra}  status={enum_str(o.status)}{fill}")


# ---------------------------------------------------------------- online wrapper
class AlpacaPaperBroker:
    """Delegates to alpaca-py TradingClient(paper=True) and adds latest_price()."""

    mode = "alpaca-paper"

    def __init__(self):
        from alpaca.trading.client import TradingClient
        key, secret = get_keys()
        self.client = TradingClient(api_key=key, secret_key=secret, paper=True)   # PAPER ONLY

    def __getattr__(self, name):
        return getattr(self.client, name)

    def latest_price(self, symbol: str) -> float:
        from alpaca.data.enums import DataFeed
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockLatestTradeRequest
        key, secret = get_keys()
        data = StockHistoricalDataClient(api_key=key, secret_key=secret)
        trade = data.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol, feed=DataFeed.IEX))
        return float(trade[symbol].price)


# ---------------------------------------------------------------- offline simulator
class PaperBrokerSim:
    """Minimal paper broker: cash account (no margin, no shorting), whole-book JSON state."""

    mode = "offline-sim"

    def __init__(self, state_file: str = "sim_account.json", starting_cash: float = 100_000.0,
                 reset: bool = False, slippage_bps: float = 1.0):
        self.path = state_path(state_file)
        self.slippage_bps = slippage_bps
        if reset or not self.path.exists():
            self.state = {"account_number": "SIM-LCC-0001", "cash": starting_cash,
                          "last_equity": starting_cash, "positions": {}, "orders": [],
                          "prices": {}, "now": None, "market_open": True}
            self._save()
        else:
            self.state = json.loads(self.path.read_text())

    # ---------- persistence and prices
    def _save(self):
        self.path.write_text(json.dumps(self.state, indent=2, default=str))

    def _now(self) -> datetime:
        return pd.Timestamp(self.state["now"]).to_pydatetime() if self.state["now"] else datetime.now()

    def latest_price(self, symbol: str) -> float:
        if symbol not in self.state["prices"]:
            from common.data import _bars_from_csv          # last bundled close
            self.state["prices"][symbol] = float(_bars_from_csv(symbol, None, None, "1Day")["close"].iloc[-1])
        return float(self.state["prices"][symbol])

    def set_clock(self, timestamp, is_open: bool = True):
        self.state["now"], self.state["market_open"] = str(pd.Timestamp(timestamp)), is_open
        self._save()

    def mark(self, symbol: str, price: float):
        """Update the simulated last price and fill any orders it triggers."""
        self.state["prices"][symbol] = float(price)
        self._match(symbol, price, price, price, price)
        self._save()

    def process_bar(self, symbol: str, open_: float, high: float, low: float, close: float, timestamp=None):
        """Replay one bar: pending market orders fill at the open, limits/stops by high/low."""
        if timestamp is not None:
            self.state["now"] = str(pd.Timestamp(timestamp))
        self.state["market_open"] = True
        self._match(symbol, open_, high, low, close)
        self.state["prices"][symbol] = float(close)
        self._save()

    def end_of_day(self):
        """Roll last_equity forward (used for the daily-loss risk check)."""
        self.state["last_equity"] = self._equity()
        self._save()

    # ---------- account / clock
    def _equity(self) -> float:
        mv = sum(p["qty"] * self.latest_price(s) for s, p in self.state["positions"].items())
        return self.state["cash"] + mv

    def get_account(self):
        eq = self._equity()
        return SimpleNamespace(
            account_number=self.state["account_number"], status="ACTIVE", currency="USD",
            cash=f"{self.state['cash']:.2f}", equity=f"{eq:.2f}", portfolio_value=f"{eq:.2f}",
            buying_power=f"{max(self.state['cash'], 0):.2f}", last_equity=f"{self.state['last_equity']:.2f}",
            long_market_value=f"{eq - self.state['cash']:.2f}", pattern_day_trader=False,
            trading_blocked=False, shorting_enabled=False)

    def get_clock(self):
        now = self._now()
        return SimpleNamespace(timestamp=now, is_open=self.state["market_open"],
                               next_open=now + timedelta(days=1), next_close=now + timedelta(hours=6))

    # ---------- orders
    def submit_order(self, order_data):
        """Accepts alpaca-py MarketOrderRequest / LimitOrderRequest / StopOrderRequest (incl. bracket)."""
        sym, side = order_data.symbol, enum_str(order_data.side)
        price = self.latest_price(sym)
        qty = float(order_data.qty) if order_data.qty else round(float(order_data.notional) / price, 6)
        if qty <= 0:
            raise SimAPIError("qty must be > 0")
        if side == "buy" and qty * price > self.state["cash"] + 1e-6:
            raise SimAPIError(f"insufficient buying power (need {qty * price:,.2f}, have {self.state['cash']:,.2f})")
        if side == "sell" and qty > self._qty_available(sym) + 1e-9:
            raise SimAPIError(f"insufficient qty available for order (requested: {qty:g}, "
                              f"available: {self._qty_available(sym):g})")
        cid = getattr(order_data, "client_order_id", None)
        if cid and any(o["client_order_id"] == cid for o in self.state["orders"]):
            raise SimAPIError("client_order_id must be unique")       # same rule as the Alpaca API (422)
        oclass = enum_str(getattr(order_data, "order_class", None) or "simple")
        parent = self._new_order(order_data, sym, side, qty, oclass)
        if oclass == "bracket":
            tp, sl = order_data.take_profit, order_data.stop_loss
            exit_side = "sell" if side == "buy" else "buy"
            parent["legs"] = [self._new_leg(parent, exit_side, "limit", limit_price=tp.limit_price)["id"],
                              self._new_leg(parent, exit_side, "stop", stop_price=sl.stop_price)["id"]]
        if self.state["market_open"]:
            self._match(sym, price, price, price, price)
        self._save()
        return self.get_order_by_id(parent["id"])

    def _new_order(self, req, sym, side, qty, oclass) -> dict:
        o = {"id": str(uuid.uuid4()), "client_order_id": req.client_order_id or str(uuid.uuid4()),
             "symbol": sym, "side": side, "qty": qty, "type": enum_str(req.type),
             "time_in_force": enum_str(req.time_in_force), "order_class": oclass,
             "limit_price": getattr(req, "limit_price", None), "stop_price": getattr(req, "stop_price", None),
             "status": "new" if self.state["market_open"] else "accepted", "parent_id": None, "legs": None,
             "submitted_at": str(self._now()), "filled_at": None, "filled_qty": 0.0, "filled_avg_price": None}
        self.state["orders"].append(o)
        return o

    def _new_leg(self, parent, side, otype, limit_price=None, stop_price=None) -> dict:
        leg = {**parent, "id": str(uuid.uuid4()), "client_order_id": str(uuid.uuid4()), "side": side,
               "type": otype, "limit_price": limit_price, "stop_price": stop_price, "status": "held",
               "parent_id": parent["id"], "legs": None, "time_in_force": "gtc"}
        self.state["orders"].append(leg)
        return leg

    def _qty_available(self, sym) -> float:
        held = self.state["positions"].get(sym, {}).get("qty", 0.0)
        reserved, seen = 0.0, set()
        for o in self.state["orders"]:
            if o["symbol"] == sym and o["side"] == "sell" and o["status"] in OPEN_STATES:
                group = o["parent_id"] or o["id"]           # bracket legs reserve the qty once
                if group not in seen:
                    seen.add(group)
                    reserved += o["qty"] - o["filled_qty"]
        return held - reserved

    def _match(self, sym, open_, high, low, close):
        """Fill open orders for `sym` that this bar/price would trigger."""
        slip = self.slippage_bps / 1e4
        for o in [o for o in self.state["orders"] if o["symbol"] == sym and o["status"] in OPEN_STATES - {"held"}]:
            if o["status"] not in OPEN_STATES:              # cancelled by an OCO sibling just now
                continue
            buy, px = o["side"] == "buy", None
            if o["type"] == "market":
                px = open_ * (1 + slip if buy else 1 - slip)
            elif o["type"] == "limit":
                lim = o["limit_price"]
                if buy and low <= lim:
                    px = min(open_, lim)
                elif not buy and high >= lim:
                    px = max(open_, lim)
            elif o["type"] == "stop":
                stp = o["stop_price"]
                if buy and high >= stp:
                    px = max(open_, stp) * (1 + slip)
                elif not buy and low <= stp:
                    px = min(open_, stp) * (1 - slip)
            if px is not None:
                self._fill(o, px)

    def _fill(self, o, px):
        qty, sym = o["qty"], o["symbol"]
        pos = self.state["positions"].setdefault(sym, {"qty": 0.0, "avg_entry_price": 0.0})
        if o["side"] == "buy":
            if qty * px > self.state["cash"] + 1e-6:
                o["status"] = "rejected"
                return
            pos["avg_entry_price"] = (pos["qty"] * pos["avg_entry_price"] + qty * px) / (pos["qty"] + qty)
            pos["qty"] += qty
            self.state["cash"] -= qty * px
        else:
            pos["qty"] -= qty
            self.state["cash"] += qty * px
        if pos["qty"] <= 1e-9:
            self.state["positions"].pop(sym, None)
        o.update(status="filled", filled_qty=qty, filled_avg_price=round(px, 4), filled_at=str(self._now()))
        for other in self.state["orders"]:
            if o["legs"] and other["id"] in o["legs"]:
                other["status"] = "new"                    # parent filled -> exit legs become live
            elif o["parent_id"] and other["parent_id"] == o["parent_id"] and other["id"] != o["id"] \
                    and other["status"] in OPEN_STATES:
                other["status"] = "canceled"               # one-cancels-other

    def _as_order(self, o: dict):
        legs = [self._as_order(self._find(i)) for i in o["legs"]] if o["legs"] else None
        fmt = lambda v: None if v is None else f"{float(v):.4f}".rstrip("0").rstrip(".")
        return SimpleNamespace(
            id=o["id"], client_order_id=o["client_order_id"], symbol=o["symbol"], qty=fmt(o["qty"]),
            filled_qty=fmt(o["filled_qty"]), filled_avg_price=fmt(o["filled_avg_price"]),
            side=OrderSide(o["side"]), order_type=OrderType(o["type"]), type=OrderType(o["type"]),
            order_class=OrderClass(o["order_class"]), time_in_force=TimeInForce(o["time_in_force"]),
            status=OrderStatus(o["status"]), limit_price=fmt(o["limit_price"]), stop_price=fmt(o["stop_price"]),
            submitted_at=o["submitted_at"], filled_at=o["filled_at"], legs=legs)

    def _find(self, order_id) -> dict:
        for o in self.state["orders"]:
            if o["id"] == str(order_id):
                return o
        raise SimAPIError(f"order not found: {order_id}")

    def get_order_by_id(self, order_id):
        return self._as_order(self._find(order_id))

    def get_order_by_client_id(self, client_id):
        """Look an order up by the id YOU chose (used for idempotent order submission)."""
        for o in self.state["orders"]:
            if o["client_order_id"] == str(client_id):
                return self._as_order(o)
        raise SimAPIError(f"order not found for client_order_id: {client_id}")

    def get_orders(self, filter=None):
        status = enum_str(getattr(filter, "status", None) or QueryOrderStatus.OPEN)
        symbols = getattr(filter, "symbols", None)
        limit = getattr(filter, "limit", None) or 50
        rows = [o for o in self.state["orders"] if o["parent_id"] is None]    # legs nest under parents
        if status == "open":
            rows = [o for o in rows if o["status"] in OPEN_STATES or
                    any(self._find(i)["status"] in OPEN_STATES for i in (o["legs"] or []))]
        elif status == "closed":
            rows = [o for o in rows if o["status"] not in OPEN_STATES]
        if symbols:
            rows = [o for o in rows if o["symbol"] in symbols]
        return [self._as_order(o) for o in reversed(rows)][:limit]

    def cancel_order_by_id(self, order_id):
        o = self._find(order_id)
        if o["status"] not in OPEN_STATES:
            raise SimAPIError(f"order is not cancelable (status={o['status']})")
        o["status"] = "canceled"
        for leg_id in o["legs"] or []:
            leg = self._find(leg_id)
            if leg["status"] in OPEN_STATES:
                leg["status"] = "canceled"
        self._save()

    def cancel_orders(self):
        open_ids = [o["id"] for o in self.state["orders"] if o["status"] in OPEN_STATES and not o["parent_id"]]
        open_ids += [o["id"] for o in self.state["orders"] if o["status"] in OPEN_STATES and o["parent_id"]]
        for oid in open_ids:
            if self._find(oid)["status"] in OPEN_STATES:
                self.cancel_order_by_id(oid)
        return [SimpleNamespace(id=i, status=200) for i in open_ids]

    # ---------- positions
    def _as_position(self, sym, p):
        px = self.latest_price(sym)
        mv, cost = p["qty"] * px, p["qty"] * p["avg_entry_price"]
        return SimpleNamespace(symbol=sym, qty=f"{p['qty']:g}", side="long", avg_entry_price=f"{p['avg_entry_price']:.4f}",
                               current_price=f"{px:.4f}", market_value=f"{mv:.2f}", cost_basis=f"{cost:.2f}",
                               unrealized_pl=f"{mv - cost:.2f}", unrealized_plpc=f"{(mv / cost - 1) if cost else 0:.6f}",
                               qty_available=f"{self._qty_available(sym):g}")

    def get_all_positions(self):
        return [self._as_position(s, p) for s, p in self.state["positions"].items()]

    def get_open_position(self, symbol_or_asset_id):
        p = self.state["positions"].get(symbol_or_asset_id)
        if not p:
            raise SimAPIError(f"position does not exist: {symbol_or_asset_id}")
        return self._as_position(symbol_or_asset_id, p)

    def close_position(self, symbol_or_asset_id, close_options=None):
        from alpaca.trading.requests import MarketOrderRequest
        pos = self.get_open_position(symbol_or_asset_id)
        qty = float(pos.qty)
        if close_options is not None and getattr(close_options, "percentage", None):
            qty = round(qty * float(close_options.percentage) / 100, 6)
        elif close_options is not None and getattr(close_options, "qty", None):
            qty = float(close_options.qty)
        return self.submit_order(MarketOrderRequest(symbol=symbol_or_asset_id, qty=qty,
                                                    side=OrderSide.SELL, time_in_force=TimeInForce.DAY))

    def close_all_positions(self, cancel_orders: bool = False):
        if cancel_orders:
            self.cancel_orders()
        return [self.close_position(s) for s in list(self.state["positions"])]


def get_broker(state_file: str = "sim_account.json", reset: bool = False,
               starting_cash: float = 100_000.0):
    """Alpaca paper TradingClient wrapper when keys are set, else the local simulator."""
    if is_online():
        return AlpacaPaperBroker()
    return PaperBrokerSim(state_file=state_file, starting_cash=starting_cash, reset=reset)
