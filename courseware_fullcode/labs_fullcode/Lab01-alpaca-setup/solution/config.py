"""
pipeline/config.py - Stage 01: load and validate pipeline/config.yaml.

Every other stage calls load_config() instead of hard-coding symbols, dates,
strategy parameters, risk limits or costs. Secrets are NEVER read from the YAML:
the YAML only names the environment variables that hold them.

    from pipeline.config import load_config
    cfg = load_config()                 # dict, validated
    cfg["risk"]["max_position_pct"]     # 0.95
"""
from __future__ import annotations

if __package__ in (None, ""):                      # allow: python3 path/to/config.py
    import sys
    from pathlib import Path
    sys.path[0] = str(next(p for p in Path(__file__).resolve().parents if (p / "common").is_dir()))

import os
import re
from pathlib import Path

import yaml

from common.backtest import COST_PRESETS, CostModel
from common.config import LAB_ROOT

PIPELINE_DIR = LAB_ROOT / "pipeline"
DEFAULT_CONFIG = PIPELINE_DIR / "config.yaml"
REQUIRED_SECTIONS = ["broker", "universe", "data", "strategy", "costs", "risk", "secrets_from_env"]

# Patterns that look like real credentials - they must never appear in the YAML
SECRET_PATTERNS = [re.compile(p) for p in (r"^(PK|AK|CK)[A-Z0-9]{14,}$", r"^sk-ant-", r"^[A-Za-z0-9/+]{32,}={0,2}$")]
ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

_CACHE: dict[str, dict] = {}


def apply_cli_flags(argv: list[str]) -> list[str]:
    """Strip the global flags --offline and --config PATH from argv and apply them."""
    out, i = [], 0
    while i < len(argv):
        if argv[i] == "--offline":
            os.environ["LAB_OFFLINE"] = "1"
        elif argv[i] == "--config" and i + 1 < len(argv):
            os.environ["PIPELINE_CONFIG"] = argv[i + 1]
            i += 1
        else:
            out.append(argv[i])
        i += 1
    return out


def _walk(node, path=""):
    """Yield (dotted.path, value) for every leaf in the YAML tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")
    else:
        yield path, node


def validate(cfg: dict) -> list[str]:
    """Return a list of problems (empty list = valid)."""
    problems = [f"missing section '{s}'" for s in REQUIRED_SECTIONS if s not in cfg]
    if problems:
        return problems
    if cfg["broker"].get("paper") is not True:
        problems.append("broker.paper must be true - this pipeline only trades paper accounts")
    for key in ("max_position_pct", "max_daily_loss_pct"):
        v = cfg["risk"].get(key)
        if not isinstance(v, (int, float)) or not 0 < v <= 1:
            problems.append(f"risk.{key} must be a fraction between 0 and 1 (got {v!r})")
    if cfg["costs"].get("preset") not in COST_PRESETS:
        problems.append(f"costs.preset must be one of {sorted(COST_PRESETS)}")
    if not cfg["universe"].get("trade"):
        problems.append("universe.trade is empty")
    for name, env in cfg["secrets_from_env"].items():
        if not isinstance(env, str) or not ENV_NAME.match(env):
            problems.append(f"secrets_from_env.{name} must be an ENVIRONMENT VARIABLE NAME, not a value")
    for path, value in _walk(cfg):
        if isinstance(value, str) and any(p.search(value) for p in SECRET_PATTERNS):
            problems.append(f"{path} looks like a secret - move it to an environment variable")
    return problems


def load_config(path: str | Path | None = None, strict: bool = True) -> dict:
    """Load config.yaml (or PIPELINE_CONFIG / an explicit path), validate it, apply `mode`."""
    path = Path(path or os.environ.get("PIPELINE_CONFIG") or DEFAULT_CONFIG)
    key = str(path.resolve())
    if key not in _CACHE:
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cfg["_path"] = str(path)
        cfg["_problems"] = validate(cfg)
        if strict and cfg["_problems"]:
            raise ValueError(f"{path.name} is invalid: " + "; ".join(cfg["_problems"]))
        _CACHE[key] = cfg
    cfg = _CACHE[key]
    if cfg.get("mode") == "offline":
        os.environ["LAB_OFFLINE"] = "1"
    return cfg


def secret(cfg: dict, name: str) -> str | None:
    """Value of a secret, looked up by its env-variable NAME in secrets_from_env."""
    env = cfg["secrets_from_env"].get(name)
    return os.environ.get(env) if env else None


def lab_path(rel: str | Path) -> Path:
    """Path relative to labs (config paths are always relative to labs)."""
    return LAB_ROOT / rel


def kill_switch_path(cfg: dict) -> Path:
    return lab_path(cfg["risk"].get("kill_switch_file", "KILL_SWITCH"))


def cost_model(cfg: dict, preset: str | None = None) -> CostModel:
    return COST_PRESETS[preset or cfg["costs"]["preset"]]


def tradingview_cost_model(cfg: dict) -> CostModel:
    """The costs typed into the Pine strategy() call (USD per order + slippage)."""
    tv = cfg["costs"].get("tradingview", {})
    return CostModel("TradingView settings", min_commission=float(tv.get("commission_per_order", 1.0)),
                     slippage_bps=float(tv.get("slippage_bps", 0.4)))


def stage_banner(no: int, title: str) -> None:
    from common.config import banner
    banner(f"Pipeline stage {no:02d} - {title}")


if __name__ == "__main__":
    c = load_config(strict=False)
    print(f"{c['_path']}: {'valid' if not c['_problems'] else c['_problems']}")
