"""
plotting.py - consistent matplotlib charts saved to labs/_outputs/.

Uses the non-interactive 'Agg' backend so scripts run the same on a laptop,
a server or in class without a display.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from common.config import output_path  # noqa: E402

PALETTE = ["#1f4e79", "#c0504d", "#4f9a3b", "#e2a400", "#7f5fa8", "#2aa1b3", "#7f7f7f"]
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.prop_cycle": matplotlib.cycler(color=PALETTE), "font.size": 9})


def save(fig, filename: str) -> str:
    """Save a figure into _outputs/, close it, and return the path as a string."""
    path = output_path(filename)
    if fig.get_layout_engine() is None:
        fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] saved {path.relative_to(path.parent.parent)}")
    return str(path)


def plot_equity_and_drawdown(curves: dict[str, pd.Series], title: str, filename: str) -> str:
    """Top: equity curves (growth of $1). Bottom: drawdown of each curve."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1.3]})
    for name, eq in curves.items():
        norm = eq / eq.iloc[0]
        ax1.plot(norm.index, norm, label=name, lw=1.4)
        ax2.plot(norm.index, (norm / norm.cummax() - 1) * 100, lw=1.0)
    ax1.set_title(title)
    ax1.set_ylabel("Growth of $1")
    ax1.legend(loc="upper left")
    ax2.set_ylabel("Drawdown %")
    return save(fig, filename)


def plot_price_signals(close: pd.Series, entries: pd.Series, exits: pd.Series, title: str,
                       filename: str, overlays: dict[str, pd.Series] | None = None) -> str:
    """Price with optional overlay lines and buy (^) / sell (v) markers."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(close.index, close, color="#333333", lw=1.0, label="Close")
    for name, s in (overlays or {}).items():
        ax.plot(s.index, s, lw=1.1, label=name)
    ax.scatter(close.index[entries.astype(bool)], close[entries.astype(bool)], marker="^",
               color="#4f9a3b", s=40, label="Buy", zorder=3)
    ax.scatter(close.index[exits.astype(bool)], close[exits.astype(bool)], marker="v",
               color="#c0504d", s=40, label="Sell", zorder=3)
    ax.set_title(title)
    ax.legend(loc="upper left")
    return save(fig, filename)
