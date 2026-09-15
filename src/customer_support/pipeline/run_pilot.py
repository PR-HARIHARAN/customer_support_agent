"""Small reproducible end-to-end pilot for intent classification.

Runs the trivial baseline (majority class), a nearest-centroid baseline and a
logistic-regression classifier on a small labelled set, then writes a metrics
JSON report and prints a comparison table.

By default it evaluates on ``data/processed/experiments/gold_300.csv`` — the
300-message proxy-gold set produced by two-LLM + adjudicator annotation in
``notebooks/005``. **These labels are model-generated; they are NOT human
gold.** The human golden set (``data/processed/golden_set.csv``) is being
built separately and is still in progress.

Usage::

    python main.py pilot                      # defaults from configs/repro.toml
    python main.py pilot -m intfloat/e5-small-v2
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

from customer_support.classification import (
    logistic_regression_prediction,
    majority_class_prediction,
    nearest_centroid_prediction,
)
from customer_support.config import load_pilot_config
from customer_support.data import split_indexed
from customer_support.embeddings import TextEmbedder
from customer_support.evaluation import classification_metrics

DEFAULT_REPORT = "reports/experiments/intent_classification/intent_pilot_metrics.json"

PROVENANCE_NOTE = (
    "Labels are model-generated proxy labels (two LLMs + adjudicator), NOT human gold. "
    "Treat all metrics as taxonomy-consistency estimates, not human-ground-truth performance."
)


def run_pilot(
    gold_set: Path,
    embedding_model: str,
    test_fraction: float,
    seed: int,
    report_path: Path,
    device: str | None = None,
    sampling_group: str | None = None,
) -> dict:
    """Embed the gold set, split it, evaluate baselines, write the report."""
    gold = pd.read_csv(
        gold_set, dtype={"message_id": str, "conversation_id": str}, keep_default_na=False
    )
    if sampling_group and "sampling_group" in gold.columns and sampling_group != "all":
        gold = gold[gold["sampling_group"] == sampling_group]

    text_col = (
        "full_conversation_text" if "full_conversation_text" in gold.columns else "message_text"
    )
    label_col = (
        "human_intent"
        if "human_intent" in gold.columns and (gold["human_intent"] != "").any()
        else "gold_intent"
    )

    good = gold[(gold[text_col] != "") & (gold[label_col] != "")]
    if len(good) < 10:
        raise ValueError(f"Too few usable rows in {gold_set}: {len(good)}")

    texts = good[text_col].astype(str).tolist()
    labels = good[label_col].astype(str).tolist()
    n = len(texts)

    train_idx, test_idx = split_indexed(n, test_fraction, seed=seed)
    train_idx_set = set(train_idx)

    emb = TextEmbedder(embedding_model, device=device)
    x = emb.encode(texts)
    x_train, x_test = x[train_idx], x[test_idx]
    y_train = [labels[i] for i in train_idx]
    y_test = [labels[i] for i in test_idx]

    predictions = {
        "majority_class": majority_class_prediction(y_train, len(test_idx)),
        "nearest_centroid": nearest_centroid_prediction(x_train, y_train, x_test),
        "logistic_regression": logistic_regression_prediction(x_train, y_train, x_test),
    }

    results = {model: classification_metrics(y_test, pred) for model, pred in predictions.items()}

    provenance = (
        "Labels are human-annotated ground truth from the 250-conversation golden set (data/processed/golden_set.csv)."
        if label_col == "human_intent"
        else PROVENANCE_NOTE
    )

    report = {
        "task": "intent_classification",
        "embedding_model": embedding_model,
        "embedding_dimension": emb.dimension,
        "seed": seed,
        "test_fraction": test_fraction,
        "sampling_group": sampling_group or "all",
        "n_total": n,
        "n_train": len(train_idx_set),
        "n_test": len(test_idx),
        "label_provenance": provenance,
        "dataset": str(gold_set),
        "metrics": results,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def _print_summary(report: dict) -> None:
    print(f"\nIntent-classification pilot — {report['embedding_model']}")
    print(
        f"n_train={report['n_train']}  n_test={report['n_test']}  seed={report['seed']}  group={report.get('sampling_group', 'all')}"
    )
    print(f"{'model':<24}{'accuracy':>10}{'macro-F1':>10}{'weighted-F1':>12}")
    for model, metrics in report["metrics"].items():
        print(
            f"{model:<24}{metrics['accuracy']:>10.3f}"
            f"{metrics['macro_f1']:>10.3f}{metrics['weighted_f1']:>12.3f}"
        )
    print(f"\n{report['label_provenance']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-m", "--embedding-model", default=None, help="sentence-transformers model id"
    )
    parser.add_argument("--gold-set", default=None, help="path to labelled CSV override")
    parser.add_argument(
        "--sampling-group",
        default=None,
        help="filter by sampling group (e.g. representative, uncertainty, challenge, all)",
    )
    parser.add_argument("--test-fraction", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--report", default=None, help="output metrics JSON path")
    parser.add_argument("--device", default=None, help="torch device (cpu/cuda)")
    args = parser.parse_args(argv)

    config = load_pilot_config()

    gold_set = Path(args.gold_set) if args.gold_set else config.paths.gold_set
    test_fraction = args.test_fraction if args.test_fraction is not None else config.test_fraction
    seed = args.seed if args.seed is not None else config.seed
    embedding_model = args.embedding_model or config.embedding_model
    report_path = Path(args.report) if args.report else config.paths.root / DEFAULT_REPORT

    if not Path(gold_set).exists():
        print(f"ERROR: gold set not found: {gold_set}")
        return 2

    started = time.time()
    report = run_pilot(
        gold_set=Path(gold_set),
        embedding_model=embedding_model,
        test_fraction=test_fraction,
        seed=seed,
        report_path=report_path,
        device=args.device,
        sampling_group=args.sampling_group,
    )
    _print_summary(report)
    print(f"Report written to {report_path}  ({time.time() - started:.1f}s elapsed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
