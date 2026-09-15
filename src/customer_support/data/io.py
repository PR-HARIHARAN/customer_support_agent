"""Dataset loading and sampling utilities."""

from __future__ import annotations

import json
import random
from pathlib import Path


def load_jsonl(path: str | Path) -> list[dict]:
    """Load newline-delimited JSON into a list of dicts.

    Skips blank lines and raises a clear error on malformed JSON (with the
    offending line number) instead of failing silently.
    """
    records: list[dict] = []
    with Path(path).open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}") from error
    return records


def load_conversations(path: str | Path) -> list[dict]:
    """Load reconstructed support conversations (``conversations.jsonl``)."""
    return load_jsonl(path)


def first_customer_messages(conversations: list[dict], limit: int, seed: int = 42) -> list[dict]:
    """Deterministically sample customer messages from conversations.

    Each conversation contributes its first customer message (the opening
    request), up to ``limit`` messages total. Conversations are shuffled with
    ``seed`` before selection so the sample is reproducible.
    """
    shuffled = list(conversations)
    random.Random(seed).shuffle(shuffled)

    sampled: list[dict] = []
    for conversation in shuffled:
        if len(sampled) >= limit:
            break
        for message in conversation.get("messages", []):
            if str(message.get("role", "")).lower() == "customer":
                sampled.append(
                    {
                        "conversation_id": str(conversation.get("conversation_id", "")),
                        "tweet_id": str(message.get("tweet_id", "")),
                        "text": message.get("text", "").strip(),
                        "created_at": message.get("created_at", ""),
                    }
                )
                break
    return sampled


def split_indexed(n: int, test_fraction: float, seed: int = 42) -> tuple[list[int], list[int]]:
    """Split ``range(n)`` into (train, test) index lists with a fixed seed."""
    rng = random.Random(seed)
    indices = list(range(n))
    rng.shuffle(indices)
    cutoff = max(1, int(n * (1.0 - test_fraction)))
    return indices[:cutoff], indices[cutoff:]


__all__ = [
    "load_jsonl",
    "load_conversations",
    "first_customer_messages",
    "split_indexed",
]
