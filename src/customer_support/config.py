"""Central configuration for the reproducible pipeline.

Settings live in ``configs/repro.toml`` and can be overridden through a small
number of environment variables so that paths never need to be hardcoded:

* ``CSA_ROOT``       - repo root (defaults to the package location)
* ``CSA_DATA_DIR``   - data directory (default: ``data``)
* ``CSA_REPORTS_DIR``- reports directory (default: ``reports``)
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CONFIG = REPO_ROOT / "configs" / "repro.toml"


@dataclass(frozen=True)
class Paths:
    """Resolved filesystem locations used by the pipeline."""

    root: Path
    data_dir: Path
    reports_dir: Path
    experiments_dir: Path
    gold_set: Path


@dataclass(frozen=True)
class PilotConfig:
    """Resolved settings for the small intent-classification pilot."""

    embedding_model: str
    test_fraction: float
    seed: int
    paths: Paths


def _resolve_root(env: dict[str, str]) -> Path:
    return Path(env["CSA_ROOT"]).resolve() if env.get("CSA_ROOT") else REPO_ROOT


def load_paths(env: dict[str, str] | None = None) -> Paths:
    env = dict(env or os.environ)
    raw = _read_toml(DEFAULT_CONFIG).get("paths", {})
    root = _resolve_root(env)

    data_dir = Path(env.get("CSA_DATA_DIR", raw.get("data_dir", "data")))
    reports_dir = Path(env.get("CSA_REPORTS_DIR", raw.get("reports_dir", "reports")))
    if not data_dir.is_absolute():
        data_dir = root / data_dir
    if not reports_dir.is_absolute():
        reports_dir = root / reports_dir

    return Paths(
        root=root,
        data_dir=data_dir,
        reports_dir=reports_dir,
        experiments_dir=data_dir / "processed" / "experiments",
        gold_set=data_dir / raw.get("gold_set", "processed/experiments/gold_300.csv"),
    )


def load_pilot_config(
    config_file: Path | None = None, env: dict[str, str] | None = None
) -> PilotConfig:
    env = dict(env or os.environ)
    raw = _read_toml(config_file or DEFAULT_CONFIG).get("pilot", {})
    return PilotConfig(
        embedding_model=str(
            env.get(
                "CSA_EMBEDDING_MODEL",
                raw.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
            )
        ),
        test_fraction=float(raw.get("test_fraction", 0.2)),
        seed=int(env.get("CSA_SEED", raw.get("seed", 42))),
        paths=load_paths(env),
    )


def _read_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "REPO_ROOT",
    "DEFAULT_CONFIG",
    "Paths",
    "PilotConfig",
    "load_paths",
    "load_pilot_config",
]
