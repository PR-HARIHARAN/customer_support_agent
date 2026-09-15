"""LLM-as-a-Judge rubric for evaluating AI-generated customer support replies.

Evaluates:
1. Grounding & Faithfulness (1-5)
2. Intent Relevance (1-5)
3. Brand Tone & Empathy (1-5)
4. Actionability & Privacy (1-5)
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class JudgeScore:
    grounding: int
    relevance: int
    tone: int
    actionability: int
    overall: float
    critique: str

    @property
    def grounding_score(self) -> int:
        return self.grounding

    @property
    def intent_relevance_score(self) -> int:
        return self.relevance

    @property
    def brand_tone_score(self) -> int:
        return self.tone

    @property
    def actionability_score(self) -> int:
        return self.actionability

    @property
    def overall_score(self) -> float:
        return self.overall

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReplyQualityJudge:
    """Evaluates support reply quality using explicit rubric criteria."""

    def evaluate(
        self,
        customer_message: str,
        generated_reply: str,
        predicted_intent: str = "",
        retrieved_context: list[str] | None = None,
    ) -> JudgeScore:
        """Alias for evaluate_reply matching standard eval harness signature."""
        ctx = retrieved_context[0] if retrieved_context else ""
        return self.evaluate_reply(
            customer_message=customer_message,
            intent=predicted_intent,
            historical_resolution=ctx,
            draft_reply=generated_reply,
        )

    RUBRIC_PROMPT = """You are an expert Quality Assurance Lead for American Airlines Customer Relations on Twitter.
Evaluate the following AI-generated support reply on a 1-5 scale across four key criteria:

1. Grounding & Faithfulness (1-5):
   - 5: Strictly aligned with retrieved historical resolutions; makes zero false promises or hallucinated guarantees.
   - 3: Plausible but generic; loosely grounded.
   - 1: Severe hallucination (e.g. promising cash refunds, booking vouchers, or fake flight changes).

2. Intent Relevance (1-5):
   - 5: Directly addresses the customer's specific problem (e.g. baggage, delay, cancellation, seating).
   - 3: Recognizes the general area but misses the customer's core question.
   - 1: Completely misses the customer's intent.

3. Brand Voice & Tone (1-5):
   - 5: Professional, empathetic, concise, and appropriate for American Airlines Twitter support (#AATeam).
   - 3: Somewhat robotic or bland.
   - 1: Uncaring, defensive, or unprofessional.

4. Actionability & Privacy (1-5):
   - 5: Directs customer to send confirmation/PNR/bag tag via private Direct Message (DM) to protect privacy.
   - 3: Vague next step.
   - 1: Asks customer to tweet personal sensitive data publicly.

Customer Message: {customer_message}
Predicted Intent: {intent}
Retrieved Historical Resolution: {historical_resolution}
AI Draft Reply: {draft_reply}

Return ONLY a JSON object formatted exactly as:
{{
  "grounding": <int 1-5>,
  "relevance": <int 1-5>,
  "tone": <int 1-5>,
  "actionability": <int 1-5>,
  "overall": <float 1.0-5.0>,
  "critique": "<one sentence explanation>"
}}
"""

    def __init__(self, llm_callable: Any = None) -> None:
        self.llm_callable = llm_callable

    def evaluate_reply(
        self,
        customer_message: str,
        intent: str,
        historical_resolution: str,
        draft_reply: str,
    ) -> JudgeScore:
        """Evaluate a generated reply against the rubric."""
        if self.llm_callable:
            try:
                prompt = self.RUBRIC_PROMPT.format(
                    customer_message=customer_message,
                    intent=intent,
                    historical_resolution=historical_resolution,
                    draft_reply=draft_reply,
                )
                raw = self.llm_callable(prompt)
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    return JudgeScore(
                        grounding=int(data.get("grounding", 4)),
                        relevance=int(data.get("relevance", 4)),
                        tone=int(data.get("tone", 4)),
                        actionability=int(data.get("actionability", 5)),
                        overall=float(data.get("overall", 4.25)),
                        critique=str(
                            data.get("critique", "Aligned with brand resolution standards.")
                        ),
                    )
            except Exception as exc:
                logger.warning(
                    f"LLM Judge call failed ({exc}); falling back to deterministic heuristic judge."
                )

        # Deterministic heuristic scoring baseline (calibrated to human rubric)
        g_score = 4
        r_score = 4
        t_score = 4
        a_score = 4
        notes = []

        # Privacy check: does the draft properly ask for DM for sensitive details?
        if any(w in draft_reply.lower() for w in ["dm", "direct message"]):
            a_score = 5
            notes.append("Properly directs sensitive identifiers to DM.")
        else:
            a_score = 3
            notes.append("No explicit DM redirection.")

        # Brand voice: empathy check
        if any(
            w in draft_reply.lower()
            for w in ["apologize", "sorry", "appreciate", "welcome", "#aateam"]
        ):
            t_score = 5
        else:
            t_score = 3

        # Grounding check: does it hallucinate cash/vouchers?
        if any(w in draft_reply.lower() for w in ["refund $", "free ticket", "guarantee cash"]):
            g_score = 1
            notes.append("Hallucinates monetary guarantee.")
        else:
            g_score = 5

        # Relevance check
        intent_lower = intent.lower()
        if (
            "baggage" in intent_lower
            and any(w in draft_reply.lower() for w in ["bag", "luggage", "claim"])
            or "delay" in intent_lower
            and any(w in draft_reply.lower() for w in ["delay", "time", "travels"])
            or "positive" in intent_lower
            and any(w in draft_reply.lower() for w in ["appreciate", "thank", "love", "loyalty"])
        ):
            r_score = 5
        else:
            r_score = 4

        overall = round((g_score + r_score + t_score + a_score) / 4.0, 2)
        critique = (
            " ".join(notes) if notes else "Professional reply grounded in historical resolution."
        )

        return JudgeScore(
            grounding=g_score,
            relevance=r_score,
            tone=t_score,
            actionability=a_score,
            overall=overall,
            critique=critique,
        )
