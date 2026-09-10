import json
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
CONVERSATIONS_PATH = PROJECT_ROOT / "data" / "processed" / "conversations.jsonl"


@st.cache_data(show_spinner="Loading conversations...")
def load_conversations(path: str) -> list[dict]:
    conversations = []
    with Path(path).open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                conversations.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}"
                ) from error
    return conversations


def format_timestamp(value: str | None) -> str:
    if not value:
        return "Unknown time"
    return value.replace("T", " ").replace("+00:00", " UTC")[:22]


def conversation_label(conversation: dict) -> str:
    message_count = len(conversation.get("messages", []))
    return f"{conversation['conversation_id']}  |  {message_count} messages"


def matching_messages(conversation: dict, keywords: list[str]) -> list[dict]:
    return [
        message
        for message in conversation.get("messages", [])
        if all(
            keyword in str(message.get("text", "")).lower()
            for keyword in keywords
        )
    ]


def conversation_matches(conversation: dict, keywords: list[str]) -> bool:
    if not keywords:
        return True

    searchable_text = " ".join(
        [
            str(conversation.get("conversation_id", "")),
            *(str(message.get("text", "")) for message in conversation.get("messages", [])),
        ]
    ).lower()
    return all(keyword in searchable_text for keyword in keywords)


st.set_page_config(
    page_title="AmericanAir Support Conversations",
    page_icon="✈️",
    layout="wide",
)

st.title("AmericanAir Support Conversations")
st.caption("Browse reconstructed Twitter support threads from the JSONL dataset.")

if not CONVERSATIONS_PATH.exists():
    st.error(f"Conversation file not found: {CONVERSATIONS_PATH}")
    st.stop()

try:
    conversations = load_conversations(str(CONVERSATIONS_PATH))
except ValueError as error:
    st.error(str(error))
    st.stop()

if not conversations:
    st.warning("The conversation file does not contain any records.")
    st.stop()

conversation_by_id = {
    str(conversation["conversation_id"]): conversation
    for conversation in conversations
}
conversation_ids = list(conversation_by_id)

with st.sidebar:
    st.header("Find a conversation")
    search_text = st.text_input(
        "Search keywords",
        placeholder="Try: flight delay refund",
        help="Enter one or more keywords. Every keyword must appear in the conversation.",
    ).strip().lower()
    keywords = [keyword for keyword in search_text.split() if keyword]

    matching_conversations = [
        conversation
        for conversation in conversations
        if conversation_matches(conversation, keywords)
    ]

    st.caption(f"{len(matching_conversations):,} matching conversations")
    matching_ids = [str(item["conversation_id"]) for item in matching_conversations]

    if not matching_ids:
        st.info("No conversations match that search.")
        st.stop()

    current_id = st.session_state.get("conversation_id")
    if current_id not in matching_ids:
        current_id = matching_ids[0]

    selected_id = st.selectbox(
        "Conversation",
        matching_ids,
        index=matching_ids.index(current_id),
        format_func=lambda value: conversation_label(conversation_by_id[value]),
    )
    st.session_state["conversation_id"] = selected_id

    if keywords:
        st.caption("Keywords: " + ", ".join(keywords))

    st.divider()
    st.metric("Total conversations", f"{len(conversations):,}")
    st.metric(
        "Total messages",
        f"{sum(len(item.get('messages', [])) for item in conversations):,}",
    )

conversation = conversation_by_id[selected_id]
messages = conversation.get("messages", [])
matched = matching_messages(conversation, keywords)

if keywords:
    st.info(f"Found {len(matching_conversations):,} matching conversations.")
    if matched:
        with st.expander("Matching message excerpts", expanded=True):
            for message in matched:
                st.markdown(
                    f"**{message.get('role', 'customer').title()}**  "
                    f"({format_timestamp(message.get('created_at'))})  "
                    f"`{message.get('tweet_id', '')}`\n\n"
                    f"> {message.get('text', '')}"
                )

header_left, header_right = st.columns([3, 1])
with header_left:
    st.subheader(f"Conversation {conversation['conversation_id']}")
    st.caption(
        f"{len(messages)} messages  •  "
        f"{format_timestamp(conversation.get('start_time'))} to "
        f"{format_timestamp(conversation.get('end_time'))}"
    )
with header_right:
    st.download_button(
        "Download conversation",
        data=json.dumps(conversation, ensure_ascii=False, indent=2),
        file_name=f"conversation_{conversation['conversation_id']}.json",
        mime="application/json",
        use_container_width=True,
    )

for message in messages:
    role = message.get("role", "customer")
    avatar = "🧑" if role == "customer" else "✈️"
    with st.chat_message(role, avatar=avatar):
        st.caption(
            f"{role.title()}  •  {format_timestamp(message.get('created_at'))}  •  "
            f"Tweet {message.get('tweet_id', '')}"
        )
        st.write(message.get("text", ""))
