"""Tests for the baseline classifiers and evaluation metrics."""

from __future__ import annotations

import numpy as np
import pytest

from customer_support.classification import (
    logistic_regression_prediction,
    majority_class_prediction,
    nearest_centroid_prediction,
)
from customer_support.evaluation import classification_metrics


def _tiny_dataset() -> tuple[np.ndarray, np.ndarray]:
    # Two well-separated blobs in R2; 4 of each class so any 50% split is balanced.
    rng = np.random.default_rng(0)
    x = np.vstack(
        [
            rng.normal([-2, 0], 0.3, size=(4, 2)),
            rng.normal([2, 0], 0.3, size=(4, 2)),
        ]
    )
    y = np.asarray(["a"] * 4 + ["b"] * 4, dtype=object)
    return x, y


def test_majority_class_always_predicts_majority() -> None:
    y = np.asarray(["a", "a", "a", "b"], dtype=object)
    pred = majority_class_prediction(y, n_test=3)
    assert list(pred) == ["a", "a", "a"]


def test_nearest_centroid_separates_blobs() -> None:
    x, y = _tiny_dataset()
    train, test = np.array([0, 1, 4, 5]), np.array([2, 3, 6, 7])
    pred = nearest_centroid_prediction(x[train], y[train], x[test])
    assert list(pred) == ["a", "a", "b", "b"]


def test_logistic_regression_separates_blobs() -> None:
    x, y = _tiny_dataset()
    train, test = np.array([0, 1, 4, 5]), np.array([2, 3, 6, 7])
    pred = logistic_regression_prediction(x[train], y[train], x[test])
    assert list(pred) == ["a", "a", "b", "b"]


def test_classification_metrics_keys() -> None:
    y_true = np.asarray(["a", "a", "b"])
    y_pred = np.asarray(["a", "b", "b"])
    metrics = classification_metrics(y_true, y_pred)
    assert set(metrics) >= {"accuracy", "macro_f1", "weighted_f1", "per_class", "n_test"}
    assert metrics["accuracy"] == pytest.approx(2 / 3)

    by_label = {row["label"]: row for row in metrics["per_class"]}
    assert by_label["a"]["f1"] == pytest.approx(2 / 3)
    # b: precision 0.5, recall 1.0 -> F1 = 2/3
    assert by_label["b"]["f1"] == pytest.approx(2 / 3)
    assert by_label["a"]["support"] == 2


def test_classification_metrics_all_wrong() -> None:
    y_true = np.asarray(["a", "a", "b"])
    y_pred = np.asarray(["b", "b", "a"])
    metrics = classification_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 0.0
    assert metrics["macro_f1"] == 0.0
