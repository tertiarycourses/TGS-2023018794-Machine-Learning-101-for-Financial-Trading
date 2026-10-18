"""
pipeline/diagnose.py - Stage 18: automated bias checks before anything goes live.

For the configured strategy (or --strategy) and for the colleague's 'smoothed
momentum' exhibit (Lab18 buggy_backtest.py) the stage runs:

  1 look-ahead in FEATURES   truncation + future-shock test: values up to t must not change when the future does
  2 look-ahead in EXECUTION  same-bar returns (signal_t x return_t) vs next-bar fills
  3 cost drag                gross vs net CAGR, break-even cost vs assumed cost
  4 overfitting              in-sample Sharpe vs the best of N skill-free random strategies
                             (N = parameter sets tried), and in/out-of-sample decay
  5 survivorship/hindsight   universe chosen today; hindsight 'winners' basket vs SPY
and writes a PASS / WARN / FAIL table to _outputs/Lab18_diagnostics.csv.

    python -m pipeline diagnose
    python -m pipeline diagnose --strategy dip_buy
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
from common.backtest import COST_PRESETS, backtest, buy_and_hold
from common.config import output_path
from common.plotting import plt, save
from pipeline.backtest import break_even_bps
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.ingest import load_bars, load_closes
from pipeline.signals import SIGNALS, lookahead_test, next_bar_position, target_position

IS_END, OOS_START = "2021-12-31", "2022-01-01"


# ------------------------------------------------------------------ the exhibit (as submitted by a junior quant)
def buggy_signal(bars: pd.DataFrame) -> pd.Series:
    smooth = bars["close"].rolling(5, center=True).mean()      # centred window: uses t+1 and t+2
    return (smooth > smooth.shift(1)).astype(float)


def trailing_signal(bars: pd.DataFrame) -> pd.Series:
    smooth = bars["close"].rolling(5).mean()                   # the fix: past prices only
    return (smooth > smooth.shift(1)).astype(float)


def random_strategies(ret: pd.Series, n: int, seed: int = 1) -> pd.DataFrame:
    """n skill-free long/flat strategies (switch with 10% probability a day), traded next bar."""
    rng = np.random.default_rng(seed)
    state = (np.cumsum(rng.random((len(ret), n)) < 0.10, axis=0) % 2).astype(float)
    return pd.DataFrame(state, index=ret.index).shift(1).fillna(0).mul(ret, axis=0)


def status(ok: bool, warn: bool = False) -> str:
    return "PASS" if ok else ("WARN" if warn else "FAIL")


def run(strategy: str | None = None, trials: int | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    cfg = load_config()
    s = cfg["strategy"]
    name = strategy or s["name"]
    params = s["params"] if name == s["name"] else {}
    sym = s["symbol"]
    bars = load_bars(sym, cfg["data"]["start"], cfg["data"]["end"])
    costs = cost_model(cfg)
    daily = bars["close"].pct_change()
    rows = []

    def add(check, subject, st, evidence):
        rows.append({"check": check, "subject": subject, "status": st, "evidence": evidence})

    # 1 look-ahead in features
    bad = lookahead_test(name, bars, **params)
    add("1 look-ahead (features)", name, status(bad == 0), f"{bad} of 25 truncation / future-shock checks changed values up to t")
    bad_b = lookahead_test("exhibit", bars, fn=buggy_signal)
    add("1 look-ahead (features)", "exhibit", status(bad_b == 0), f"{bad_b} of 25 checks changed values up to t: rolling(center=True)")

    # 2 look-ahead in execution
    tgt = target_position(name, bars, **params)
    same_bar = (tgt * daily).fillna(0)
    nxt = backtest(bars, tgt).returns
    infl = M.sharpe_ratio(same_bar) - M.sharpe_ratio(nxt)
    add("2 look-ahead (execution)", name, "PASS",
        f"pipeline fills next bar; a same-bar backtest would show Sharpe {M.sharpe_ratio(same_bar):.2f} vs "
        f"{M.sharpe_ratio(nxt):.2f} ({infl:+.2f})")
    steps = {
        "0 As submitted (biased)": (buggy_signal(bars) * daily).fillna(0),
        "1 Trailing window, same bar": (trailing_signal(bars) * daily).fillna(0),
        "2 + next-bar execution": backtest(bars, trailing_signal(bars)).returns,
        "3 + realistic costs": backtest(bars, trailing_signal(bars), costs=COST_PRESETS["alpaca_retail"]).returns,
        f"{sym} buy & hold": buy_and_hold(bars, COST_PRESETS["alpaca_retail"]).returns,
    }
    fix = M.format_table({k: M.summary(v) for k, v in steps.items()}).loc[["CAGR", "Sharpe", "Max drawdown"]].T
    sr0, sr2 = M.sharpe_ratio(steps["0 As submitted (biased)"]), M.sharpe_ratio(steps["2 + next-bar execution"])
    add("2 look-ahead (execution)", "exhibit", "FAIL",
        f"signal_t x return_t: Sharpe {sr0:.2f} as submitted -> {sr2:.2f} once fixed and filled next bar")

    # 3 cost drag
    res = backtest(bars, tgt, costs=costs)
    cs = res.cost_summary()
    be = break_even_bps(bars, tgt)
    assumed = costs.spread_bps / 2 + costs.slippage_bps
    share = cs["cost_drag_cagr"] / cs["gross_cagr"] if cs["gross_cagr"] > 0 else 1.0
    add("3 cost drag", name, status(be >= 3 * assumed and share < 0.25, warn=be >= assumed),
        f"gross {cs['gross_cagr']:.2%} -> net {cs['net_cagr']:.2%} (drag {share:.0%} of gross); break-even "
        f"{be:.1f} bps vs assumed {assumed:.1f} bps one way")
    ex = backtest(bars, trailing_signal(bars), costs=costs).cost_summary()
    add("3 cost drag", "exhibit (fixed)", status(False, warn=ex["net_cagr"] > 0),
        f"{trailing_signal(bars).diff().abs().sum() / 8:.0f} position changes a year; net CAGR {ex['net_cagr']:.2%}")

    # 4 overfitting
    if trials is None:
        try:
            trials = len(pd.read_csv(output_path("Lab10_grid_results.csv")))
        except FileNotFoundError:
            trials = 76
    spy = daily.fillna(0)
    rnd = random_strategies(spy, 500)
    is_sh, oos_sh = rnd.loc[:IS_END].apply(M.sharpe_ratio), rnd.loc[OOS_START:].apply(M.sharpe_ratio)
    best = is_sh.idxmax()
    noise_max = is_sh.iloc[:trials].max()
    s_is, s_oos = M.sharpe_ratio(res.returns.loc[:IS_END]), M.sharpe_ratio(res.returns.loc[OOS_START:])
    add("4 overfitting", name, status(s_is > noise_max and s_oos > 0, warn=s_oos > 0),
        f"IS Sharpe {s_is:.2f} vs best of {trials} random strategies {noise_max:.2f}; OOS {s_oos:.2f} (decay {s_oos - s_is:+.2f})")
    add("4 overfitting", "500 random strategies", "INFO",
        f"best IS {is_sh[best]:.2f} -> OOS {oos_sh[best]:.2f}; median OOS {oos_sh.median():.2f}; "
        f"IS/OOS correlation {is_sh.corr(oos_sh):.2f}; {(is_sh > 1).mean():.0%} have IS Sharpe > 1")

    # 5 survivorship / hindsight
    closes = load_closes(["NVDA", "MSFT", "AAPL", "SPY"], cfg["data"]["start"], cfg["data"]["end"])
    r = closes.pct_change().fillna(0)
    basket = r[["NVDA", "MSFT", "AAPL"]].mean(axis=1)
    add("5 survivorship / hindsight", "universe", "WARN",
        f"{len(cfg['universe']['trade'])} symbols chosen in 2025 from listed names; a hindsight 'AI basket' "
        f"(NVDA, MSFT, AAPL) CAGR {M.cagr(basket):.2%} vs SPY {M.cagr(r['SPY']):.2%} - use a point-in-time universe")

    df = pd.DataFrame(rows)
    out(f"\nDiagnostics for {name} {params or SIGNALS[name][2]} on {sym} (and the Lab 18 exhibit):")
    for _, x in df.iterrows():
        out(f"  [{x.status:<4}] {x.check:<26} {x.subject:<22} {x.evidence}")
    out("\nThe exhibit fixed one problem at a time:")
    out("  " + fix.to_string().replace("\n", "\n  "))
    fails = df[(df.subject == name) & (df.status == "FAIL")]
    verdict = ("BLOCK - fix the FAIL items before paper or live trading" if len(fails) else
               "CLEAR for paper trading - review every WARN with the risk committee")
    out(f"\nVERDICT for {name}: {verdict}")
    path = output_path("Lab18_diagnostics.csv")
    df.to_csv(path, index=False)
    out(f"Diagnostics -> _outputs/{path.name}")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for k, v in steps.items():
        ax.plot(M.equity_curve(v), label=k, lw=1.2)
    ax.set_yscale("log")
    ax.set_title("Lab 18: the exhibit before and after removing each bias (log scale)")
    ax.legend()
    save(fig, "Lab18_bias_comparison.png")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.3))
    a1.scatter(is_sh, oos_sh, s=8, alpha=0.5, color="#1f4e79", label="random strategies")
    a1.scatter([is_sh[best]], [oos_sh[best]], color="#c0504d", s=60, label="'best' random")
    a1.scatter([s_is], [s_oos], color="#4f9a3b", s=80, marker="*", label=name)
    a1.axhline(0, color="black", lw=0.6)
    a1.set_xlabel("In-sample Sharpe 2018-2021")
    a1.set_ylabel("Out-of-sample Sharpe 2022-2025")
    a1.set_title("Overfitting: in-sample skill rarely persists")
    a1.legend()
    a2.plot(M.equity_curve(basket), label="Hindsight AI basket")
    a2.plot(M.equity_curve(r["SPY"]), label="SPY")
    a2.set_yscale("log")
    a2.set_title("Survivorship / hindsight: chosen after the fact")
    a2.legend()
    save(fig, "Lab18_overfitting.png")
    return {"strategy": name, "verdict": verdict, "checks": df.to_dict("records")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline diagnose", description="Stage 18 - automated bias checks")
    ap.add_argument("--strategy", default=None, choices=list(SIGNALS))
    ap.add_argument("--trials", type=int, default=None, help="parameter sets tried (default: Lab 10 grid size)")
    ap.add_argument("--strict", action="store_true", help="exit 1 if the strategy has a FAIL")
    a = ap.parse_args(argv)
    stage_banner(18, "diagnostics: look-ahead, cost drag, overfitting, survivorship")
    res = run(a.strategy, a.trials)
    return 1 if a.strict and res["verdict"].startswith("BLOCK") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
