"""Tests for dataset loading and sampling."""

from __future__ import annotations

from pathlib import Path

from customer_support.data import (
    first_customer_messages,
    load_conversations,
    load_jsonl,
    split_indexed,
)


def _write_jsonl(tmp_path: Path, records: list[dict]) -> Path:
    path = tmp_path / "sample.jsonl"
    path.write_text(
        "\n".join(__import__("json").dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    return path


def test_load_jsonl(tmp_path: Path) -> None:
    path = _write_jsonl(tmp_path, [{"a": 1}, {"b": 2}])
    assert load_jsonl(path) == [{"a": 1}, {"b": 2}]


def test_load_jsonl_blank_lines_skipped(tmp_path: Path) -> None:
    path = tmp_path / "blank.jsonl"
    path.write_text('{"a": 1}\n\n{"b": 2}\n', encoding="utf-8")
    assert len(load_jsonl(path)) == 2


def test_first_customer_messages_picks_openers(tmp_path: Path) -> None:
    conversations = [
        {"conversation_id": "1", "messages": [{"role": "customer", "text": " hi "}]},
        {
            "conversation_id": "2",
            "messages": [
                {"role": "agent", "text": "first"},
                {"role": "customer", "text": "lost bag"},
            ],
        },
        {"conversation_id": "3", "messages": []},
    ]
    sampled = first_customer_messages(conversations, limit=5, seed=1)
    texts = {item["text"] for item in sampled}
    assert "hi" in texts and "lost bag" in texts
    assert len(sampled) == 2  # conversation 3 contributes nothing


def test_first_customer_messages_limit(tmp_path: Path) -> None:
    conversations = [
        {"conversation_id": str(i), "messages": [{"role": "customer", "text": f"text {i}"}]}
        for i in range(10)
    ]
    sampled = first_customer_messages(conversations, limit=3, seed=0)
    assert len(sampled) == 3


def test_first_customer_messages_reproducible() -> None:
    conversations = [
        {"conversation_id": str(i), "messages": [{"role": "customer", "text": f"t{i}"}]}
        for i in range(20)
    ]
    a = first_customer_messages(conversations, limit=8, seed=42)
    b = first_customer_messages(conversations, limit=8, seed=42)
    assert [item["conversation_id"] for item in a] == [item["conversation_id"] for item in b]


def test_split_indexed() -> None:
    train, test = split_indexed(100, test_fraction=0.2, seed=42)
    assert len(train) == 80 and len(test) == 20
    assert set(train).isdisjoint(set(test))
    assert sorted(train + test) == list(range(100))


def test_load_conversations_real_file() -> None:
    path = Path(__file__).resolve().parent.parent / "data" / "processed" / "conversations.jsonl"
    conversations = load_conversations(path)
    assert len(conversations) > 1000
    assert "messages" in conversations[0]
