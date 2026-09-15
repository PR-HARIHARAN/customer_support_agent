"""Tests for the central configuration module."""

from __future__ import annotations

import pytest

from customer_support.config import REPO_ROOT, load_pilot_config

CONFIG_FILE = REPO_ROOT / "configs" / "repro.toml"


def test_default_config_isolated_from_environment() -> None:
    config = load_pilot_config(config_file=CONFIG_FILE, env={})
    assert str(config.paths.data_dir).endswith("data")
    assert str(config.paths.reports_dir).endswith("reports")
    assert config.paths.gold_set.exists()
    assert config.embedding_model
    assert 0.0 < config.test_fraction < 1.0
    assert config.seed >= 0


def test_env_overrides() -> None:
    config = load_pilot_config(
        config_file=CONFIG_FILE,
        env={
            "CSA_DATA_DIR": "other_data",
            "CSA_REPORTS_DIR": "other_reports",
            "CSA_EMBEDDING_MODEL": "test/model",
            "CSA_SEED": "7",
        },
    )
    assert str(config.paths.data_dir).endswith("other_data")
    assert str(config.paths.reports_dir).endswith("other_reports")
    assert config.embedding_model == "test/model"
    assert config.seed == 7


def test_missing_config_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_pilot_config(config_file=REPO_ROOT / "configs" / "does_not_exist.toml", env={})
