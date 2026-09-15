"""Grounded historical resolution store for AmericanAir Twitter support.

Indexes historical (customer_query, agent_resolution) pairs from conversations.jsonl
so the agent can retrieve how real human agents historically resolved similar issues.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from customer_support.embeddings import TextEmbedder

logger = logging.getLogger(__name__)


class HistoricalResolutionStore:
    """Vector-indexed repository of historical customer-agent resolution pairs."""

    def __init__(
        self,
        conversations_path: Path | str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Path | str | None = None,
        max_records: int = 1500,
        device: str | None = None,
    ) -> None:
        self.conversations_path = Path(conversations_path)
        self.embedding_model = embedding_model
        self.max_records = max_records
        self.device = device
        self.cache_dir = (
            Path(cache_dir) if cache_dir else self.conversations_path.parent / "retrieval_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.records: list[dict[str, Any]] = []
        self.embeddings: np.ndarray | None = None
        self.embedder = TextEmbedder(embedding_model, device=device)

        self._initialize_store()

    def _initialize_store(self) -> None:
        """Load or build the historical resolution index."""
        records_cache = self.cache_dir / "historical_records.json"
        embeds_cache = self.cache_dir / "historical_embeddings.npy"

        if records_cache.exists() and embeds_cache.exists():
            try:
                with records_cache.open(encoding="utf-8") as f:
                    self.records = json.load(f)
                self.embeddings = np.load(embeds_cache)
                if len(self.records) == len(self.embeddings):
                    logger.info(f"Loaded {len(self.records)} cached historical resolution pairs.")
                    return
            except Exception as exc:
                logger.warning(f"Cache load failed ({exc}); rebuilding index from source.")

        self._build_from_conversations()
        try:
            with records_cache.open("w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            np.save(embeds_cache, self.embeddings)
            logger.info(f"Cached {len(self.records)} pairs to {self.cache_dir}")
        except Exception as exc:
            logger.warning(f"Failed to write cache ({exc}). Continuing with in-memory index.")

    def _build_from_conversations(self) -> None:
        """Extract customer inquiry -> agent resolution pairs from conversations.jsonl."""
        extracted: list[dict[str, Any]] = []

        if not self.conversations_path.exists():
            raise FileNotFoundError(f"Conversations file not found: {self.conversations_path}")

        with self.conversations_path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                conv = json.loads(line)
                messages = conv.get("messages", [])

                # Find first customer message and first subsequent agent reply
                cust_text = ""
                agent_text = ""

                for msg in messages:
                    role = msg.get("role", "").lower()
                    text = msg.get("text", "").strip()
                    if role == "customer" and not cust_text:
                        cust_text = text
                    elif role == "agent" and cust_text and not agent_text:
                        agent_text = text
                        break

                if len(cust_text) >= 12 and len(agent_text) >= 15:
                    extracted.append(
                        {
                            "conversation_id": str(conv.get("conversation_id", "")),
                            "customer_query": cust_text,
                            "agent_resolution": agent_text,
                            "coarse_intent": conv.get("intent", "General"),
                        }
                    )
                if len(extracted) >= self.max_records:
                    break

        if not extracted:
            raise ValueError(
                f"No valid customer-agent pairs extracted from {self.conversations_path}"
            )

        self.records = extracted
        queries = [r["customer_query"] for r in self.records]
        raw_embeds = self.embedder.encode(queries)
        norms = np.linalg.norm(raw_embeds, axis=1, keepdims=True)
        self.embeddings = raw_embeds / np.maximum(norms, 1e-12)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Retrieve the most relevant historical customer resolutions for a query.

        Returns list of dicts with keys: conversation_id, customer_query, agent_resolution, score.
        """
        if not query or self.embeddings is None or len(self.records) == 0:
            return []

        q_vec = self.embedder.encode([query])
        q_norm = q_vec / np.maximum(np.linalg.norm(q_vec, axis=1, keepdims=True), 1e-12)

        # Cosine similarities
        scores = np.dot(self.embeddings, q_norm.T).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            rec = dict(self.records[idx])
            rec["score"] = float(round(scores[idx], 4))
            results.append(rec)
        return results
