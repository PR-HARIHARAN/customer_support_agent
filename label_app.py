"""Golden-set human labeling app.

Streamlit UI over data/processed/golden_set.csv (built by 005_golden_set.ipynb):
review each candidate label against the FULL conversation and save the human
verdict back to the same CSV. Candidate columns are never modified — only the
human_* / annotation_* / reviewer_notes / human_intent_r2 columns are written.

Run:  streamlit run label_app.py
"""

import os
import re
import shutil
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from customer_support.labeling.validation import (  # noqa: E402  (after sys.path setup)
    ANNOTATION_GUIDE,
    CANDIDATE_INTENTS,
    HUMAN_INTENTS_ALLOWED,
    INTENT_DEFINITIONS,
    VALID_OUTCOMES,
    validate_review,
)

GOLDEN_PATH = Path(
    os.environ.get("GOLDEN_SET_PATH", PROJECT_ROOT / "data" / "processed" / "golden_set.csv")
)
BACKUP_PATH = GOLDEN_PATH.with_name(GOLDEN_PATH.stem + ".backup.csv")


# ----------------------------------------------------------------------------
# Pure helpers (no Streamlit calls — easy to test).
# ----------------------------------------------------------------------------
def load_golden(path: Path = GOLDEN_PATH) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"conversation_id": str}, keep_default_na=False)


def parse_conversation(text: str) -> list[tuple[str, str]]:
    """Split full_conversation_text into [(role, body)] preserving order."""
    parts = re.split(r"\n\s*\n(?=(?:CUSTOMER|AGENT):)", str(text).strip())
    messages: list[tuple[str, str]] = []
    for part in parts:
        match = re.match(r"(CUSTOMER|AGENT):\s*(.*)$", part.strip(), re.DOTALL)
        if match:
            messages.append((match.group(1).lower(), match.group(2).strip()))
        elif part.strip():
            messages.append(("customer", part.strip()))
    return messages


def save_golden(df: pd.DataFrame, path: Path = GOLDEN_PATH) -> None:
    """Rolling backup + atomic write so a crash can never corrupt the gold set.

    On Windows the CSV is often locked by Excel/another viewer — retry briefly,
    then raise a human-readable error instead of a raw traceback.
    """
    import time

    if path.exists():
        shutil.copyfile(path, BACKUP_PATH)
    tmp = path.with_name(path.name + ".tmp")
    df.to_csv(tmp, index=False)
    last_error: OSError | None = None
    for _ in range(10):
        try:
            os.replace(tmp, path)
            return
        except OSError as error:  # file locked (e.g. open in Excel)
            last_error = error
            time.sleep(0.5)
    tmp.unlink(missing_ok=True)
    raise OSError(
        f"Could not write {path} — it is locked by another program "
        f"(close it in Excel/viewers and retry). Details: {last_error}"
    )


def build_queue(
    df: pd.DataFrame,
    status: str,
    groups: list[str],
    intents: list[str],
    second_pass_only: bool,
    sort_by: str,
    search: str,
) -> pd.DataFrame:
    queue = df.copy()
    if status == "Pending only":
        queue = queue[queue["annotation_status"] != "reviewed"]
    elif status == "Reviewed only":
        queue = queue[queue["annotation_status"] == "reviewed"]
    if groups:
        queue = queue[queue["sampling_group"].isin(groups)]
    if intents:
        queue = queue[queue["candidate_intent"].isin(intents)]
    if second_pass_only:
        queue = queue[queue["second_pass"].astype(str) == "True"]
    if search:
        needle = search.lower()
        queue = queue[
            queue["conversation_id"].str.lower().str.contains(needle)
            | queue["full_conversation_text"].str.lower().str.contains(needle)
        ]
    sorters = {
        "Highest ambiguity first": ("candidate_ambiguity_margin", True),
        "Hardest challenge first": ("difficulty_score", False),
        "Lowest confidence first": ("candidate_distance_best", False),
        "Conversation ID": ("conversation_id", True),
    }
    column, ascending = sorters[sort_by]
    if sort_by == "Lowest confidence first":
        queue = queue.sort_values(["candidate_confidence", column], ascending=[True, ascending])
    else:
        queue = queue.sort_values(column, ascending=ascending, kind="stable")
    return queue.reset_index(drop=True)


# ----------------------------------------------------------------------------
# App.
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Golden-set labeler", page_icon="🏷️", layout="wide")

if not GOLDEN_PATH.exists():
    st.error(f"Golden set not found: {GOLDEN_PATH} — run 005_golden_set.ipynb first.")
    st.stop()

df = load_golden()
if len(df) != 250:
    st.warning(f"Expected 250 rows, found {len(df)} — check {GOLDEN_PATH}.")

n_reviewed = int((df["annotation_status"] == "reviewed").sum())

# Programmatic navigation lands here on the *next* run, before any widget
# exists, so resetting the record picker is legal (avoids stale selection).
_pending_goto = st.session_state.pop("_goto", None)
if _pending_goto:
    st.session_state["current_id"] = _pending_goto
    st.session_state.pop("nav-select", None)

st.title("Golden-set human labeling")
st.caption(
    "You are reviewing the candidate label, never forced to accept it. "
    "Saving writes only the human_*/annotation_* columns back to golden_set.csv "
    "(rolling backup kept at golden_set.backup.csv)."
)

# ---- sidebar: progress + filters -------------------------------------------
with st.sidebar:
    st.header("Progress")
    st.progress(n_reviewed / max(len(df), 1), text=f"{n_reviewed} / {len(df)} reviewed")
    for group in ["representative", "uncertainty", "challenge"]:
        sub = df[df["sampling_group"] == group]
        done = int((sub["annotation_status"] == "reviewed").sum())
        st.caption(f"{group}: {done}/{len(sub)}")
    both = df[(df["human_intent"] != "") & (df["human_intent_r2"] != "")]
    st.caption(f"Double-reviewed: {len(both)}/50 second-pass")

    st.divider()
    st.header("Queue filters")
    status = st.radio(
        "Status",
        ["Pending first", "Pending only", "Reviewed only", "All"],
        key="flt-status",
    )
    groups = st.multiselect(
        "Sampling group",
        ["representative", "uncertainty", "challenge"],
        key="flt-group",
    )
    intents = st.multiselect("Candidate intent", CANDIDATE_INTENTS, key="flt-intent")
    second_pass_only = st.checkbox("Second-pass pool only (50)", key="flt-second")
    sort_by = st.selectbox(
        "Order",
        [
            "Highest ambiguity first",
            "Hardest challenge first",
            "Lowest confidence first",
            "Conversation ID",
        ],
        key="flt-sort",
    )
    search = st.text_input("Search id or text", key="flt-search").strip()

queue = build_queue(df, status, groups, intents, second_pass_only, sort_by, search)

# Pin the record being reviewed: a just-saved (now reviewed) record must stay
# visible and editable even when the active filters would exclude it.
_pinned_notice = False
_pinned_id = st.session_state.get("current_id")
if (
    _pinned_id
    and _pinned_id in set(df["conversation_id"].tolist())
    and _pinned_id not in set(queue["conversation_id"].tolist())
):
    queue = pd.concat([df[df["conversation_id"] == _pinned_id], queue], ignore_index=True)
    _pinned_notice = True

with st.sidebar:
    st.caption(f"{len(queue)} records in queue")
    if _pinned_notice:
        st.caption("📌 Current record pinned — it's outside the active filters.")
    if queue.empty:
        st.info("Queue is empty — loosen the filters.")
        st.stop()
    queue_ids = queue["conversation_id"].tolist()
    if status == "Pending first":
        pending_ids = queue[queue["annotation_status"] != "reviewed"]["conversation_id"].tolist()
        ordered_ids = pending_ids + [i for i in queue_ids if i not in set(pending_ids)]
    else:
        ordered_ids = queue_ids
    current = st.session_state.get("current_id")
    if current not in ordered_ids:
        current = ordered_ids[0]
        st.session_state["current_id"] = current
    selected = st.selectbox(
        "Record",
        ordered_ids,
        index=ordered_ids.index(current),
        format_func=lambda cid: (
            f"{cid} | {queue.set_index('conversation_id').loc[cid, 'candidate_intent'][:24]} | "
            f"{queue.set_index('conversation_id').loc[cid, 'sampling_group'][:5]} | "
            f"{queue.set_index('conversation_id').loc[cid, 'annotation_status']}"
        ),
        key="nav-select",
    )
    st.session_state["current_id"] = selected if selected else current
    # Only sync when the USER picked from the dropdown — never clobber a
    # programmatic move (those arrive via _goto, applied above).
    pos = (
        ordered_ids.index(st.session_state["current_id"])
        if st.session_state["current_id"] in ordered_ids
        else 0
    )

    nav_prev, nav_next = st.columns(2)
    with nav_prev:
        if st.button("◀ Prev", use_container_width=True, key="btn-prev"):
            st.session_state["_goto"] = ordered_ids[(pos - 1) % len(ordered_ids)]
            st.rerun()
    with nav_next:
        if st.button("Next ▶", use_container_width=True, key="btn-next"):
            st.session_state["_goto"] = ordered_ids[(pos + 1) % len(ordered_ids)]
            st.rerun()

row = df[df["conversation_id"] == selected].iloc[0]
cid = str(row["conversation_id"])

# ---- record header ----------------------------------------------------------
badge = "🔁 second-pass" if str(row["second_pass"]) == "True" else ""
done_mark = "✅ reviewed" if row["annotation_status"] == "reviewed" else "⏳ pending"
st.subheader(f"{cid}  ·  {row['sampling_group']}  ·  {done_mark}  {badge}")
meta = st.columns(5)
_cards = [
    ("Candidate intent", str(row["candidate_intent"])),
    ("Cluster", f"{row['candidate_cluster']} (2nd: {row['candidate_second_cluster']})"),
    ("Confidence", str(row["candidate_confidence"])),
    ("Ambiguity margin ↓=harder", str(row["candidate_ambiguity_margin"])),
    ("Difficulty", f"{row['difficulty_score']} · {row['n_messages']} msgs"),
]
for _col, (_label, _value) in zip(meta, _cards, strict=True):
    with _col:
        # Plain markdown (not st.metric): long values wrap instead of truncating.
        st.markdown(
            f"<div style='font-size:0.8rem;color:gray'>{_label}</div>"
            f"<div style='font-size:1.1rem;font-weight:600;overflow-wrap:anywhere'>{_value}</div>",
            unsafe_allow_html=True,
        )
st.caption(f"Domain: {row['candidate_domain']}  ·  Sub-intent: {row['candidate_sub_intent']}")

# ---- full conversation ------------------------------------------------------
messages = parse_conversation(row["full_conversation_text"])
with st.container(height=420):
    for role, body in messages:
        avatar = "🧑" if role == "customer" else "✈️"
        with st.chat_message(role, avatar=avatar):
            st.write(body)

with st.expander("Taxonomy reference (definitions + annotation guide)"):
    for intent in CANDIDATE_INTENTS:
        st.markdown(f"**{intent}** — {INTENT_DEFINITIONS[intent]}")
        st.caption(ANNOTATION_GUIDE[intent])


# ---- labeling form ----------------------------------------------------------
def _storage_key(name: str) -> str:
    return f"{name}::{cid}"


k = _storage_key
stored_outcome = (
    row["annotation_outcome"] if row["annotation_outcome"] in VALID_OUTCOMES else "ACCEPT"
)
stored_intent = (
    row["human_intent"] if row["human_intent"] in HUMAN_INTENTS_ALLOWED else row["candidate_intent"]
)
if stored_intent not in HUMAN_INTENTS_ALLOWED:
    stored_intent = HUMAN_INTENTS_ALLOWED[0]

with st.form(key=f"label-form::{cid}"):
    st.markdown("### Your verdict")
    outcome = st.selectbox(
        "Outcome (is the candidate right or wrong?)",
        VALID_OUTCOMES,
        index=VALID_OUTCOMES.index(stored_outcome),
        help="ACCEPT=candidate right. CHANGE_INTENT/RENAME=candidate wrong. SPLIT/MERGE_NEEDED=taxonomy problem. SOCIAL/NON_ACTIONABLE/UNKNOWN=no actionable intent.",
        key=k("fld-outcome"),
    )
    col_a, col_b = st.columns(2)
    with col_a:
        human_intent = st.selectbox(
            "human_intent (gold label)",
            HUMAN_INTENTS_ALLOWED,
            index=HUMAN_INTENTS_ALLOWED.index(stored_intent),
            key=k("fld-intent"),
        )
        human_domain = st.text_input(
            "human_domain",
            value=row["human_domain"] or row["candidate_domain"],
            key=k("fld-domain"),
        )
    with col_b:
        human_sub = st.text_input(
            "human_sub_intent",
            value=row["human_sub_intent"] or row["candidate_sub_intent"],
            key=k("fld-sub"),
        )
        notes = st.text_area(
            "reviewer_notes (required for New intent / splits / merges)",
            value=row["reviewer_notes"],
            key=k("fld-notes"),
        )
    save, save_next = st.columns(2)
    with save:
        do_save = st.form_submit_button("💾 Save", use_container_width=True)
    with save_next:
        do_save_next = st.form_submit_button("💾 Save & next pending", use_container_width=True)


def _persist(outcome_v: str, intent_v: str, domain_v: str, sub_v: str, notes_v: str) -> bool:
    error = validate_review(outcome_v, intent_v, candidate_intent=str(row["candidate_intent"]))
    if error:
        st.error(error)
        return False
    if outcome_v == "New intent (see notes)" and not notes_v.strip():
        st.error("Describe the new intent in reviewer_notes.")
        return False
    fresh = load_golden()
    mask = fresh["conversation_id"] == cid
    fresh.loc[mask, "human_intent"] = intent_v
    fresh.loc[mask, "human_domain"] = domain_v.strip()
    fresh.loc[mask, "human_sub_intent"] = sub_v.strip()
    fresh.loc[mask, "annotation_outcome"] = outcome_v
    fresh.loc[mask, "annotation_status"] = "reviewed"
    fresh.loc[mask, "reviewer_notes"] = notes_v.strip()
    save_golden(fresh)
    return True


if do_save or do_save_next:
    try:
        saved_ok = _persist(outcome, human_intent, human_domain, human_sub, notes)
    except OSError as error:
        st.error(str(error))
        saved_ok = False
    if saved_ok:
        st.success(f"Saved {cid} as {outcome} → {human_intent}.")
        if do_save_next:
            pend = queue[
                (queue["annotation_status"] != "reviewed") & (queue["conversation_id"] != cid)
            ]
            if not pend.empty:
                st.session_state["_goto"] = pend.iloc[0]["conversation_id"]
            else:
                st.info("No more pending records in this queue.")
        st.rerun()

# ---- second reviewer ---------------------------------------------------------
with st.expander("Second reviewer (50 second-pass rows → agreement)"):
    r2_default = (
        row["human_intent_r2"] if row["human_intent_r2"] in HUMAN_INTENTS_ALLOWED else "(skip)"
    )
    r2 = st.selectbox(
        "human_intent_r2 (independent second label)",
        ["(skip)"] + HUMAN_INTENTS_ALLOWED,
        index=(["(skip)"] + HUMAN_INTENTS_ALLOWED).index(r2_default)
        if r2_default in (["(skip)"] + HUMAN_INTENTS_ALLOWED)
        else 0,
        key=k("fld-r2"),
    )
    if st.button("Save second label", key=k("btn-r2")):
        if r2 == "(skip)":
            st.warning("Pick a label first.")
        else:
            fresh = load_golden()
            fresh.loc[fresh["conversation_id"] == cid, "human_intent_r2"] = r2
            try:
                save_golden(fresh)
            except OSError as error:
                st.error(str(error))
                st.stop()
            st.success(f"Saved second label for {cid}: {r2}.")
            st.rerun()
    if len(both):
        raw = float((both["human_intent"] == both["human_intent_r2"]).mean())
        try:
            from sklearn.metrics import cohen_kappa_score

            kappa = (
                round(float(cohen_kappa_score(both["human_intent"], both["human_intent_r2"])), 4)
                if len(both) >= 2 and both["human_intent"].nunique() > 1
                else None
            )
        except Exception:
            kappa = None
        st.caption(f"Agreement so far: n={len(both)}, raw={raw:.2f}, κ={kappa}")
