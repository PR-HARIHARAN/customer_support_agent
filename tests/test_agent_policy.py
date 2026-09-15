"""Tests for SupportDecisionPolicy, LLM Judge, and GroundedReplyEvaluator."""

from __future__ import annotations

from customer_support.agent.policy import SupportDecisionPolicy
from customer_support.evaluation.llm_judge import ReplyQualityJudge
from customer_support.evaluation.ragas_eval import GroundedReplyEvaluator


def test_policy_escalates_safety_and_medical() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "I need emergency medical assistance at gate 4", "Flight information"
    )
    assert decision.action == "ESCALATE"
    assert "medical" in decision.reason.lower()


def test_policy_escalates_profanity_and_anger() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "You guys are fucking crooks and stole my money", "Service complaint"
    )
    assert decision.action == "ESCALATE"
    assert "profanity" in decision.reason.lower() or "agitation" in decision.reason.lower()


def test_policy_escalates_legal_threats() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "I am filing a DOT complaint and contacting my lawyer", "Service complaint"
    )
    assert decision.action == "ESCALATE"
    assert "legal" in decision.reason.lower() or "dot" in decision.reason.lower()


def test_policy_auto_handles_routine_praise() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "Thank you Erica at ORD for the wonderful flight service! #AATeam", "Positive experience"
    )
    assert decision.action == "AUTO_HANDLE"
    assert decision.risk_level == "low"


def test_policy_auto_handles_social_greeting() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "Good morning @AmericanAir, have a great day!", "Social acknowledgement"
    )
    assert decision.action == "AUTO_HANDLE"


def test_llm_judge_deterministic_scoring() -> None:
    judge = ReplyQualityJudge()
    score = judge.evaluate_reply(
        customer_message="Where is my bag?",
        intent="Baggage issues",
        historical_resolution="Please report to the Baggage Service Office.",
        draft_reply="We're so sorry. Please DM us your record locator so we can assist.",
    )
    assert 1 <= score.grounding <= 5
    assert 1 <= score.relevance <= 5
    assert 1 <= score.tone <= 5
    assert 1 <= score.actionability <= 5
    assert 1.0 <= score.overall <= 5.0


def test_grounded_reply_evaluator() -> None:
    evaluator = GroundedReplyEvaluator()
    metrics = evaluator.evaluate_sample(
        customer_query="Flight 100 delay status",
        retrieved_contexts=["Flight 100 is delayed 45 minutes."],
        generated_reply="Flight 100 has an estimated 45 minute delay.",
        reference_reply="Flight 100 departure delayed.",
    )
    assert 0.0 <= metrics["answer_relevancy"] <= 1.0
    assert 0.0 <= metrics["faithfulness"] <= 1.0
    assert 0.0 <= metrics["semantic_agreement"] <= 1.0


def test_failure_mode_1_sarcasm_escalated() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "@AmericanAir thank you so much for allowing passengers to sit for 8+ hours with no AC. Top notch service!",
        "Positive experience",
    )
    assert decision.action == "ESCALATE"
    assert "sarcastic" in decision.reason.lower() or "disruption" in decision.reason.lower()


def test_failure_mode_2_staff_insult_escalated() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "@AmericanAir talking to your staff is like talking to a toad. Leaving people stranded with no room",
        "Disruption recovery",
    )
    assert decision.action == "ESCALATE"
    assert "conduct" in decision.reason.lower() or "supervisor" in decision.reason.lower()


def test_failure_mode_3_in_cabin_lost_handled() -> None:
    policy = SupportDecisionPolicy()
    # General lost item auto-handled with portal link
    decision = policy.evaluate(
        "@AmericanAir A friend flew ORD-LGA and left his laptop in the seatback pocket. Who does he contact?",
        "Seats and fares",
    )
    assert decision.action == "AUTO_HANDLE"
    assert "lost & found" in decision.reason.lower() or "in-cabin" in decision.reason.lower()

    # Urgent passport lost escalated
    urgent_decision = policy.evaluate(
        "@AmericanAir I left my passport in the seat pocket on flight 402, need it urgently!",
        "Seats and fares",
    )
    assert urgent_decision.action == "ESCALATE"


def test_failure_mode_4_gate_ticketing_dispute_escalated() -> None:
    policy = SupportDecisionPolicy()
    decision = policy.evaluate(
        "@AmericanAir pls explain why my $750 tkt isn't eligible for paid standby. Gate agt doesn't know what to do.",
        "Seats and fares",
    )
    assert decision.action == "ESCALATE"
    assert "gate agent" in decision.reason.lower() or "standby" in decision.reason.lower()
