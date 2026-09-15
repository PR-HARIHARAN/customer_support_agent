"""Baseline intent classifiers.

Kept intentionally simple: each baseline is a pure function mapping training
features/labels + test features to test predictions, so the evaluation
harness can compare them on identical splits.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def majority_class_prediction(y_train: np.ndarray, n_test: int) -> np.ndarray:
    """Trivial baseline: always predict the training-set majority class."""
    import numpy as np

    counts = {}
    for label in y_train:
        counts[label] = counts.get(label, 0) + 1
    majority = max(counts, key=counts.get)
    return np.full(n_test, majority, dtype=object)


def nearest_centroid_prediction(
    x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray
) -> np.ndarray:
    """Nearest-centroid classifier on the given (ideally normalised) features.

    Mirrors the strongest baseline from the taxonomy pilot where geometry
    carried more signal than parametric heads at small sample size.
    """
    import numpy as np

    centroids: dict[object, np.ndarray] = {}
    labels = sorted({str(label) for label in y_train})
    for label in labels:
        mask = np.array([str(y) == label for y in y_train])
        centroids[label] = x_train[mask].mean(axis=0)
    centroids[label] /= max(np.linalg.norm(centroids[label]), 1e-12)

    predictions: list[object] = []
    for row in x_test:
        best_label, best_dist = None, None
        for label, centroid in centroids.items():
            distance = float(np.linalg.norm(row - centroid))
            if best_dist is None or distance < best_dist:
                best_label, best_dist = label, distance
        predictions.append(best_label)
    return np.asarray(predictions, dtype=object)


def logistic_regression_prediction(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    class_weight: str = "balanced",
    c: float = 1.0,
) -> np.ndarray:
    """Simple ML baseline: multinomial logistic regression on embeddings."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression(
        class_weight=class_weight,
        C=c,
        solver="lbfgs",
        max_iter=2000,
    )
    model.fit(x_train, np.asarray(y_train))
    return np.asarray(model.predict(x_test), dtype=object)


__all__ = [
    "majority_class_prediction",
    "nearest_centroid_prediction",
    "logistic_regression_prediction",
]
