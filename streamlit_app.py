import os
import uuid
from datetime import datetime

import streamlit as st

# Reuse existing logic without changes
from simple_app import (
    validate_groq_api_key,
    extract_text_from_file,
    get_ai_response,
    analyze_document_content,
)


# App config
st.set_page_config(page_title="DocuChat (Streamlit)", page_icon="🤖", layout="wide")


# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Session state initialization (keeps logic structure like Flask 'sessions')
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4()}"

if "files" not in st.session_state:
    # each: {id, original_name, path, size, text_content, uploaded_at}
    st.session_state.files = []

if "conversation" not in st.session_state:
    # list of {role: 'user'|'assistant', content, timestamp}
    st.session_state.conversation = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Track known uploads to avoid duplicates on reruns
if "known_files" not in st.session_state:
    # keys like "name:size"
    st.session_state.known_files = set()


def _remove_file(file_id: str, original_name: str, size_bytes: int, path: str) -> None:
    """Remove a file from disk and session state."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        # Ignore deletion errors; still remove from state
        pass

    # Remove entry from files list
    st.session_state.files = [x for x in st.session_state.files if x.get("id") != file_id]
    # Ensure we can re-upload later by clearing unique key
    st.session_state.known_files.discard(f"{original_name}:{size_bytes}")


# Sidebar: Upload + API key
with st.sidebar:
    st.title("DocuChat")
    st.caption("Chat with your documents")

    uploaded = st.file_uploader(
        "Upload documents (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt", "doc"],
        accept_multiple_files=True,
    )

    if uploaded:
        for file in uploaded:
            try:
                original_name = file.name
                size_bytes = getattr(file, 'size', None) or len(file.getbuffer())
                unique_key = f"{original_name}:{size_bytes}"
                # Skip if already added (prevents duplicates every rerun)
                if unique_key in st.session_state.known_files:
                    continue
                file_id = f"{uuid.uuid4()}_{original_name}"
                file_path = os.path.join(UPLOAD_DIR, file_id)
                # Save file to disk
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                # Extract text using existing function
                text_content = extract_text_from_file(file_path, original_name)

                st.session_state.files.append(
                    {
                        "id": file_id,
                        "original_name": original_name,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "text_content": text_content,
                        "uploaded_at": datetime.now().isoformat(),
                    }
                )
                st.session_state.known_files.add(unique_key)
                st.toast(f"Uploaded {original_name}")
            except Exception as e:
                st.warning(f"Failed to process {file.name}: {e}")

    if st.session_state.files:
        st.subheader("Uploaded Documents")
        for f in list(st.session_state.files):
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.write(f"- {f['original_name']} ({round(f['size']/1024, 2)} KB)")
            with col2:
                if st.button(
                    "🗑",
                    key=f"rm_{f['id']}",
                    help="Remove file",
                    use_container_width=True,
                ):
                    _remove_file(
                        file_id=f["id"],
                        original_name=f["original_name"],
                        size_bytes=int(f.get("size", 0)),
                        path=f.get("path", ""),
                    )
                    st.rerun()

    st.divider()
    st.subheader("Enhanced AI (optional)")
    api_key_input = st.text_input("Enter your GROQ API Key (starts with gsk_)", value=st.session_state.api_key, type="password")
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input.strip()

    if st.session_state.api_key:
        is_valid, msg = validate_groq_api_key(st.session_state.api_key)
        if is_valid:
            st.success("Valid GROQ API key format")
        else:
            st.error(f"{msg}")

    # Quick access to get a free, fast GROQ API key
    st.markdown(
        "**Don't have a key?** Get a fast, free-tier key from [Groq Console](https://console.groq.com/keys) and paste it above.")
    st.link_button("Get Free GROQ API Key", url="https://console.groq.com/keys", use_container_width=True)

    if st.button("Clear Chat"):
        st.session_state.conversation = []
        st.success("Chat cleared")


# Main area: Chat
st.title("AI Document Assistant")

mode = "🤖 AI Enhanced" if (st.session_state.api_key and validate_groq_api_key(st.session_state.api_key)[0]) else "📄 Smart Mode"
st.caption(f"Mode: {mode}")

# Help/Guide section (middle area)
with st.container():
    tabs = st.tabs(["Quick Start", "Modes", "Tips"])

    with tabs[0]:
        st.markdown(
            """
            1. Upload one or more documents from the left sidebar (PDF, DOCX, TXT).
            2. Optional: Enter your GROQ API key (starts with `gsk_`) to enable AI Enhanced mode.
            3. Ask your question in the input at the bottom.
            4. Read the response; ask follow-ups as needed.
            5. Use the trash icon next to a file to remove it.
            """
        )
        st.info(
            "Your files never leave your machine except when you choose to use your own GROQ key for AI Enhanced responses.")

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📄 Smart Mode")
            st.write(
                "Uses built-in document analysis to extract summaries, key points, and answers. No API key required.")
            st.markdown("- Works offline\n- Fast and private\n- Great for quick insights")
        with c2:
            st.subheader("🤖 AI Enhanced Mode")
            st.write(
                "When you add a valid GROQ API key, the app augments answers with large language models for richer responses.")
            st.markdown("- Higher-quality answers\n- Handles complex queries\n- Requires your `gsk_...` key")

    with tabs[2]:
        st.markdown(
            """
            - Keep questions specific: e.g., "List start dates" or "Summarize the key terms".
            - Upload multiple related documents; the app analyzes all of them together.
            - Invalid or missing GROQ keys automatically fall back to Smart Mode.
            """
        )

chat_container = st.container()
with chat_container:
    for msg in st.session_state.conversation:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])


def handle_user_message(user_message: str):
    if not user_message:
        return
    if len(st.session_state.files) == 0:
        st.warning("Please upload at least one document first")
        return

    # Store user message
    st.session_state.conversation.append(
        {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
        }
    )

    # Aggregate document content (same as Flask logic)
    all_text = ""
    file_names = []
    for f in st.session_state.files:
        file_names.append(f["original_name"])
        all_text += f"\n\n--- Content from {f['original_name']} ---\n"
        all_text += f.get("text_content", "Could not extract text from this file.")

    use_ai = False
    api_key = st.session_state.api_key.strip() if st.session_state.api_key else ""
    if api_key and api_key != "no-key-needed":
        is_valid, validation_message = validate_groq_api_key(api_key)
        if is_valid:
            use_ai = True

    if use_ai:
        try:
            response = get_ai_response(user_message, all_text, api_key)
            if response and not response.startswith("All AI models are currently unavailable"):
                final = f"🤖 **AI Enhanced Response:**\n\n{response}"
            else:
                analysis = analyze_document_content(user_message, all_text)
                final = f"📄 **Smart Analysis** (AI service unavailable):\n\n{analysis}"
        except Exception as e:
            analysis = analyze_document_content(user_message, all_text)
            final = f"📄 **Smart Analysis** (AI error):\n\n{analysis}"
    else:
        analysis = analyze_document_content(user_message, all_text)
        if api_key and api_key != "no-key-needed":
            final = analysis
        else:
            final = f"📄 **Smart Analysis:**\n\n{analysis}\n\n💡 *Tip: Add your own GROQ API key for enhanced AI responses!*"

    # Store assistant response
    st.session_state.conversation.append(
        {
            "role": "assistant",
            "content": final,
            "timestamp": datetime.now().isoformat(),
        }
    )

    # Stream to UI
    with st.chat_message("assistant"):
        st.markdown(final)


prompt = st.chat_input("Ask a question about your documents...")
if prompt is not None:
    with st.chat_message("user"):
        st.markdown(prompt)
    handle_user_message(prompt)


