"""
pipeline/abtest.py - Stage 13: A/B test two strategy variants before moving capital.

Both variants are run on the SAME days with the SAME costs, then:
  1. Welch t-test on daily returns            (treats the samples as independent)
  2. paired t-test on the daily difference A-B (same days -> paired design)
  3. block-bootstrap 95% CI of Sharpe(A) - Sharpe(B) (keeps autocorrelation, no normality)
  4. DECISION: reject H0 only if the paired test AND the Sharpe CI agree
  5. multiple-testing caution (Bonferroni) for the number of variants tried

    python -m pipeline abtest --a trend_filter --b dip_buy --alpha 0.05
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys

import numpy as np
import yaml
from scipy import stats

from common import metrics as M
from common.backtest import backtest
from common.config import output_path
from common.plotting import plt, save
from pipeline.config import cost_model, load_config, stage_banner
from pipeline.indicators import ta_sma
from pipeline.ingest import load_bars
from pipeline.signals import SIGNALS, target_position


def block_bootstrap_sharpe_diff(a, b, n_boot: int = 2000, block: int = 21, seed: int = 7) -> np.ndarray:
    """Resample blocks of consecutive days and recompute Sharpe(A) - Sharpe(B)."""
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a), np.asarray(b)
    n, need, out = len(a), int(np.ceil(len(a) / block)), []
    for _ in range(n_boot):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.integers(0, n - block, need)])[:n]
        out.append(a[idx].mean() / a[idx].std() * np.sqrt(252) - b[idx].mean() / b[idx].std() * np.sqrt(252))
    return np.array(out)


def ab_test(ra, rb, alpha: float = 0.05, tried: int = 20) -> dict:
    t_w, p_w = stats.ttest_ind(ra, rb, equal_var=False)
    t_p, p_p = stats.ttest_rel(ra, rb)
    boot = block_bootstrap_sharpe_diff(ra, rb)
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    diff = M.sharpe_ratio(ra) - M.sharpe_ratio(rb)
    reject = bool(p_p < alpha and not (lo <= 0 <= hi))
    return {"welch_t": float(t_w), "welch_p": float(p_w), "paired_t": float(t_p), "paired_p": float(p_p),
            "mean_diff_daily": float((ra - rb).mean()), "sharpe_diff": float(diff), "ci": [float(lo), float(hi)],
            "share_a_beats_b": float((boot > 0).mean()), "reject_h0": reject, "bonferroni_p": alpha / tried, "_boot": boot}


def run(a: str = "trend_filter", b: str = "dip_buy", alpha: float = 0.05, tried: int = 20, symbol: str = "SPY",
        quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *x, **k: None)
    cfg = load_config()
    bars = load_bars(symbol, cfg["data"]["start"], cfg["data"]["end"])
    costs = cost_model(cfg)
    res_a, res_b = (backtest(bars, target_position(n, bars), costs=costs) for n in (a, b))
    start = ta_sma(bars["close"], 200).first_valid_index()             # same window for both variants
    ra, rb = res_a.returns.loc[start:], res_b.returns.loc[start:]
    la, lb = f"A: {a}", f"B: {b}"
    table = M.format_table({la: M.summary(ra, res_a.position.loc[start:], res_a.trades["net_return"]),
                            lb: M.summary(rb, res_b.position.loc[start:], res_b.trades["net_return"])})
    out(f"\n{symbol} {start.date()} to {ra.index[-1].date()} ({len(ra)} days), costs {costs.name}")
    out(table.loc[["CAGR", "Ann. volatility", "Sharpe", "Max drawdown", "Exposure", "Trades"]].to_string())
    r = ab_test(ra, rb, alpha, tried)
    out(f"\nH0: {a} and {b} have the same expected daily return and Sharpe  |  alpha = {alpha}")
    out(f"  1. Welch t-test (independent)  : t = {r['welch_t']:5.2f}, p = {r['welch_p']:.3f}")
    out(f"  2. Paired t-test on A - B      : t = {r['paired_t']:5.2f}, p = {r['paired_p']:.3f} "
        f"(mean diff {r['mean_diff_daily']:.5f}/day)")
    out(f"  3. Sharpe difference A - B     : {r['sharpe_diff']:+.2f}, {1 - alpha:.0%} block-bootstrap CI "
        f"[{r['ci'][0]:+.2f}, {r['ci'][1]:+.2f}]; A beats B in {r['share_a_beats_b']:.0%} of samples")
    winner = a if r["sharpe_diff"] > 0 else b
    decision = (f"REJECT H0 - {winner} is better on the paired test and the Sharpe CI; allocate to {winner}"
                if r["reject_h0"] else
                f"DO NOT REJECT H0 - {winner} looks better on paper, but the evidence is not reliable; keep both on paper")
    out(f"\nDECISION: {decision}")
    out(f"  Multiple testing: with {tried} variants tried, Bonferroni requires p < {r['bonferroni_p']:.4f}")
    boot = r.pop("_boot")
    path = output_path("Lab13_abtest_decision.yaml")
    path.write_text(yaml.safe_dump({"a": a, "b": b, "alpha": alpha, "window": [str(start.date()), str(ra.index[-1].date())],
                                    **{k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()},
                                    "decision": decision}, sort_keys=False))
    out(f"  Decision record -> _outputs/{path.name}")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))
    for name, rr in [(la, ra), (lb, rb)]:
        ax1.plot(M.equity_curve(rr), label=name)
    ax1.set_title("Variant A vs Variant B (net of costs)")
    ax1.legend()
    ax2.hist(boot, bins=60, color="#1f4e79", alpha=0.8)
    ax2.axvline(0, color="black", lw=1)
    ax2.axvline(r["ci"][0], color="#c0504d", ls="--", label=f"{1 - alpha:.0%} CI")
    ax2.axvline(r["ci"][1], color="#c0504d", ls="--")
    ax2.set_title("Bootstrap distribution of Sharpe(A) - Sharpe(B)")
    ax2.legend()
    save(fig, "Lab13_ab_test.png")
    return {**r, "decision": decision}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline abtest", description="Stage 13 - A/B test")
    ap.add_argument("--a", default="trend_filter", choices=list(SIGNALS))
    ap.add_argument("--b", default="dip_buy", choices=list(SIGNALS))
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--tried", type=int, default=20, help="number of variants tried (for the Bonferroni caution)")
    ap.add_argument("--symbol", default="SPY")
    x = ap.parse_args(argv)
    stage_banner(13, "A/B test: Welch, paired, bootstrap -> decision")
    run(x.a, x.b, x.alpha, x.tried, x.symbol.upper())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
