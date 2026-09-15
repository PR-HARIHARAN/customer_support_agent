"""Decision policy module: Auto-handle vs. Escalate to human support agent.

Evaluates an incoming customer interaction against safety rules, liability constraints,
financial/legal triggers, and confidence thresholds to decide whether the agent should
autonomously reply or escalate to a human tier-2 support specialist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ActionType = Literal["AUTO_HANDLE", "ESCALATE"]


@dataclass
class PolicyDecision:
    action: ActionType
    reason: str
    confidence: float
    risk_level: Literal["low", "medium", "high"]


class SupportDecisionPolicy:
    """Evaluates support policy rules to decide AUTO_HANDLE vs ESCALATE."""

    # Explicit escalation keywords
    LEGAL_REGULATORY_PATTERNS = [
        r"\b(lawyer|attorney|sue|lawsuit|legal action|court|small claims)\b",
        r"\b(dot|department of transportation|faa|better business bureau|bbb)\b",
        r"\b(compensation|eu261|montreal convention|chargeback|dispute charge)\b",
    ]

    SAFETY_MEDICAL_PATTERNS = [
        r"\b(medical|emergency|doctor|hospital|injury|injured|sick|ambulance)\b",
        r"\b(unaccompanied minor|infant|wheelchair|oxygen|disability|blind)\b",
    ]

    HIGH_ANGER_PROFANITY = [
        r"\b(fuck|fucking|shit|bitch|bastard|asshole|pissed|scam|fraud|liars|crooks)\b",
        r"\b(horrible|appalling|disgusting|unacceptable|disgrace)\b",
    ]

    # Failure Mode 1: Sarcastic praise disguising severe operational delays/distress
    SARCASM_CONTRADICTION_PATTERNS = [
        r"\b(thank you|thanks|top notch|great service|stellar|wonderful|awesome|love|kudos)\b.*\b(\d+\+?\s*hours?|hours?|tarmac|no ac|no air|no food|no water|stranded|stuck|cancelled|nightmare|disaster|joke)\b",
        r"\b(\d+\+?\s*hours?|hours?|tarmac|no ac|no air|no food|no water|stranded|stuck|cancelled|nightmare|disaster|joke)\b.*\b(thank you|thanks|top notch|great service|stellar|wonderful|awesome|love|kudos)\b",
        r'"(top notch|great service|stellar|amazing|wonderful)"',
    ]

    # Failure Mode 2: Staff conduct grievance / insults combined with disruption
    STAFF_GRIEVANCE_PATTERNS = [
        r"\b(staff|agent|crew|attendant|representative|manager|supervisor)\b.*\b(toad|rude|incompetent|horrible|useless|attitude|disrespect|refused|yelled|lied|clueless)\b",
        r"\b(talking to your staff|dealing with your staff|frontline agent)\b",
    ]

    # Failure Mode 3: In-cabin lost and found items
    IN_CABIN_LOST_PATTERNS = [
        r"\b(left|forgot|lost)\b.*\b(seat|pocket|seatback|overhead|plane|aircraft|cabin|onboard|board)\b",
        r"\b(lost\s*and\s*found|lost\s*property)\b",
    ]

    # Failure Mode 4: Standby/upgrade dispute with airport personnel
    TICKETING_DISPUTE_PATTERNS = [
        r"\b(gate\s*agt|gate\s*agent|ticket\s*counter)\b.*\b(standby|upgrade|doesn't know|won't help|refused|can't help)\b",
    ]

    def __init__(self, confidence_threshold: float = 0.40) -> None:
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        customer_message: str,
        predicted_intent: str,
        intent_confidence: float = 1.0,
        retrieval_similarity: float = 1.0,
    ) -> PolicyDecision:
        """Decide whether to auto-handle or escalate with an explicit justification."""
        text = customer_message.lower()

        # 1. Safety and Medical Emergencies -> Immediate Escalation
        for pattern in self.SAFETY_MEDICAL_PATTERNS:
            if re.search(pattern, text):
                return PolicyDecision(
                    action="ESCALATE",
                    reason="Safety, medical condition, or accessibility assistance detected requiring human intervention.",
                    confidence=1.0,
                    risk_level="high",
                )

        # 2. Failure Mode 1: Sarcastic praise masking severe delay or tarmac distress
        for pattern in self.SARCASM_CONTRADICTION_PATTERNS:
            if re.search(pattern, text):
                return PolicyDecision(
                    action="ESCALATE",
                    reason="Sarcastic or ironic sentiment detected disguising operational disruption; escalating to senior customer relations agent.",
                    confidence=0.92,
                    risk_level="high",
                )

        # 3. Failure Mode 2: Staff misconduct / insults combined with disruption
        for pattern in self.STAFF_GRIEVANCE_PATTERNS:
            if re.search(pattern, text):
                return PolicyDecision(
                    action="ESCALATE",
                    reason="Frontline employee conduct grievance or customer conflict detected; escalating to human supervisor.",
                    confidence=0.90,
                    risk_level="high",
                )

        # 4. Failure Mode 4: Airport gate agent dispute / complex standby rules
        for pattern in self.TICKETING_DISPUTE_PATTERNS:
            if re.search(pattern, text):
                return PolicyDecision(
                    action="ESCALATE",
                    reason="Airport gate agent standby or upgrade dispute requires human ticketing specialist review.",
                    confidence=0.88,
                    risk_level="medium",
                )

        # 5. Failure Mode 3: In-cabin lost item (urgent passports escalate, standard auto-handled with portal)
        for pattern in self.IN_CABIN_LOST_PATTERNS:
            if re.search(pattern, text):
                if re.search(r"\b(passport|id|wallet|medication|medicine)\b", text):
                    return PolicyDecision(
                        action="ESCALATE",
                        reason="Critical identity document or medication left in aircraft cabin; escalating immediately to airport station operations.",
                        confidence=0.95,
                        risk_level="high",
                    )
                return PolicyDecision(
                    action="AUTO_HANDLE",
                    reason="In-cabin lost item inquiry; auto-handling with official American Airlines Lost & Found portal guidance.",
                    confidence=0.90,
                    risk_level="low",
                )

        # 6. Legal, Regulatory, or Direct Compensation Claims -> Escalate
        for pattern in self.LEGAL_REGULATORY_PATTERNS:
            if re.search(pattern, text):
                return PolicyDecision(
                    action="ESCALATE",
                    reason="Legal, regulatory complaint (DOT/FAA), or financial compensation claim requires human oversight.",
                    confidence=0.95,
                    risk_level="high",
                )

        # 7. High Agitation, Hostility, or Severe Profanity -> Escalate
        for pattern in self.HIGH_ANGER_PROFANITY:
            if re.search(pattern, text):
                return PolicyDecision(
                    action="ESCALATE",
                    reason="High customer agitation or profanity detected; escalating to senior customer relations agent.",
                    confidence=0.90,
                    risk_level="high",
                )

        # 4. Complex Multi-Leg Disruption or Stranded Overnight -> Escalate
        if predicted_intent == "Disruption recovery" and any(
            k in text
            for k in ["stranded", "hotel", "rebook", "cancelled", "missed connection", "tomorrow"]
        ):
            return PolicyDecision(
                action="ESCALATE",
                reason="Active flight disruption with rebooking or accommodation need requires authorized human rebooking agent.",
                confidence=0.85,
                risk_level="medium",
            )

        # 5. Physical Baggage Damage / Lost Luggage -> Escalate
        if predicted_intent == "Baggage issues" and any(
            k in text for k in ["damaged", "broken", "ripped", "stolen", "missing"]
        ):
            return PolicyDecision(
                action="ESCALATE",
                reason="Physical damage or lost luggage claim requires verification with Baggage Service Office personnel.",
                confidence=0.85,
                risk_level="medium",
            )

        # 6. Service Complaint regarding Staff or Discrimination -> Escalate
        if predicted_intent == "Service complaint":
            return PolicyDecision(
                action="ESCALATE",
                reason="Customer service quality or employee conduct complaint requires human supervisor review.",
                confidence=0.80,
                risk_level="medium",
            )

        # 7. Low Classification or Retrieval Confidence Gating
        if intent_confidence < self.confidence_threshold or retrieval_similarity < 0.25:
            return PolicyDecision(
                action="ESCALATE",
                reason=f"Ambiguous intent or low confidence ({intent_confidence:.2f}); routing to human to avoid inaccurate automated reply.",
                confidence=intent_confidence,
                risk_level="low",
            )

        # 8. Safe Auto-Handle Categories:
        # Positive experience / Kudos
        if predicted_intent == "Positive experience":
            return PolicyDecision(
                action="AUTO_HANDLE",
                reason="Routine positive feedback and praise; auto-handle with brand appreciation template.",
                confidence=0.95,
                risk_level="low",
            )

        # Social pleasantry
        if predicted_intent == "Social acknowledgement":
            return PolicyDecision(
                action="AUTO_HANDLE",
                reason="Casual greeting or social mention without support liability; auto-handle safely.",
                confidence=0.95,
                risk_level="low",
            )

        # Standard flight information inquiry
        if predicted_intent == "Flight information":
            return PolicyDecision(
                action="AUTO_HANDLE",
                reason="Standard informational inquiry regarding schedule, flight status, or airline policy; safe to auto-handle.",
                confidence=0.88,
                risk_level="low",
            )

        # General flight delay without missed connections
        if predicted_intent == "Flight delay":
            return PolicyDecision(
                action="AUTO_HANDLE",
                reason="Routine operational delay notification; auto-handle with flight status tracking and apology.",
                confidence=0.85,
                risk_level="low",
            )

        # Standard seat assignment / general questions
        if predicted_intent == "Seats and fares":
            return PolicyDecision(
                action="AUTO_HANDLE",
                reason="General seating/cabin policy question; auto-handle with self-service change guidance.",
                confidence=0.80,
                risk_level="low",
            )

        # Default fallback
        return PolicyDecision(
            action="AUTO_HANDLE",
            reason="Standard customer interaction matching established brand resolution patterns.",
            confidence=0.75,
            risk_level="low",
        )
