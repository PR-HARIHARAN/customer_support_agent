"""Ragas and automated evaluation metrics for grounded reply quality."""

from __future__ import annotations

import numpy as np

from customer_support.embeddings import TextEmbedder


class GroundedReplyEvaluator:
    """Evaluates RAG reply faithfulness, answer relevance, and historical semantic agreement."""

    def __init__(self, embedder: TextEmbedder | None = None) -> None:
        self.embedder = embedder or TextEmbedder("sentence-transformers/all-MiniLM-L6-v2")

    def evaluate(
        self,
        query: str,
        reply: str,
        contexts: list[str],
        reference: str = "",
    ) -> dict[str, float]:
        """Convenience alias matching evaluate_sample signature."""
        return self.evaluate_sample(
            customer_query=query,
            retrieved_contexts=contexts,
            generated_reply=reply,
            reference_reply=reference,
        )

    def evaluate_sample(
        self,
        customer_query: str,
        retrieved_contexts: list[str],
        generated_reply: str,
        reference_reply: str = "",
    ) -> dict[str, float]:
        """Compute semantic similarity, relevance, and grounding overlap."""
        # 1. Answer Relevancy (Cosine similarity between query and generated reply)
        vec_q = self.embedder.encode([customer_query])[0]
        vec_r = self.embedder.encode([generated_reply])[0]
        norm_q = float(np.linalg.norm(vec_q) + 1e-12)
        norm_r = float(np.linalg.norm(vec_r) + 1e-12)
        relevancy = float(np.dot(vec_q, vec_r) / (norm_q * norm_r))

        # 2. Faithfulness / Grounding against retrieved historical resolution
        if retrieved_contexts:
            vec_ctx = self.embedder.encode(retrieved_contexts)
            ctx_sims = []
            for c in vec_ctx:
                norm_c = float(np.linalg.norm(c) + 1e-12)
                ctx_sims.append(float(np.dot(vec_r, c) / (norm_r * norm_c)))
            faithfulness = max(ctx_sims) if ctx_sims else 0.5
        else:
            faithfulness = 0.5

        # 3. Semantic similarity against reference agent response (if available)
        if reference_reply:
            vec_ref = self.embedder.encode([reference_reply])[0]
            norm_ref = float(np.linalg.norm(vec_ref) + 1e-12)
            semantic_agreement = float(np.dot(vec_r, vec_ref) / (norm_r * norm_ref))
        else:
            semantic_agreement = faithfulness

        return {
            "answer_relevancy": round(max(0.0, min(1.0, (relevancy + 1.0) / 2.0)), 4),
            "faithfulness": round(max(0.0, min(1.0, (faithfulness + 1.0) / 2.0)), 4),
            "semantic_agreement": round(max(0.0, min(1.0, (semantic_agreement + 1.0) / 2.0)), 4),
        }
