"""Review vocabulary and validation rules for the human golden-set labelling.

Kept importable (no Streamlit dependencies) so both ``label_app.py`` and
``scripts/golden_set_report.py`` share a single source of truth.

The vocabulary must stay in sync with ``notebooks/005_golden_set.ipynb``.
"""

from __future__ import annotations

VALID_OUTCOMES = [
    "ACCEPT",
    "RENAME",
    "CHANGE_INTENT",
    "SPLIT_NEEDED",
    "MERGE_NEEDED",
    "SOCIAL",
    "NON_ACTIONABLE",
    "UNKNOWN",
]

CANDIDATE_INTENTS = [
    "Positive experience",
    "Flight delay",
    "Disruption recovery",
    "Flight information",
    "General dissatisfaction",
    "Service complaint",
    "Social acknowledgement",
    "Seats and fares",
    "Baggage issues",
]

HUMAN_INTENTS_ALLOWED = CANDIDATE_INTENTS + [
    "Non-actionable",
    "Unknown / insufficient context",
    "New intent (see notes)",
]

REVIEW_ONLY_OUTCOMES = {"UNKNOWN", "NON_ACTIONABLE", "SOCIAL", "SPLIT_NEEDED", "MERGE_NEEDED"}

INTENT_DEFINITIONS = {
    "Positive experience": "Praise or thanks for a completed flight, crew, or staff experience.",
    "Social acknowledgement": "Short social contact, thanks, casual mention, or low-context exchange without a support problem.",
    "Disruption recovery": "Cancellation, missed connection, rerouting, rebooking, compensation, or recovery after a disrupted itinerary.",
    "Flight delay": "Late departure, arrival, gate, maintenance wait, or tarmac delay is the dominant issue.",
    "Seats and fares": "Seat assignment/change, upgrade, cabin, basic-economy restriction, or paid seating/fare issue.",
    "Baggage issues": "Lost, delayed, damaged, checked, carry-on, or luggage-handling issue.",
    "Service complaint": "Complaint about agent behavior, staff, responsiveness, customer relations, or support quality.",
    "General dissatisfaction": "Broad negative experience where no single operational issue dominates; do not use when a specific issue applies.",
    "Flight information": "Question or request about flight status, route, schedule, policy, check-in, or travel rules.",
}

ANNOTATION_GUIDE = {
    "Positive experience": "Include: explicit praise of crew/flight/service. Exclude: bare 'thanks' with no content (that is Social). Confusing: Social acknowledgement.",
    "Social acknowledgement": "Include: greetings, bare thanks, casual mentions, no problem stated. Exclude: any actionable request. Confusing: Positive experience, Flight information.",
    "Disruption recovery": "Include: cancelled/missed/rebooked itinerary + recovery ask. Exclude: mere delay with original flight intact (that is Flight delay). Confusing: Flight delay, Flight information.",
    "Flight delay": "Include: late departure/arrival/gate/tarmac wait as the dominant issue. Exclude: delay that already caused a missed connection (that is Disruption recovery). Confusing: Disruption recovery, Service complaint.",
    "Seats and fares": "Include: seat assignment/change, upgrade, cabin, fare rules/charges. Exclude: general delay complaints from a seat (that is Flight delay). Confusing: Flight information, Service complaint. Watch for SPLIT into seat-assignment vs fare/payment.",
    "Baggage issues": "Include: lost/delayed/damaged/checked/carry-on baggage handling. Exclude: complaining about staff while discussing bags -> pick the dominant issue. Confusing: Service complaint.",
    "Service complaint": "Include: complaint about agent/staff/responsiveness/support quality. Exclude: broad venting with no service target (that is General dissatisfaction). Confusing: General dissatisfaction.",
    "General dissatisfaction": "Include ONLY: broad negativity where no single operational issue dominates. Exclude: any case a specific intent fits — prefer the specific intent. Confusing: Service complaint. Top MERGE/REMOVE suspect.",
    "Flight information": "Include: questions about status/route/schedule/policy/check-in. Exclude: complaints phrased as questions about a past failure. Confusing: Disruption recovery, Seats and fares.",
}


def validate_review(outcome: str, human_intent: str, candidate_intent: str = "") -> str | None:
    """Validate a single review record; return an error message or ``None``.

    Cross-checks outcome vs. intent so the labeller cannot record a
    contradictory verdict (e.g. ACCEPT while changing the candidate label).
    """
    if outcome not in VALID_OUTCOMES:
        return f"Invalid outcome: {outcome!r}. Must be one of {VALID_OUTCOMES}."
    if human_intent not in HUMAN_INTENTS_ALLOWED:
        return (
            f"Invalid human_intent: {human_intent!r}. Pick a candidate intent, "
            "'Non-actionable', 'Unknown / insufficient context', or "
            "'New intent (see notes)' (and describe it in reviewer notes)."
        )
    if not human_intent and outcome not in REVIEW_ONLY_OUTCOMES:
        return f"Outcome {outcome} requires a human_intent label."
    if outcome == "ACCEPT" and candidate_intent and human_intent != candidate_intent:
        return (
            f"ACCEPT means the candidate label is correct, but human_intent "
            f"{human_intent!r} differs from candidate_intent {candidate_intent!r}. "
            f"Use CHANGE_INTENT or RENAME, or set human_intent to {candidate_intent!r}."
        )
    if outcome == "CHANGE_INTENT" and candidate_intent and human_intent == candidate_intent:
        return (
            "CHANGE_INTENT means the candidate label is wrong, but human_intent "
            "matches candidate_intent. Pick a different intent or use ACCEPT/RENAME."
        )
    if outcome == "RENAME" and candidate_intent and human_intent != candidate_intent:
        return (
            f"RENAME is for keeping the same intent with a new name, but human_intent "
            f"{human_intent!r} differs from {candidate_intent!r}. Use CHANGE_INTENT instead."
        )
    return None


__all__ = [
    "VALID_OUTCOMES",
    "CANDIDATE_INTENTS",
    "HUMAN_INTENTS_ALLOWED",
    "REVIEW_ONLY_OUTCOMES",
    "INTENT_DEFINITIONS",
    "ANNOTATION_GUIDE",
    "validate_review",
]
