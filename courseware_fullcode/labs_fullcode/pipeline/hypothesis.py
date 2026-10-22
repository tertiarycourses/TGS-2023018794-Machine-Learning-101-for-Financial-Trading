"""
pipeline/hypothesis.py - Stage 04: `python -m pipeline hypothesis --card <card.yaml>`

Turns a written hypothesis card into an automated statistical test so that no
idea reaches the signal and backtest stages without evidence:

  1. build the signal condition from the card (known at the close of day t)
  2. measure the OUTCOME: the forward return from close t to close t + horizon
  3. compare signal days with all other days: means, hit rates, Welch t-test,
     bootstrap 95% CI of the signal-day mean
  4. apply the card's decision rule (p < alpha AND effect > estimated cost)
  5. robustness grid over other parameters and symbols
  6. write the card + result to _outputs/Lab04_hypothesis_result.yaml
"""
from __future__ import annotations

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import stats

from common.config import output_path
from common.indicators import rsi, sma
from common.plotting import plt, save
from pipeline.config import PIPELINE_DIR, load_config, stage_banner
from pipeline.ingest import load_bars

DEFAULT_CARD = PIPELINE_DIR / "hypotheses" / "spy_dip_after_streak.yaml"


def losing_streak(close: pd.Series) -> pd.Series:
    """Number of consecutive down closes ending at each day (0 if today was up)."""
    down = close.diff() < 0
    return down.groupby((~down).cumsum()).cumsum().astype(int)


def condition(bars: pd.DataFrame, signal: dict) -> pd.Series:
    """Boolean signal from the card - every type uses data up to the close of day t only."""
    c = bars["close"]
    kind = signal["type"]
    if kind == "losing_streak":
        return losing_streak(c) >= int(signal["n"])
    if kind == "rsi_below":
        return rsi(c, int(signal.get("window", 2))) < float(signal["level"])
    if kind == "close_below_sma":
        return c < sma(c, int(signal["window"]))
    raise ValueError(f"unknown signal type {kind}")


def test_card(bars: pd.DataFrame, card: dict, signal: dict | None = None) -> dict:
    signal = signal or card["signal"]
    h = int(card["outcome"].get("horizon_days", 1))
    fwd = bars["close"].shift(-h) / bars["close"] - 1.0             # the OUTCOME (future), never a feature
    df = pd.DataFrame({"on": condition(bars, signal), "fwd": fwd}).dropna()
    sig, oth, allr = df.loc[df["on"], "fwd"], df.loc[~df["on"], "fwd"], df["fwd"]
    t, p = stats.ttest_ind(sig, oth, equal_var=False)
    rng = np.random.default_rng(int(card["test"].get("seed", 42)))
    boot = [rng.choice(sig.values, len(sig)).mean() for _ in range(int(card["test"].get("bootstrap", 5000)))]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    rule = card["decision_rule"]
    edge_bps = (sig.mean() - oth.mean()) * 1e4
    supported = (p < rule["alpha"] and (t > 0 or not rule.get("require_positive_effect", True))
                 and edge_bps >= rule.get("min_edge_bps", 0))
    return {"n_days": int(len(df)), "signal_days": int(len(sig)), "share": float(len(sig) / len(df)),
            "mean_signal": float(sig.mean()), "mean_other": float(oth.mean()), "mean_all": float(allr.mean()),
            "hit_signal": float((sig > 0).mean()), "hit_all": float((allr > 0).mean()),
            "ci95": [float(lo), float(hi)], "welch_t": float(t), "p_value": float(p),
            "edge_bps": float(edge_bps), "supported": bool(supported), "first": str(df.index[0].date()),
            "last": str(df.index[-1].date()), "_frame": df}


def run(card_path: Path | None = None, quiet: bool = False) -> dict:
    out = print if not quiet else (lambda *a, **k: None)
    load_config()
    card_path = Path(card_path or DEFAULT_CARD)
    card = yaml.safe_load(card_path.read_text())
    sym = card["instrument"]
    bars = load_bars(sym, card["sample"]["start"], card["sample"]["end"])
    res = test_card(bars, card)
    out(f"\nCard {card['id']}: {card['name']}  ({card_path.name})")
    out(f"  H1: {card['h1']}\n  H0: {card['h0']}")
    out(f"  Sample {res['first']} to {res['last']} ({res['n_days']} days) | signal {card['signal']} | "
        f"outcome: {card['outcome']['horizon_days']}-day forward return")
    out(f"  Signal days                     : {res['signal_days']:5d}  ({res['share']:.1%} of days)")
    out(f"  Mean forward return | signal    : {res['mean_signal']:+.4%}")
    out(f"  Mean forward return | other     : {res['mean_other']:+.4%}")
    out(f"  Unconditional mean (all days)   : {res['mean_all']:+.4%}")
    out(f"  Hit rate | signal vs all        : {res['hit_signal']:.1%} vs {res['hit_all']:.1%}")
    out(f"  95% bootstrap CI (signal mean)  : [{res['ci95'][0]:+.4%}, {res['ci95'][1]:+.4%}]")
    out(f"  Welch t-test signal vs other    : t = {res['welch_t']:.2f}, p = {res['p_value']:.3f}")
    rule = card["decision_rule"]
    out(f"  Edge vs other days              : {res['edge_bps']:+.1f} bps (rule: p < {rule['alpha']} and edge >= "
        f"{rule['min_edge_bps']} bps)")
    verdict = ("SUPPORTED - reject H0; promote the idea to the signal and backtest stages" if res["supported"]
               else "NOT SUPPORTED - do not reject H0; do not spend backtest time on it yet")
    out(f"  DECISION: {verdict}")

    rob = []
    for s in [sym] + [x for x in card["robustness"].get("symbols", []) if x != sym]:
        b = bars if s == sym else load_bars(s, card["sample"]["start"], card["sample"]["end"])
        for n in card["robustness"].get("streaks", [card["signal"].get("n")]):
            r = test_card(b, card, {**card["signal"], "n": n})
            rob.append({"symbol": s, "n": n, "signal_days": r["signal_days"], "edge_bps": round(r["edge_bps"], 1),
                        "t": round(r["welch_t"], 2), "p": round(r["p_value"], 3),
                        "decision": "supported" if r["supported"] else "not supported"})
    rob_df = pd.DataFrame(rob)
    out("\nRobustness grid (same card, other parameters and symbols):")
    out(rob_df.to_string(index=False))
    out(f"  -> {int((rob_df.decision == 'supported').sum())} of {len(rob_df)} variants supported. "
        f"Count every variant you try: {len(rob_df)} tests at alpha {rule['alpha']} -> Bonferroni p < "
        f"{rule['alpha'] / len(rob_df):.4f}")

    df = res.pop("_frame")
    streak = losing_streak(bars["close"]).reindex(df.index)
    table = df.groupby(streak.clip(upper=5))["fwd"].agg(["count", "mean", "sem"])
    table.index = [f"{i}" if i < 5 else "5+" for i in table.index]
    out("\nForward return by losing-streak length (the shape of the effect):")
    out(table.assign(mean=lambda x: x["mean"] * 100, sem=lambda x: x["sem"] * 100)
        .rename(columns={"mean": "mean %", "sem": "std err %"}).round(3).to_string())
    n = int(card["signal"].get("n", 3))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(table.index, table["mean"] * 100, yerr=1.96 * table["sem"] * 100, capsize=4,
           color=["#7f7f7f"] * n + ["#1f4e79"] * (len(table) - n))
    ax.axhline(res["mean_all"] * 100, color="#c0504d", ls="--", label="Unconditional mean")
    ax.set_xlabel("Consecutive down closes before the signal day")
    ax.set_ylabel("Mean next-day return % (95% CI)")
    ax.set_title(f"{card['id']} {sym}: {verdict.split(' - ')[0]} (p = {res['p_value']:.3f})")
    ax.legend()
    save(fig, "Lab04_hypothesis.png")

    result = {"card": card, "result": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in res.items()},
              "decision": verdict, "robustness": rob}
    path = output_path("Lab04_hypothesis_result.yaml")
    path.write_text(yaml.safe_dump(result, sort_keys=False))
    out(f"Result card -> _outputs/{path.name}")
    return {**res, "decision": verdict, "robustness": rob}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline hypothesis", description="Stage 04 - hypothesis test")
    ap.add_argument("--card", default=None, help="path to a hypothesis card YAML")
    a = ap.parse_args(argv)
    stage_banner(4, "hypothesis card -> automated statistical test")
    run(Path(a.card) if a.card else None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
