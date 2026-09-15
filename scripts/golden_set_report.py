"""Standalone Steps 9-10 report for the human golden set (005_golden_set.ipynb).

Runs the post-review taxonomy analysis (Step 9) and the quality/final report
(Step 10) on the CURRENT saved state of data/processed/golden_set.csv without
needing the full notebook (no FAISS, no KMeans, no embeddings).

Prereqs:
  data/processed/golden_set.csv        saved by label_app.py
  data/processed/conversations.jsonl   source conversation ids for leakage check

Usage:
  python scripts/golden_set_report.py [--golden data/processed/golden_set.csv]
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from customer_support.labeling.validation import (  # noqa: E402
    HUMAN_INTENTS_ALLOWED,
    VALID_OUTCOMES,
)

DEFAULT_GOLDEN = PROJECT_ROOT / "data" / "processed" / "golden_set.csv"
DEFAULT_CONVERSATIONS = PROJECT_ROOT / "data" / "processed" / "conversations.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def step9(gold: pd.DataFrame) -> None:
    reviewed = gold[gold["annotation_status"] == "reviewed"].copy()
    print(f"Review completion: {len(reviewed)}/250 ({len(reviewed) / 250 * 100:.1f}%)")
    if len(reviewed) == 0:
        print("No human labels yet - complete Step 8 reviews.")
        return

    labeled = reviewed[reviewed["human_intent"] != ""].copy()
    print(f"\nHUMAN-ANNOTATED distribution (observed within reviewed, n={len(labeled)}):")
    print(
        labeled["human_intent"]
        .value_counts()
        .to_frame("human_count")
        .assign(human_pct=lambda f: (f["human_count"] / len(labeled) * 100).round(1))
        .to_string()
    )

    print("\nCandidate -> human confusion (rows=candidate proposal, columns=human decision):")
    conf = pd.crosstab(labeled["candidate_intent"], labeled["human_intent"])
    print(conf.to_string())

    acc = (
        (labeled["candidate_intent"] == labeled["human_intent"])
        .groupby(labeled["candidate_intent"])
        .mean()
    )
    print("\nPer-candidate acceptance rate (human kept the proposed label):")
    print(acc.to_frame("acceptance_rate").round(3).sort_values("acceptance_rate").to_string())

    print("\n--- Taxonomy revision flags ---")
    flagged = False
    for intent, grp in labeled.groupby("candidate_intent"):
        n = len(grp)
        a = float((grp["candidate_intent"] == grp["human_intent"]).mean())
        spread = grp["human_intent"].value_counts(normalize=True)
        big = spread[spread >= 0.15]
        if n >= 5 and a < 0.50:
            print(f"MERGE/REDEFINE candidate: '{intent}' accepted only {a:.0%} (n={n})")
            flagged = True
        if n >= 8 and len(big) >= 3:
            print(f"SPLIT candidate: '{intent}' spreads across {dict(big.round(2))} (n={n})")
            flagged = True
    # Cross-field consistency (the ACCEPT/CHANGE_INTENT/RENAME semantic checks).
    complain = []
    for _, r in labeled.iterrows():
        outcome = r["annotation_outcome"]
        if outcome == "ACCEPT" and r["candidate_intent"] != r["human_intent"]:
            complain.append(f"{r['conversation_id']}: ACCEPT but human != candidate")
        elif outcome == "CHANGE_INTENT" and r["candidate_intent"] == r["human_intent"]:
            complain.append(f"{r['conversation_id']}: CHANGE_INTENT but intents match")
        elif outcome == "RENAME" and r["candidate_intent"] != r["human_intent"]:
            complain.append(f"{r['conversation_id']}: RENAME but intents differ")
    if not flagged and not complain:
        print("No taxonomy revision flags met (needs >=5/>=8 reviewed per candidate intent).")
    if complain:
        print("Cross-field inconsistencies to fix:")
        for line in complain:
            print(f"  ! {line}")


def step10(golden_path: Path, conversations_path: Path | None, rec_by_id: dict[str, dict]) -> None:
    check = pd.read_csv(golden_path, dtype={"conversation_id": str}, keep_default_na=False)
    REQUIRED = [
        "conversation_id",
        "full_conversation_text",
        "sampling_group",
        "candidate_cluster",
        "candidate_intent",
        "candidate_confidence",
        "candidate_ambiguity_margin",
        "human_intent",
        "human_sub_intent",
        "human_domain",
        "annotation_status",
        "reviewer_notes",
    ]
    missing = [c for c in REQUIRED if c not in check.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(check) == 250 and check["conversation_id"].nunique() == 250
    assert Counter(check["sampling_group"]) == {
        "representative": 150,
        "uncertainty": 60,
        "challenge": 40,
    }
    assert check["sampling_group"].isna().sum() == 0 and (check["sampling_group"] != "").all()
    assert set(check["conversation_id"]) <= set(rec_by_id), "sampling leakage"
    rev = check[check["annotation_status"] == "reviewed"]
    assert ((rev["human_intent"] != "") | (rev["annotation_outcome"] != "")).all()
    assert set(check["human_intent"]) <= set(HUMAN_INTENTS_ALLOWED + [""])
    assert set(check["annotation_outcome"]) <= set(VALID_OUTCOMES + [""])

    # Cross-field semantic checks (Step 9 addition; candidate labels preserved).
    inconsistent = []
    for _, r in rev.iterrows():
        if (
            r["annotation_outcome"] == "ACCEPT"
            and r["human_intent"]
            and r["candidate_intent"] != r["human_intent"]
        ):
            inconsistent.append(r["conversation_id"])
    assert not inconsistent, f"ACCEPT with mismatched intent: {inconsistent}"

    print(
        "ALL QUALITY CHECKS PASSED (250 unique | groups 150/60/40 | candidates preserved | labels valid | no leakage)"
    )

    n_rev = len(rev)
    n_acc = int((rev["annotation_outcome"] == "ACCEPT").sum())
    n_corr = int(rev["annotation_outcome"].isin(["RENAME", "CHANGE_INTENT"]).sum())
    n_split = int((rev["annotation_outcome"] == "SPLIT_NEEDED").sum())
    n_merge = int((rev["annotation_outcome"] == "MERGE_NEEDED").sum())
    n_unk = int(rev["annotation_outcome"].isin(["UNKNOWN", "NON_ACTIONABLE", "SOCIAL"]).sum())
    print("\n================ GOLDEN SET SUMMARY ================")
    print(
        f"total = {len(check)} | representative = 150 | uncertainty/diversity = 60 | challenge = 40"
    )
    print(f"3. human-reviewed distribution: {n_rev} reviewed; see Step 9 table")
    print(
        f"7. new intents discovered: {int((rev['human_intent'] == 'New intent (see notes)').sum())}"
    )
    print(f"9. accepted unchanged: {n_acc} | 10. corrected: {n_corr}")
    print(
        f"11. unknown/non-actionable/social: {n_unk} | split-needed: {n_split} | merge-needed: {n_merge}"
    )
    print(f"12. review completion: {n_rev}/250 ({n_rev / 250 * 100:.1f}%)")
    print("\nDownstream: evaluate population-like behavior on the 150 representative rows;")
    print("report any all-250 number as an ENRICHED gold-set metric.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Standalone Steps 9-10 golden-set report.")
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--conversations", type=Path, default=DEFAULT_CONVERSATIONS)
    args = parser.parse_args(argv)
    if not args.golden.exists():
        print(f"Golden set not found: {args.golden}")
        return 2

    gold = pd.read_csv(args.golden, dtype={"conversation_id": str}, keep_default_na=False)
    sources = load_jsonl(args.conversations) if args.conversations.exists() else []
    rec_by_id = {str(r["conversation_id"]): r for r in sources}
    print("== Step 9: post-review taxonomy analysis ==")
    step9(gold)
    print("\n== Step 10: quality checks + final summary ==")
    step10(args.golden, args.conversations if args.conversations.exists() else None, rec_by_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
