"""Evaluation metrics for intent classification.

All metrics are computed with scikit-learn and returned as plain dicts so the
results can be written directly to JSON for the report directory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Accuracy, macro-F1, weighted-F1 and per-class F1.

    ``labels`` for per-class F1 is derived from the unique true labels so no
    unseen test-only class is silently dropped from the report.
    """
    import numpy as np
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        f1_score,
        precision_recall_fscore_support,
    )

    true = np.asarray(y_true)
    pred = np.asarray(y_pred)
    labels = sorted({str(label) for label in true})

    report = classification_report(true, pred, labels=labels, zero_division=0, output_dict=True)

    precision, recall, f1, support = precision_recall_fscore_support(
        true, pred, labels=labels, zero_division=0
    )
    per_class = [
        {
            "label": label,
            "precision": float(p),
            "recall": float(r),
            "f1": float(f),
            "support": int(s),
        }
        for label, p, r, f, s in zip(labels, precision, recall, f1, support, strict=True)
    ]

    return {
        "accuracy": float(accuracy_score(true, pred)),
        "macro_f1": float(f1_score(true, pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(true, pred, average="weighted", zero_division=0)),
        "n_test": int(len(true)),
        "n_labels": len(labels),
        "majority_class_share": float(
            max(np.bincount([labels.index(str(label)) for label in true])) / max(len(true), 1)
        ),
        "per_class": per_class,
        "report": report,
    }


__all__ = ["classification_metrics"]
