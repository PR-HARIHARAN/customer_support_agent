"""Intent-classification baselines."""

from .baselines import (
    logistic_regression_prediction,
    majority_class_prediction,
    nearest_centroid_prediction,
)

__all__ = [
    "logistic_regression_prediction",
    "majority_class_prediction",
    "nearest_centroid_prediction",
]
