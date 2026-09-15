"""LangGraph-powered AI Support Agent workflow for AmericanAir.

Orchestrates multi-stage agent reasoning:
1. Intent Classification (SOTA SetFit / Fine-Tuned Embedding + Linear Head)
2. Historical Resolution Retrieval (Grounded RAG from 12,443 real conversations)
3. Reply Drafting (Brand-grounded resolution synthesis)
4. Decision Policy (AUTO_HANDLE vs. ESCALATE with explicit justification)
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, TypedDict

import numpy as np
from langgraph.graph import END, StateGraph

from customer_support.agent.policy import SupportDecisionPolicy
from customer_support.retrieval.historical_store import HistoricalResolutionStore

logger = logging.getLogger(__name__)


def sanitize_grounding_text(text: str) -> str:
    """Clean historical resolution text by removing Twitter handles, legacy customer names, and artifacts."""
    if not text:
        return ""
    # Strip all @mentions (even repeated @@138000 or @AmericanAir)
    cleaned = re.sub(r"[@]+\w+\s*", "", text).strip()
    # Strip direct address names like ', Jasen and' or 'Jasen, ' or 'Hi Jasen,'
    cleaned = re.sub(r",\s+[A-Z][a-z]+(\s+and\b)", r"\1", cleaned)
    cleaned = re.sub(r"^[A-Z][a-z]+,\s*", "", cleaned)
    cleaned = re.sub(r",\s+[A-Z][a-z]+\s*([.!?])", r"\1", cleaned)
    cleaned = re.sub(r"\bHi\s+[A-Z][a-z]+,\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bThanks\s+[A-Z][a-z]+[!,\s]*", "", cleaned, flags=re.IGNORECASE)
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned.strip()


def try_llm_synthesis(
    customer_message: str,
    intent: str,
    grounding_facts: str,
    timeout: float = 3.5,
) -> str | None:
    """Attempt dynamic grounded reply generation via local Ollama LLM if available."""
    try:
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")
        prompt = (
            "You are an official American Airlines (@AmericanAir) customer support specialist.\n"
            "Draft a concise, empathetic, professional response (under 280 characters for Twitter) to the customer inquiry.\n"
            "Ground your answer strictly in the provided historical resolution facts. Do NOT hallucinate compensation or unverified policies.\n"
            "Never mention other customer names or old tweet IDs.\n"
            "If assistance with reservations, luggage, or rebooking is needed, invite the passenger to send a private DM with their 6-character record locator.\n\n"
            f"Customer Message: {customer_message}\n"
            f"Classified Intent: {intent}\n"
            f"Historical Grounding Knowledge: {grounding_facts}\n\n"
            "Drafted Reply:"
        )
        payload = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 75},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        res = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(res.read().decode("utf-8"))
        reply = data.get("response", "").strip().strip('"')
        if reply and len(reply) > 15:
            return sanitize_grounding_text(reply)
    except Exception:
        pass
    return None


class SupportAgentState(TypedDict):
    customer_message: str
    intent: str
    intent_confidence: float
    retrieved_resolutions: list[dict[str, Any]]
    draft_reply: str
    action: str  # "AUTO_HANDLE" | "ESCALATE"
    action_reason: str


class SupportAgentWorkflow:
    """End-to-end support agent graph."""

    def __init__(
        self,
        classifier: Any,
        retrieval_store: HistoricalResolutionStore,
        policy: SupportDecisionPolicy | None = None,
    ) -> None:
        self.classifier = classifier
        self.retrieval_store = retrieval_store
        self.policy = policy or SupportDecisionPolicy()
        self.graph = self._build_graph()

    def _classify_node(self, state: SupportAgentState) -> dict[str, Any]:
        msg = state["customer_message"]
        try:
            # Predict intent
            pred = self.classifier.predict([msg])[0]
            intent = str(pred)
            confidence = 0.85
            if hasattr(self.classifier, "predict_proba"):
                probs = self.classifier.predict_proba([msg])[0]
                confidence = float(max(probs))
            elif hasattr(self.classifier, "decision_function"):
                scores = self.classifier.decision_function([msg])[0]
                # Temperature-scaled softmax approximation for multiclass SVM margins
                temperature = 2.5
                scaled = scores * temperature
                exp_scores = np.exp(scaled - np.max(scaled))
                confidence = float(np.max(exp_scores) / np.sum(exp_scores))
        except Exception as e:
            logger.warning(f"Classification failed ({e}); falling back to Flight information.")
            intent = "Flight information"
            confidence = 0.50

        return {"intent": intent, "intent_confidence": confidence}

    def _retrieve_node(self, state: SupportAgentState) -> dict[str, Any]:
        msg = state["customer_message"]
        resolutions = self.retrieval_store.retrieve(msg, top_k=2)
        return {"retrieved_resolutions": resolutions}

    def _draft_node(self, state: SupportAgentState) -> dict[str, Any]:
        msg = state["customer_message"]
        text = msg.lower()
        intent = state["intent"]
        retrieved = state.get("retrieved_resolutions", [])

        top_resolution = retrieved[0]["agent_resolution"] if retrieved else ""
        cleaned_historical = sanitize_grounding_text(top_resolution)

        # Failure Mode 1: Sarcastic praise disguising severe operational delay/disruption
        if re.search(
            r"\b(thank you|thanks|top notch|great service|stellar|wonderful|awesome|love)\b.*\b(\d+\+?\s*hours?|hours?|tarmac|no ac|no air|no food|no water|stranded|stuck|cancelled|nightmare|disaster)\b",
            text,
        ) or re.search(
            r"\b(\d+\+?\s*hours?|hours?|tarmac|no ac|no air|no food|no water|stranded|stuck|cancelled|nightmare|disaster)\b.*\b(thank you|thanks|top notch|great service|stellar|wonderful|awesome|love)\b",
            text,
        ):
            reply = "We sincerely apologize for the severe delay and difficult conditions you experienced. Please DM us your 6-character record locator and flight number so our team can immediately look into this for you."
            return {"draft_reply": reply}

        # Failure Mode 3: In-cabin lost and found items
        if (
            re.search(
                r"\b(left|forgot|lost)\b.*\b(seat|pocket|seatback|overhead|plane|aircraft|cabin|onboard|board)\b",
                text,
            )
            or "lost and found" in text
        ):
            reply = "Items left on board our aircraft are collected by our airport team. Please submit an official report at https://www.aa.com/lostandfound or speak with the Baggage Service Office at your arrival airport with your flight and seat details."
            return {"draft_reply": reply}

        # Failure Mode 5: Loyalty milestone recognition
        if re.search(
            r"\b(platinum|exec\s*plat|executive\s*platinum|conciergekey|gold status|million miler|status milestone)\b",
            text,
        ) and ("made it" in text or "finally" in text or "hit" in text or "earned" in text):
            reply = "Congratulations on reaching your status milestone! Thank you for your continued loyalty and dedication to flying with us. Welcome to the elite tier! #AATeam"
            return {"draft_reply": reply}

        # Attempt dynamic LLM grounded synthesis if Ollama is available
        if cleaned_historical:
            llm_reply = try_llm_synthesis(msg, intent, cleaned_historical)
            if llm_reply:
                return {"draft_reply": llm_reply}

        # Grounded brand synthesis fallback tailored to AmericanAir voice
        if intent == "Positive experience":
            reply = "We truly appreciate the love and your loyalty! We'll pass your kind words along to our team. #AATeam"
        elif intent == "Social acknowledgement":
            reply = "Thanks for connecting with us! Wishing you safe and pleasant travels. #AATeam"
        elif intent == "Baggage issues":
            reply = "We're so sorry for the luggage issue. Please DM us your 6-character record locator and bag tag claim number so our baggage team can track this immediately."
        elif intent == "Flight delay":
            reply = "We sincerely apologize for the delay to your travels today. Please DM your record locator and we will check updated departure and gate information for you."
        elif intent == "Disruption recovery":
            reply = "We understand how disruptive this is to your plans and sincerely apologize. Please DM your 6-character confirmation code so our rebooking team can review available options."
        elif intent == "Seats and fares":
            reply = "We'd be glad to look into your seating and reservation details. Please DM us your record locator so we can review your cabin options."
        elif intent == "Service complaint":
            reply = "We hold our service to high standards and apologize for your frustrating experience today. Please DM us your flight details and contact info so our team can follow up."
        elif any(k in text for k in ("snack", "food", "hungry", "eat", "drink", "beverage", "cookie")):
            url_match = re.search(r"https?://\S+", cleaned_historical)
            url_part = f": {url_match.group(0)}" if url_match else "."
            reply = f"We serve complimentary Biscoff cookies and drinks on board, and also have a wide selection of snacks available for purchase{url_part} #AATeam"
        elif cleaned_historical:
            reply = cleaned_historical
        else:
            reply = "We're here to help! Please send us a DM with your 6-character record locator and we'd be glad to take a closer look."

        return {"draft_reply": reply}

    def _policy_node(self, state: SupportAgentState) -> dict[str, Any]:
        msg = state["customer_message"]
        intent = state["intent"]
        confidence = state.get("intent_confidence", 1.0)
        retrieved = state.get("retrieved_resolutions", [])
        similarity = retrieved[0]["score"] if retrieved else 0.5

        decision = self.policy.evaluate(
            customer_message=msg,
            predicted_intent=intent,
            intent_confidence=confidence,
            retrieval_similarity=similarity,
        )

        return {
            "action": decision.action,
            "action_reason": decision.reason,
        }

    def _build_graph(self) -> Any:
        workflow = StateGraph(SupportAgentState)

        workflow.add_node("classify", self._classify_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("draft", self._draft_node)
        workflow.add_node("policy", self._policy_node)

        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "retrieve")
        workflow.add_edge("retrieve", "draft")
        workflow.add_edge("draft", "policy")
        workflow.add_edge("policy", END)

        return workflow.compile()

    def run(self, customer_message: str) -> SupportAgentState:
        """Run the end-to-end support agent workflow for an incoming customer message."""
        initial_state: SupportAgentState = {
            "customer_message": customer_message,
            "intent": "",
            "intent_confidence": 0.0,
            "retrieved_resolutions": [],
            "draft_reply": "",
            "action": "AUTO_HANDLE",
            "action_reason": "",
        }
        return self.graph.invoke(initial_state)


def build_support_agent(
    classifier: Any,
    conversations_path: str | Path,
    device: str | None = None,
    max_records: int = 2000,
) -> SupportAgentWorkflow:
    """Factory function to build a compiled LangGraph support agent."""
    retrieval_store = HistoricalResolutionStore(
        conversations_path, max_records=max_records, device=device
    )
    policy = SupportDecisionPolicy(confidence_threshold=0.20)
    return SupportAgentWorkflow(
        classifier=classifier, retrieval_store=retrieval_store, policy=policy
    )
