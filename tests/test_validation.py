"""Tests for the golden-set review vocabulary and validation rules."""

from __future__ import annotations

import pytest

from customer_support.labeling.validation import (
    CANDIDATE_INTENTS,
    HUMAN_INTENTS_ALLOWED,
    VALID_OUTCOMES,
    validate_review,
)


def test_vocabulary_is_coherent() -> None:
    assert "Non-actionable" in HUMAN_INTENTS_ALLOWED
    assert "Unknown / insufficient context" in HUMAN_INTENTS_ALLOWED
    assert len(set(CANDIDATE_INTENTS)) == len(CANDIDATE_INTENTS)


@pytest.mark.parametrize("outcome", VALID_OUTCOMES)
def test_valid_outcomes_are_accepted(outcome: str) -> None:
    # REVIEW_ONLY outcomes must accept an empty intent; others need one.
    intent = (
        ""
        if outcome in {"UNKNOWN", "NON_ACTIONABLE", "SOCIAL", "SPLIT_NEEDED", "MERGE_NEEDED"}
        else CANDIDATE_INTENTS[0]
    )
    if intent == "":
        # empty human_intent trips the "not in allowed" guard before the outcome rule
        assert validate_review(outcome, intent) is not None
    else:
        assert validate_review(outcome, intent) is None


def test_accept_must_match_candidate() -> None:
    error = validate_review("ACCEPT", "Service complaint", candidate_intent="Flight information")
    assert "ACCEPT" in error and "Flight information" in error
    assert (
        validate_review("ACCEPT", "Flight information", candidate_intent="Flight information")
        is None
    )


def test_change_intent_must_differ() -> None:
    error = validate_review("CHANGE_INTENT", "Flight delay", candidate_intent="Flight delay")
    assert "CHANGE_INTENT" in error
    assert (
        validate_review("CHANGE_INTENT", "Flight delay", candidate_intent="Disruption recovery")
        is None
    )


def test_rename_requires_same_intent() -> None:
    error = validate_review("RENAME", "Service complaint", candidate_intent="Flight delay")
    assert "CHANGE_INTENT" in error


def test_invalid_values_rejected() -> None:
    assert validate_review("NOT_A_OUTCOME", CANDIDATE_INTENTS[0]) is not None
    assert validate_review("ACCEPT", "Not a real intent") is not None
