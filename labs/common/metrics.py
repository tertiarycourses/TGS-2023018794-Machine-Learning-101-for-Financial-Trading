"""
metrics.py - performance and risk metrics for daily strategy returns.

Inputs are simple daily returns (e.g. 0.01 = +1 %) indexed by date. All
annualised figures assume 252 trading days. Each function's docstring gives the
formula so learners can reproduce it in Excel.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def equity_curve(returns: pd.Series, start_value: float = 1.0) -> pd.Series:
    """Equity_t = start_value * prod(1 + r_1 .. r_t)."""
    return start_value * (1.0 + returns.fillna(0.0)).cumprod()


def total_return(returns: pd.Series) -> float:
    """Total return = prod(1 + r_t) - 1."""
    return float((1.0 + returns.fillna(0.0)).prod() - 1.0)


def cagr(returns: pd.Series) -> float:
    """Compound annual growth rate = (1 + total return) ** (252 / N) - 1, N = number of days."""
    n = returns.dropna().shape[0]
    if n == 0:
        return float("nan")
    return float((1.0 + total_return(returns)) ** (TRADING_DAYS / n) - 1.0)


def annual_volatility(returns: pd.Series) -> float:
    """Annualised volatility = stdev(daily r) * sqrt(252)."""
    return float(returns.dropna().std(ddof=1) * np.sqrt(TRADING_DAYS))


def sharpe_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Sharpe = mean(r - rf_daily) / stdev(r - rf_daily) * sqrt(252); rf_daily = rf / 252."""
    excess = returns.dropna() - risk_free / TRADING_DAYS
    sd = excess.std(ddof=1)
    return float(excess.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def sortino_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Sortino = mean(r - rf_daily) / downside deviation * sqrt(252).

    Downside deviation = sqrt(mean(min(r - rf_daily, 0) ** 2)) - only losses count as risk."""
    excess = returns.dropna() - risk_free / TRADING_DAYS
    downside = np.sqrt((np.minimum(excess, 0.0) ** 2).mean())
    return float(excess.mean() / downside * np.sqrt(TRADING_DAYS)) if downside > 0 else float("nan")


def drawdown_series(returns: pd.Series) -> pd.Series:
    """Drawdown_t = Equity_t / running max(Equity) - 1   (0 at a new high, negative below)."""
    eq = equity_curve(returns)
    return eq / eq.cummax() - 1.0


def max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown = min over t of Drawdown_t (worst peak-to-trough loss, negative)."""
    return float(drawdown_series(returns).min())


def calmar_ratio(returns: pd.Series) -> float:
    """Calmar = CAGR / |max drawdown|."""
    mdd = max_drawdown(returns)
    return float(cagr(returns) / abs(mdd)) if mdd < 0 else float("nan")


def win_rate(trade_returns: pd.Series) -> float:
    """Win rate = number of winning trades / number of trades."""
    t = pd.Series(trade_returns).dropna()
    return float((t > 0).mean()) if len(t) else float("nan")


def profit_factor(trade_returns: pd.Series) -> float:
    """Profit factor = sum of winning trade returns / |sum of losing trade returns|."""
    t = pd.Series(trade_returns).dropna()
    losses = -t[t < 0].sum()
    return float(t[t > 0].sum() / losses) if losses > 0 else float("nan")


def expectancy(trade_returns: pd.Series) -> float:
    """Expectancy per trade = win rate * avg win - loss rate * |avg loss| (= mean trade return)."""
    t = pd.Series(trade_returns).dropna()
    if not len(t):
        return float("nan")
    wins, losses = t[t > 0], t[t <= 0]
    p = len(wins) / len(t)
    avg_win = wins.mean() if len(wins) else 0.0
    avg_loss = abs(losses.mean()) if len(losses) else 0.0
    return float(p * avg_win - (1 - p) * avg_loss)


def exposure(position: pd.Series) -> float:
    """Exposure = share of days with a non-zero position (time in the market)."""
    return float((position.fillna(0.0) != 0).mean())


def turnover(position: pd.Series) -> float:
    """Annualised turnover = sum(|position_t - position_t-1|) * 252 / N  (1.0 = one full in-or-out)."""
    pos = position.fillna(0.0)
    return float(pos.diff().abs().fillna(pos.abs()).sum() * TRADING_DAYS / max(len(pos), 1))


def alpha_beta(returns: pd.Series, benchmark: pd.Series) -> tuple[float, float]:
    """CAPM regression r_t = a + b * m_t + e_t on daily returns.

    beta  = cov(r, m) / var(m)
    alpha = a * 252 (annualised intercept)."""
    joined = pd.concat([returns, benchmark], axis=1).dropna()
    if len(joined) < 2:
        return float("nan"), float("nan")
    r, m = joined.iloc[:, 0], joined.iloc[:, 1]
    beta = r.cov(m) / m.var()
    alpha = (r.mean() - beta * m.mean()) * TRADING_DAYS
    return float(alpha), float(beta)


METRIC_DEFINITIONS = {
    "Total return": "prod(1 + r) - 1",
    "CAGR": "(1 + total return)^(252/N) - 1",
    "Ann. volatility": "stdev(r) x sqrt(252)",
    "Sharpe": "mean(r - rf) / stdev(r - rf) x sqrt(252)",
    "Sortino": "mean(r - rf) / downside deviation x sqrt(252)",
    "Max drawdown": "worst peak-to-trough fall of equity",
    "Calmar": "CAGR / |max drawdown|",
    "Win rate": "winning trades / all trades",
    "Profit factor": "gross profit / gross loss (per trade)",
    "Expectancy": "average return per trade",
    "Exposure": "share of days holding a position",
    "Turnover": "annual sum of |change in position|",
    "Alpha": "annualised CAPM intercept vs benchmark",
    "Beta": "cov(r, benchmark) / var(benchmark)",
}


def summary(returns: pd.Series, position: pd.Series | None = None,
            trade_returns: pd.Series | None = None,
            benchmark: pd.Series | None = None) -> dict:
    """All metrics in one dict (NaN where the needed input is missing)."""
    out = {
        "Total return": total_return(returns),
        "CAGR": cagr(returns),
        "Ann. volatility": annual_volatility(returns),
        "Sharpe": sharpe_ratio(returns),
        "Sortino": sortino_ratio(returns),
        "Max drawdown": max_drawdown(returns),
        "Calmar": calmar_ratio(returns),
    }
    t = trade_returns if trade_returns is not None else pd.Series(dtype=float)
    out.update({"Win rate": win_rate(t), "Profit factor": profit_factor(t),
                "Expectancy": expectancy(t), "Trades": int(pd.Series(t).dropna().shape[0])})
    pos = position if position is not None else pd.Series(1.0, index=returns.index)
    out.update({"Exposure": exposure(pos), "Turnover": turnover(pos)})
    if benchmark is not None:
        out["Alpha"], out["Beta"] = alpha_beta(returns, benchmark)
    return out


PERCENT_KEYS = {"Total return", "CAGR", "Ann. volatility", "Max drawdown", "Win rate",
                "Expectancy", "Exposure", "Alpha"}


def format_table(rows: dict[str, dict]) -> pd.DataFrame:
    """Turn {'Strategy': summary_dict, ...} into a printable, formatted DataFrame."""
    df = pd.DataFrame(rows)
    fmt = df.copy().astype(object)
    for key in df.index:
        for col in df.columns:
            v = df.loc[key, col]
            if pd.isna(v):
                fmt.loc[key, col] = "-"
            elif key in PERCENT_KEYS:
                fmt.loc[key, col] = f"{v:.2%}"
            elif key == "Trades":
                fmt.loc[key, col] = f"{int(v)}"
            else:
                fmt.loc[key, col] = f"{v:.2f}"
    return fmt
