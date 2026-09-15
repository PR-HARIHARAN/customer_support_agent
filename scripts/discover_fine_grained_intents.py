"""Discover fine-grained sub-intents inside each coarse cluster (PolyAI/Banking77 style).

Pipeline per coarse cluster (default 12 clusters, ids 0..11):
  1. Centroid sampling: 15 closest to centroid (representative) + 10 furthest
     (boundary / potential noise-overlap).
  2. TF-IDF snapshot: top-10 distinctive unigrams+bigrams (mean-TF-IDF minus global mean).
  3. LLM taxonomy generation: keywords + 25 samples -> snake_case sub-intents,
     per-query mapping, OOD / wrong-cluster flags.
  4. Output: JSON + Markdown report structured by cluster_id.

Inputs (produced by notebook 004):
  --input-jsonl : data/processed/customer_messages_with_candidate_intents_v1.jsonl
  --faiss-dir   : data/faiss_customer_message  (index.faiss + metadata.json)
Fallback: if FAISS is unavailable, embeddings are recomputed from the
  cluster labels alone is impossible, so the script exits with a clear error
  (centroid sampling *requires* vectors). No silent TF-IDF-only fallback.

LLM backends (lazy-imported so dry-run / ollama need no cloud SDKs):
  --llm-provider openai     ->  pip install openai ; env OPENAI_API_KEY
  --llm-provider anthropic  ->  pip install anthropic ; env ANTHROPIC_API_KEY
  --llm-provider ollama     ->  local Ollama, no API key, no extra dep
                                (uses stdlib urllib against http://localhost:11434).
                                Recommended local models: qwen2.5:7b (stable JSON),
                                qwen3:8b (stronger but wraps output in <think> tags,
                                auto-stripped), llama3.2, gemma3.
  --dry-run                 ->  no LLM call; deterministic heuristic stub
                                (useful for CI / cost check).

Example:
  python scripts/discover_fine_grained_intents.py --dry-run --limit-clusters 2
  python scripts/discover_fine_grained_intents.py --llm-provider ollama --model qwen2.5:7b --limit-clusters 2
  python scripts/discover_fine_grained_intents.py --llm-provider openai --model gpt-4o
  python scripts/discover_fine_grained_intents.py --llm-provider anthropic --model claude-sonnet-4-20250514

Outputs (in --output-dir):
  fine_grained_taxonomy.json   machine-readable result
  fine_grained_report.md       human-readable report
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

log = logging.getLogger("fine_grained")

OOD_LABEL = "out_of_distribution_noise"
OTHER_CLUSTER_LABEL = "belongs_to_other_cluster"

# ----------------------------------------------------------------------------
# LLM prompt (Banking77 granularity for airline support)
# ----------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are an expert NLP taxonomist designing customer-support intent schemas "
    "in the style of PolyAI Banking77: fine-grained, mutually exclusive, actionable, "
    "and narrow enough that a classifier can separate them, but broad enough that "
    "each intent gets sufficient training data (>= ~50 examples in production). "
    "You work with American Airlines Twitter support queries."
)


def build_user_prompt(
    cluster_id: int,
    coarse_intent: str,
    coarse_sub_intent: str,
    keywords: list[str],
    representative: list[dict],
    boundary: list[dict],
) -> str:
    def fmt(samples: list[dict], tag: str) -> str:
        lines = []
        for i, s in enumerate(samples, 1):
            lines.append(f"[{tag}{i} uid={s['message_uid']}] {s['customer_text']}")
        return "\n".join(lines)

    return f"""You are refining coarse cluster {cluster_id} ("{coarse_intent} / {coarse_sub_intent}") into fine-grained sub-intents.

TF-IDF distinctive keywords (unigrams+bigrams) for this cluster:
{", ".join(keywords)}

--- 15 REPRESENTATIVE queries (closest to centroid, most typical) ---
{fmt(representative, "R")}

--- 10 BOUNDARY queries (furthest from centroid; likely noise, overlap, or multi-intent) ---
{fmt(boundary, "B")}

Tasks:
1. Propose 3-8 fine-grained sub-intents that cover the REPRESENTATIVE queries.
   Rules:
   - snake_case, e.g. lost_baggage_claim, seat_upgrade_request, flight_delay_compensation
   - each with a 1-sentence definition + 2-3 prototypical phrasings
   - mutually exclusive; prefer Banking77-level specificity over vagueness
     (BAD: "baggage_issue"; GOOD: "lost_baggage_claim" vs "damaged_baggage_report" vs "carry_on_gate_check_complaint")
   - do NOT create one intent per query; merge near-duplicates
2. Map EACH of the 25 queries (R1..R15, B1..B10) to exactly one label:
   - one of your proposed snake_case intents, OR
   - "{OOD_LABEL}" (gibberish, mentions-only, photo-share, empty thanks with no problem), OR
   - "{OTHER_CLUSTER_LABEL}" (clearly belongs to a different coarse topic, say which in `note`)
3. Recommend SPLIT (this cluster should become N intents), MERGE (some proposed intents overlap),
   or KEEP (cluster is already coherent), with a 1-2 sentence justification.
4. List 2-4 edge cases / confusable pairs a classifier will struggle with.

Return STRICT JSON only (no markdown fences, no commentary) with this schema:
{{
  "cluster_id": {cluster_id},
  "coarse_intent": "{coarse_intent}",
  "proposed_sub_intents": [
    {{"name": "snake_case", "definition": "...", "prototypical_phrases": ["...", "..."]}}
  ],
  "query_mapping": [
    {{"sample_id": "R1", "message_uid": "...", "assigned_intent": "...", "confidence": "high|medium|low", "note": "..."}}
  ],
  "recommendation": {{"action": "SPLIT|MERGE|KEEP", "justification": "..."}},
  "edge_cases": ["..."]
}}"""


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------


def load_messages(input_jsonl: Path) -> pd.DataFrame:
    df = pd.read_json(input_jsonl, lines=True, dtype=False, encoding="utf-8")
    required = {"message_uid", "customer_text", "candidate_cluster"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{input_jsonl} missing columns: {missing}")
    # candidate_cluster may be str ("11") — coerce to int for grouping
    df["coarse_cluster"] = (
        pd.to_numeric(df["candidate_cluster"], errors="coerce").fillna(-1).astype(int)
    )
    df["customer_text"] = df["customer_text"].fillna("").astype(str)
    for col in ("candidate_intent", "candidate_sub_intent", "candidate_split"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
    return df


def load_embedding_matrix(faiss_dir: Path) -> tuple[np.ndarray, list[str]]:
    """Return (matrix [N, D], message_uids in FAISS order) via `faiss.read_index`."""
    try:
        import faiss  # lazy: only needed for real runs
    except ImportError as exc:
        raise ImportError("faiss-cpu is required (pip install faiss-cpu).") from exc
    index_path = faiss_dir / "index.faiss"
    meta_path = faiss_dir / "metadata.json"
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found: {index_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"FAISS metadata not found: {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    uids: list[str] = [str(u) for u in meta.get("message_uids", [])]
    index = faiss.read_index(str(index_path))
    n, d = index.ntotal, index.d
    if uids and len(uids) != n:
        raise ValueError(f"metadata has {len(uids)} uids but index has {n} vectors.")
    mat = np.zeros((n, d), dtype=np.float32)
    for i in range(n):  # reconstruct is per-vector; batch loop with progress
        mat[i] = index.reconstruct(i)
        if (i + 1) % 15000 == 0:
            log.info("reconstructed %d/%d vectors", i + 1, n)
    if not np.isfinite(mat).all():
        raise ValueError("Embedding matrix contains NaN/Inf.")
    return mat, uids


def align_embeddings_to_df(
    df: pd.DataFrame, matrix: np.ndarray, faiss_uids: list[str]
) -> np.ndarray:
    """Reorder FAISS matrix rows to match df order via message_uid."""
    if not faiss_uids:  # pragma: no cover — legacy stores without uid list
        if len(df) != matrix.shape[0]:
            raise ValueError("Cannot align: no uid list and row counts differ.")
        log.warning("No uid list in FAISS metadata; assuming row order matches JSONL.")
        return matrix
    lookup = {uid: i for i, uid in enumerate(faiss_uids)}
    missing = [u for u in df["message_uid"].astype(str) if u not in lookup]
    if missing:
        raise ValueError(f"{len(missing)} message_uids have no FAISS vector, e.g. {missing[:3]}")
    order = np.array([lookup[u] for u in df["message_uid"].astype(str)], dtype=np.int64)
    return matrix[order]


# ----------------------------------------------------------------------------
# Step 1 — centroid sampling / Step 2 — TF-IDF snapshot
# ----------------------------------------------------------------------------


def l2_normalize(mat: np.ndarray) -> np.ndarray:
    return mat / np.maximum(np.linalg.norm(mat, axis=1, keepdims=True), 1e-12)


def sample_cluster(
    idx: np.ndarray, Xn: np.ndarray, n_close: int = 15, n_far: int = 10
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (close_idx, far_idx, close_dist, far_dist) positions into df."""
    centroid = Xn[idx].mean(axis=0)
    centroid /= max(np.linalg.norm(centroid), 1e-12)
    dists = np.linalg.norm(Xn[idx] - centroid, axis=1)  # euclidean on L2-normed = cosine
    order = np.argsort(dists, kind="stable")
    return (
        idx[order[:n_close]],
        idx[order[-n_far:][::-1]],
        dists[order[:n_close]],
        dists[order[-n_far:][::-1]],
    )


def distinctive_terms(texts: pd.Series, labels: pd.Series, top_n: int = 10) -> dict[int, list[str]]:
    """Mean-TF-IDF per cluster minus global mean (c-TF-IDF lite)."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=5, max_features=20000)
    X = vec.fit_transform(texts.fillna("").astype(str))
    terms = np.array(vec.get_feature_names_out())
    global_mean = np.asarray(X.mean(axis=0)).ravel()
    out: dict[int, list[str]] = {}
    for cid in sorted(labels.unique()):
        mask = (labels == cid).to_numpy()
        if mask.sum() == 0:
            out[int(cid)] = []
            continue
        local_mean = np.asarray(X[mask].mean(axis=0)).ravel()
        score = local_mean - global_mean
        top = np.argsort(score, kind="stable")[-top_n:][::-1]
        out[int(cid)] = [str(terms[i]) for i in top if score[i] > 0]
    return out


# ----------------------------------------------------------------------------
# Step 3 — LLM calls
# ----------------------------------------------------------------------------


def extract_json(text: str) -> dict:
    """Strip code fences / <think> blocks and parse the first {...} block."""
    cleaned = (text or "").strip()
    # qwen3-style reasoning wrapper: <think>...</think> + answer
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.DOTALL).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def call_ollama(
    prompt_sys: str,
    prompt_user: str,
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    temperature: float = 0.2,
    num_ctx: int = 8192,
    timeout_s: int = 300,
    retries: int = 2,
) -> dict:
    """Local Ollama chat via stdlib urllib — no extra dependency, no API key.

    Uses the native /api/chat endpoint with format=json so the model is forced
    toward strict JSON. Tested with qwen2.5:7b / qwen3:8b / llama3.2 / gemma3.
    """
    import urllib.request

    url = host.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "num_ctx": num_ctx},
        "messages": [
            {"role": "system", "content": prompt_sys},
            {"role": "user", "content": prompt_user},
        ],
    }
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = (body.get("message") or {}).get("content", "")
            if not content:
                raise RuntimeError(f"Empty content from Ollama: {str(body)[:300]}")
            return extract_json(content)
        except Exception as exc:  # noqa: BLE001 — retry once (cold model load)
            last = exc
            log.warning("Ollama attempt %d failed: %s", attempt + 1, exc)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Ollama call failed (model={model!r} host={host!r}): {last}")


def call_openai(prompt_sys: str, prompt_user: str, model: str, retries: int = 3) -> dict:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError("pip install openai  (and set OPENAI_API_KEY).") from exc
    client = OpenAI()  # reads OPENAI_API_KEY from env
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt_sys},
                    {"role": "user", "content": prompt_user},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            return extract_json(resp.choices[0].message.content or "")
        except Exception as exc:  # noqa: BLE001 — retry transient API errors
            last = exc
            log.warning("OpenAI attempt %d failed: %s", attempt + 1, exc)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"OpenAI call failed after {retries} attempts: {last}")


def call_anthropic(prompt_sys: str, prompt_user: str, model: str, retries: int = 3) -> dict:
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError("pip install anthropic  (and set ANTHROPIC_API_KEY).") from exc
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=2500,
                temperature=0.2,
                system=prompt_sys,
                messages=[{"role": "user", "content": prompt_user}],
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            return extract_json(text)
        except Exception as exc:  # noqa: BLE001
            last = exc
            log.warning("Anthropic attempt %d failed: %s", attempt + 1, exc)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Anthropic call failed after {retries} attempts: {last}")


def heuristic_stub(
    cluster_id: int, coarse_intent: str, representative: list[dict], boundary: list[dict]
) -> dict:
    """Deterministic no-API fallback so --dry-run still exercises the full pipeline."""
    base = re.sub(r"\W+", "_", coarse_intent.lower()).strip("_") or f"cluster_{cluster_id}"
    intents = [
        {
            "name": f"{base}_core",
            "definition": f"Typical {coarse_intent} case.",
            "prototypical_phrases": [],
        },
        {
            "name": f"{base}_followup",
            "definition": "Follow-up / detail-seeking variant.",
            "prototypical_phrases": [],
        },
        {
            "name": f"{base}_complaint",
            "definition": "Complaint-flavoured variant.",
            "prototypical_phrases": [],
        },
    ]
    mapping: list[dict] = []
    for i, s in enumerate(representative, 1):
        mapping.append(
            {
                "sample_id": f"R{i}",
                "message_uid": s["message_uid"],
                "assigned_intent": intents[i % 3]["name"]
                if len(s["customer_text"]) > 30
                else OOD_LABEL,
                "confidence": "low",
                "note": "dry-run heuristic; replace with LLM call",
            }
        )
    for i, s in enumerate(boundary, 1):
        mapping.append(
            {
                "sample_id": f"B{i}",
                "message_uid": s["message_uid"],
                "assigned_intent": OTHER_CLUSTER_LABEL
                if len(s["customer_text"]) < 15
                else intents[0]["name"],
                "confidence": "low",
                "note": "dry-run heuristic; replace with LLM call",
            }
        )
    return {
        "cluster_id": cluster_id,
        "coarse_intent": coarse_intent,
        "proposed_sub_intents": intents,
        "query_mapping": mapping,
        "recommendation": {
            "action": "SPLIT",
            "justification": "dry-run placeholder — run with --llm-provider for real taxonomy.",
        },
        "edge_cases": ["dry-run: no LLM judgement available"],
    }


def validate_result(result: dict, n_expected: int = 25) -> list[str]:
    """Return list of warnings (empty = clean). Lenient by design for small local models."""
    warnings: list[str] = []
    names = {i.get("name") for i in result.get("proposed_sub_intents", [])}
    names |= {OOD_LABEL, OTHER_CLUSTER_LABEL}
    mapping = result.get("query_mapping", [])
    if len(mapping) != n_expected:
        warnings.append(f"expected {n_expected} mapped queries, got {len(mapping)}")
    seen_ids = set()
    for m in mapping:
        m.setdefault("note", "")
        m.setdefault("confidence", "low")
        seen_ids.add(m.get("sample_id"))
        if m.get("assigned_intent") not in names:
            warnings.append(f"{m.get('sample_id')}: unknown intent {m.get('assigned_intent')!r}")
        if m.get("confidence") not in {"high", "medium", "low"}:
            warnings.append(f"{m.get('sample_id')}: bad confidence {m.get('confidence')!r}")
            m["confidence"] = "low"
    expected_ids = {f"R{i}" for i in range(1, 16)} | {f"B{i}" for i in range(1, 11)}
    if seen_ids and seen_ids != expected_ids:
        warnings.append(
            f"sample_id set differs: missing={sorted(expected_ids - seen_ids)[:5]} extra={sorted(seen_ids - expected_ids)[:5]}"
        )
    for i in result.get("proposed_sub_intents", []):
        if not re.fullmatch(r"[a-z][a-z0-9_]*", str(i.get("name", ""))):
            warnings.append(f"intent name not snake_case: {i.get('name')!r}")
    if result.get("recommendation", {}).get("action") not in {"SPLIT", "MERGE", "KEEP"}:
        warnings.append("recommendation.action must be SPLIT|MERGE|KEEP")
    return warnings


# ----------------------------------------------------------------------------
# Step 4 — reports
# ----------------------------------------------------------------------------


def write_markdown(results: list[dict], samples: dict[int, dict], out_path: Path) -> None:
    lines = [
        "# Fine-grained intent discovery (per coarse cluster)",
        "",
        f"Clusters: {len(results)} | samples/cluster: 15 representative + 10 boundary | "
        "Granularity target: PolyAI/Banking77.",
        "",
    ]
    for res in sorted(results, key=lambda r: r.get("cluster_id", 0)):
        cid = res.get("cluster_id")
        smp = samples.get(cid, {})
        lines += [
            f"## Cluster {cid} — {res.get('coarse_intent', '')}",
            f"*Coarse sub-intent:* {smp.get('coarse_sub_intent', '')} | "
            f"*Size:* {smp.get('cluster_size', '?')} | "
            f"*Keywords:* {', '.join(smp.get('keywords', []))}",
            "",
            "### Proposed sub-intents",
        ]
        for intent in res.get("proposed_sub_intents", []):
            lines.append(f"- `{intent.get('name')}` — {intent.get('definition', '')}")
            for p in intent.get("prototypical_phrases", [])[:3]:
                lines.append(f"  - e.g. _{p}_")
        lines += ["", "### Query mapping (25)"]
        for m in res.get("query_mapping", []):
            flag = " 🚩" if m.get("assigned_intent") in (OOD_LABEL, OTHER_CLUSTER_LABEL) else ""
            lines.append(
                f"- **{m.get('sample_id')}** `{m.get('message_uid')}` → "
                f"`{m.get('assigned_intent')}` ({m.get('confidence', 'low')}){flag} — {m.get('note', '')}"
            )
        rec = res.get("recommendation", {})
        lines += [
            "",
            f"### Recommendation: **{rec.get('action')}**",
            f"{rec.get('justification', '')}",
            "",
            "### Edge cases",
        ]
        for e in res.get("edge_cases", []):
            lines.append(f"- {e}")
        if res.get("_warnings"):
            lines.append("")
            lines.append(f"> Warnings: {'; '.join(res['_warnings'])}")
        lines += ["", "---", ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fine-grained sub-intent discovery per coarse cluster.")
    p.add_argument(
        "--input-jsonl",
        type=Path,
        default=Path("data/processed/customer_messages_with_candidate_intents_v1.jsonl"),
    )
    p.add_argument("--faiss-dir", type=Path, default=Path("data/faiss_customer_message"))
    p.add_argument("--output-dir", type=Path, default=Path("data/processed/fine_grained_v1"))
    p.add_argument("--llm-provider", choices=["openai", "anthropic", "ollama"], default="ollama")
    p.add_argument(
        "--model",
        default="",
        help="LLM model. Defaults: gpt-4o (openai), claude-sonnet-4-20250514 (anthropic), qwen2.5:7b (ollama).",
    )
    p.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama host (default http://localhost:11434).",
    )
    p.add_argument(
        "--ollama-num-ctx",
        type=int,
        default=8192,
        help="Ollama num_ctx (prompt is ~3-4k tokens; 8192 is safe).",
    )
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--dry-run", action="store_true", help="Skip API calls; heuristic stub.")
    p.add_argument(
        "--limit-clusters", type=int, default=0, help="Only process first N clusters (0=all)."
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    np.random.seed(args.seed)

    defaults = {"openai": "gpt-4o", "anthropic": "claude-sonnet-4-20250514", "ollama": "qwen2.5:7b"}
    if not args.model:
        args.model = defaults[args.llm_provider]

    if not args.dry_run and args.llm_provider in ("openai", "anthropic"):
        key = "OPENAI_API_KEY" if args.llm_provider == "openai" else "ANTHROPIC_API_KEY"
        if not os.environ.get(key):
            log.error(
                "Missing %s in environment. Set it or use --dry-run / --llm-provider ollama.", key
            )
            return 2

    log.info("Loading messages: %s", args.input_jsonl)
    df = load_messages(args.input_jsonl)
    log.info("Loading embeddings: %s", args.faiss_dir)
    matrix, faiss_uids = load_embedding_matrix(args.faiss_dir)
    Xn = l2_normalize(align_embeddings_to_df(df, matrix, faiss_uids).astype(np.float64))
    log.info("Aligned %d vectors (%d-d) to %d messages", *Xn.shape, len(df))

    cluster_ids = sorted(df["coarse_cluster"].unique().tolist())
    cluster_ids = [c for c in cluster_ids if c >= 0]
    if args.limit_clusters:
        cluster_ids = cluster_ids[: args.limit_clusters]
    log.info("Clusters to process: %s", cluster_ids)

    log.info("Fitting TF-IDF snapshot (uni+bigrams) ...")
    kw = distinctive_terms(df["customer_text"], df["coarse_cluster"], top_n=10)

    results, samples = [], {}
    for cid in cluster_ids:
        sub = df[df["coarse_cluster"] == cid]
        idx = sub.index.to_numpy()
        close, far, d_close, d_far = sample_cluster(idx, Xn)
        rep = [
            {
                "sample_id": f"R{i + 1}",
                "message_uid": str(df.loc[j, "message_uid"]),
                "customer_text": str(df.loc[j, "customer_text"])[:600],
                "distance_to_centroid": float(d),
            }
            for i, (j, d) in enumerate(zip(close, d_close, strict=True))
        ]
        bnd = [
            {
                "sample_id": f"B{i + 1}",
                "message_uid": str(df.loc[j, "message_uid"]),
                "customer_text": str(df.loc[j, "customer_text"])[:600],
                "distance_to_centroid": float(d),
            }
            for i, (j, d) in enumerate(zip(far, d_far, strict=True))
        ]
        coarse_intent = str(sub["candidate_intent"].mode().iat[0]) if len(sub) else f"cluster_{cid}"
        coarse_sub = str(sub["candidate_sub_intent"].mode().iat[0]) if len(sub) else ""
        samples[cid] = {
            "keywords": kw.get(cid, []),
            "coarse_sub_intent": coarse_sub,
            "cluster_size": len(sub),
            "representative": rep,
            "boundary": bnd,
            "coarse_intent": coarse_intent,
        }

        prompt = build_user_prompt(cid, coarse_intent, coarse_sub, kw.get(cid, []), rep, bnd)
        if args.dry_run:
            res = heuristic_stub(cid, coarse_intent, rep, bnd)
        elif args.llm_provider == "openai":
            res = call_openai(SYSTEM_PROMPT, prompt, args.model)
        elif args.llm_provider == "ollama":
            res = call_ollama(
                SYSTEM_PROMPT,
                prompt,
                model=args.model,
                host=args.ollama_host,
                temperature=args.temperature,
                num_ctx=args.ollama_num_ctx,
            )
        else:
            res = call_anthropic(SYSTEM_PROMPT, prompt, args.model)
        res.setdefault("cluster_id", cid)
        res.setdefault("coarse_intent", coarse_intent)
        res["_warnings"] = validate_result(res)
        if res["_warnings"]:
            log.warning("Cluster %d: %s", cid, "; ".join(res["_warnings"]))
        res["_meta"] = {
            "coarse_sub_intent": coarse_sub,
            "cluster_size": len(sub),
            "keywords": kw.get(cid, []),
            "representative": rep,
            "boundary": bnd,
            "provider": "dry-run" if args.dry_run else args.llm_provider,
            "model": "heuristic" if args.dry_run else args.model,
        }
        results.append(res)
        log.info(
            "Cluster %d done: %d sub-intents -> %s",
            cid,
            len(res.get("proposed_sub_intents", [])),
            res.get("recommendation", {}).get("action"),
        )
        if not args.dry_run:
            time.sleep(1)  # gentle rate limit

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "fine_grained_taxonomy.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_markdown(results, samples, args.output_dir / "fine_grained_report.md")
    log.info(
        "Wrote %s and %s",
        args.output_dir / "fine_grained_taxonomy.json",
        args.output_dir / "fine_grained_report.md",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
