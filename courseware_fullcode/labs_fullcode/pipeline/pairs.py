"""
pipeline/pairs.py - Stage 14: a hedged, market-neutral statistical-arbitrage sleeve.

Engle-Granger two-step method, decided on the FORMATION period only:
  1. OLS  log(A) = a + beta * log(B) + e        -> beta = hedge ratio
  2. ADF unit-root test on the residual e        -> stationary = cointegrated pair
Trading period (out of sample, beta held fixed):
  z = (spread - rolling mean) / rolling std
  short spread (short A, long beta x B) when z > +entry; long spread when z < -entry;
  exit when |z| < exit; positions act on the NEXT bar; both legs pay costs.

The stage outputs per-leg TARGET weights for the latest bar. Executing the short
leg needs a margin account with shorting enabled; the desk's automation stages
are long-only (risk.long_only), so this sleeve stays a research/paper sleeve.

    python -m pipeline pairs
    python -m pipeline pairs --pair JPM BAC --entry 1.5 --exit 0
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys

import numpy as np
import pandas as pd

from common import metrics as M
from common.plotting import plt, save
from pipeline.config import load_config, stage_banner
from pipeline.ingest import load_closes

FORMATION = ("2018-01-01", "2022-12-31")
TRADING = ("2023-01-01", "2025-12-31")
EG_CRIT = {"1%": -3.90, "5%": -3.34, "10%": -3.04}      # Engle-Granger, 2 variables with constant (MacKinnon)


def ols(y: np.ndarray, X: np.ndarray):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    sigma2 = resid @ resid / (len(y) - X.shape[1])
    return coef, np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X))), resid


def adf_t(series: pd.Series, lags: int = 1) -> float:
    """ADF t-statistic: d e_t = g * e_(t-1) + sum phi_k * d e_(t-k)."""
    e = series.values
    de = np.diff(e)
    X = np.column_stack([e[lags:-1]] + [de[lags - k:-k] for k in range(1, lags + 1)])
    coef, se, _ = ols(de[lags:], X)
    return coef[0] / se[0]


def engle_granger(log_a: pd.Series, log_b: pd.Series):
    coef, _, resid = ols(log_a.values, np.column_stack([np.ones(len(log_b)), log_b.values]))
    return coef[0], coef[1], adf_t(pd.Series(resid, index=log_a.index))


def half_life(spread: pd.Series) -> float:
    lag, d = spread.shift(1).dropna(), spread.diff().dropna()
    k = np.polyfit(lag.loc[d.index], d, 1)[0]
    return float(-np.log(2) / k) if k < 0 else float("inf")


def trade_pair(closes, a, b, alpha, beta, entry, exit_, window, cost_bps):
    """Spread z-score state machine; returns spread, z, held position, gross and net daily returns."""
    spread = np.log(closes[a]) - beta * np.log(closes[b]) - alpha
    z = (spread - spread.rolling(window).mean()) / spread.rolling(window).std()
    pos, state = pd.Series(0.0, index=z.index), 0.0      # +1 = long spread (long A, short B)
    for t, zt in z.items():
        if np.isnan(zt):
            continue
        if state == 0 and zt > entry:
            state = -1.0
        elif state == 0 and zt < -entry:
            state = 1.0
        elif state != 0 and abs(zt) < exit_:
            state = 0.0
        pos[t] = state
    held = pos.shift(1).fillna(0.0)                       # decided at close t, held over t+1
    w = 1.0 / (1.0 + abs(beta))                           # gross exposure 1 across both legs
    gross = held * w * (closes[a].pct_change() - beta * closes[b].pct_change())
    legs_traded = held.diff().abs().fillna(held.abs()) * w * (1 + abs(beta))
    net = gross - legs_traded * cost_bps / 10_000
    return spread, z, held, pos, gross.fillna(0.0), net.fillna(0.0)


def leg_targets(state: float, a: str, b: str, beta: float) -> dict[str, float]:
    """Target weights per leg for a spread position (gross exposure 1)."""
    w = 1.0 / (1.0 + abs(beta))
    return {a: float(round(state * w, 4)) + 0.0, b: float(round(-state * beta * w, 4)) + 0.0}


def run(pair=("KO", "PEP"), entry: float = 2.0, exit_: float = 0.5, window: int = 60, cost_bps: float = 5.0,
        quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *x, **k: None)
    cfg = load_config()
    candidates = [tuple(p) for p in cfg["universe"]["pairs"]]
    symbols = sorted({s for p in candidates + [tuple(pair)] for s in p} | {"SPY"})
    closes = load_closes(symbols, FORMATION[0], TRADING[1])
    form = closes.loc[FORMATION[0]:FORMATION[1]]
    out(f"\n[1] Pair screen on the formation period {FORMATION[0]} to {FORMATION[1]} (Engle-Granger, 5% critical "
        f"value {EG_CRIT['5%']}):")
    out(f"  {'Pair':<10}{'corr(returns)':>14}{'beta':>8}{'ADF t':>9}  cointegrated at 5%?")
    screen = []
    for x, y in candidates:
        corr = form[x].pct_change().corr(form[y].pct_change())
        _, bc, t = engle_granger(np.log(form[x]), np.log(form[y]))
        screen.append({"pair": f"{x}/{y}", "corr": round(corr, 2), "beta": round(bc, 2), "adf_t": round(t, 2),
                       "cointegrated": bool(t < EG_CRIT["5%"])})
        out(f"  {x + '/' + y:<10}{corr:>14.2f}{bc:>8.2f}{t:>9.2f}  {'YES' if t < EG_CRIT['5%'] else 'no'}")
    out("  High correlation does not imply cointegration; screening many pairs inflates false positives.")

    a, b = pair
    alpha, beta, t = engle_granger(np.log(form[a]), np.log(form[b]))
    hl = half_life(np.log(form[a]) - beta * np.log(form[b]) - alpha)
    out(f"\n[2] Chosen pair {a}/{b}: hedge ratio beta = {beta:.3f} (short {beta:.2f} of {b} per 1 of {a}), "
        f"ADF t = {t:.2f}, half-life = {hl:.0f} days" + ("" if t < EG_CRIT["5%"] else "  WARNING: NOT cointegrated"))
    trade = closes.loc[TRADING[0]:TRADING[1]]
    hist = closes.loc[pd.Timestamp(TRADING[0]) - pd.Timedelta(days=120):TRADING[1]]
    spread, z, held, state, gross, net = trade_pair(hist, a, b, alpha, beta, entry, exit_, window, cost_bps)
    idx = trade.index
    held, gross, net, z = held.loc[idx], gross.loc[idx], net.loc[idx], z.loc[idx]
    spy = trade["SPY"].pct_change().fillna(0.0)
    entries = int(((held != 0) & (held.shift(1).fillna(0) == 0)).sum())
    _, beta_mkt = M.alpha_beta(net, spy)
    out(f"\n[3] Out-of-sample {TRADING[0]} to {TRADING[1]} (entry |z| > {entry}, exit |z| < {exit_}, {window}-day z, "
        f"{cost_bps:g} bps per leg per side):")
    out(f"  {'':<22}{'Return':>9}{'CAGR':>8}{'Vol':>8}{'Sharpe':>8}{'MaxDD':>8}")
    for name, r in [("Pairs (gross)", gross), ("Pairs (net of costs)", net), ("SPY buy and hold", spy)]:
        out(f"  {name:<22}{M.total_return(r):>9.1%}{M.cagr(r):>8.1%}{M.annual_volatility(r):>8.1%}"
            f"{M.sharpe_ratio(r):>8.2f}{M.max_drawdown(r):>8.1%}")
    out(f"  Trades opened: {entries} | time in market: {M.exposure(held):.0%} | beta to SPY: {beta_mkt:+.2f} | "
        f"correlation to SPY: {net.corr(spy):+.2f}")
    latest = float(state.loc[idx].iloc[-1])
    legs = leg_targets(latest, a, b, beta)
    out(f"\n[4] Latest spread z {z.iloc[-1]:+.2f} -> spread position {latest:+.0f} -> leg targets {legs}")
    out("  Market-neutral check: beta near 0 confirms the hedge. Short legs need a margin account; the automation "
        "stages are long-only, so this sleeve stays on paper.")

    fig, ax = plt.subplots(3, 1, figsize=(10, 8.5), sharex=True, gridspec_kw={"height_ratios": [1.2, 1, 1]})
    (trade[a] / trade[a].iloc[0]).plot(ax=ax[0], label=a)
    (trade[b] / trade[b].iloc[0]).plot(ax=ax[0], label=b)
    ax[0].set_title(f"{a} and {b}, normalised (trading period)")
    ax[0].legend()
    z.plot(ax=ax[1], color="#1f4e79", lw=0.9, label="spread z-score")
    for lvl, c in [(entry, "#c0504d"), (-entry, "#c0504d"), (exit_, "#7f7f7f"), (-exit_, "#7f7f7f")]:
        ax[1].axhline(lvl, color=c, ls="--", lw=0.8)
    ax[1].fill_between(z.index, -4, 4, where=held != 0, color="#e2a400", alpha=0.15, label="position open")
    ax[1].set_ylim(-4, 4)
    ax[1].set_title(f"Spread z-score with entry (+/-{entry:g}) and exit (+/-{exit_:g}) bands")
    ax[1].legend(loc="upper left")
    M.equity_curve(net).plot(ax=ax[2], label="pairs, net of costs")
    M.equity_curve(spy).plot(ax=ax[2], label="SPY buy and hold", alpha=0.7)
    ax[2].set_title(f"Growth of 1: hedged pair versus the market (beta {beta_mkt:+.2f})")
    ax[2].legend()
    save(fig, "Lab14_pairs_trading.png")
    return {"screen": screen, "beta": float(beta), "adf_t": float(t), "half_life": hl, "trades": entries,
            "net_return": float(M.total_return(net)), "beta_spy": float(beta_mkt), "legs": legs}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline pairs", description="Stage 14 - pairs / stat-arb")
    ap.add_argument("--pair", nargs=2, default=["KO", "PEP"])
    ap.add_argument("--entry", type=float, default=2.0)
    ap.add_argument("--exit", type=float, default=0.5)
    ap.add_argument("--window", type=int, default=60)
    ap.add_argument("--cost-bps", type=float, default=5.0, help="cost per leg per side")
    x = ap.parse_args(argv)
    stage_banner(14, "pairs trading: hedged statistical arbitrage")
    run(tuple(s.upper() for s in x.pair), x.entry, x.exit, x.window, x.cost_bps)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
