"""Embedding utilities for the reproducible pipeline.

Thin wrapper around ``sentence-transformers`` so the rest of the pipeline can
swap embedding models (MiniLM, E5-small, BGE) without changing call sites.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


class TextEmbedder:
    """Encoder that maps lists of strings to L2-normalised float32 vectors."""

    def __init__(self, model_name: str, batch_size: int = 64, device: str | None = None) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:  # pragma: no cover - guarded on purpose
            raise ImportError(
                "sentence-transformers is required; install it with `uv sync`."
            ) from error

        self.model_name = model_name
        self.batch_size = batch_size
        self._model = SentenceTransformer(model_name, device=device)

    @property
    def dimension(self) -> int:
        """Embedding dimensionality for the wrapped model."""
        if hasattr(self._model, "get_embedding_dimension"):
            return int(self._model.get_embedding_dimension())
        return int(self._model.get_sentence_embedding_dimension())  # older API

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return an ``(N, D)`` float32 matrix of normalised embeddings."""
        import numpy as np

        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        vectors = self._model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        array = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(array, axis=1, keepdims=True)
        return array / np.maximum(norms, 1e-12)


__all__ = ["TextEmbedder"]
