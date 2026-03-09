"""Streamlit UI for DocuChat — RAG-powered document assistant."""

import os
import uuid
from datetime import datetime

import streamlit as st

from docuchat.core import (
    build_vector_store,
    extract_text_from_file,
    get_ai_response,
    validate_groq_api_key,
)

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="DocuChat", page_icon="🤖", layout="wide")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "files" not in st.session_state:
    st.session_state.files: list[dict] = []

if "conversation" not in st.session_state:
    st.session_state.conversation: list[dict] = []

if "api_key" not in st.session_state:
    st.session_state.api_key: str = ""

if "known_files" not in st.session_state:
    st.session_state.known_files: set[str] = set()

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _rebuild_vector_store() -> None:
    """Rebuild the FAISS index from all currently loaded files."""
    st.session_state.vector_store = (
        build_vector_store(st.session_state.files)
        if st.session_state.files
        else None
    )


def _remove_file(file_id: str, original_name: str, size_bytes: int, path: str) -> None:
    """Delete a file from disk and remove it from session state."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    st.session_state.files = [
        f for f in st.session_state.files if f.get("id") != file_id
    ]
    st.session_state.known_files.discard(f"{original_name}:{size_bytes}")
    _rebuild_vector_store()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("DocuChat")
    st.caption("RAG-powered document assistant")

    # --- File upload ---
    uploaded = st.file_uploader(
        "Upload documents (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded:
        new_files_added = False
        for file in uploaded:
            try:
                size_bytes = getattr(file, "size", None) or len(file.getbuffer())
                unique_key = f"{file.name}:{size_bytes}"
                if unique_key in st.session_state.known_files:
                    continue

                file_id = f"{uuid.uuid4()}_{file.name}"
                file_path = os.path.join(UPLOAD_DIR, file_id)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                st.session_state.files.append(
                    {
                        "id": file_id,
                        "original_name": file.name,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "text_content": extract_text_from_file(file_path, file.name),
                        "uploaded_at": datetime.now().isoformat(),
                    }
                )
                st.session_state.known_files.add(unique_key)
                st.toast(f"✅ Uploaded {file.name}")
                new_files_added = True
            except Exception as e:
                st.warning(f"Failed to process {file.name}: {e}")

        if new_files_added:
            with st.spinner("Building knowledge base…"):
                _rebuild_vector_store()

    # --- Uploaded file list ---
    if st.session_state.files:
        st.subheader("Documents")
        for f in list(st.session_state.files):
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.write(f"📄 {f['original_name']} ({round(f['size'] / 1024, 1)} KB)")
            with col2:
                if st.button("🗑", key=f"rm_{f['id']}", help="Remove", use_container_width=True):
                    _remove_file(
                        file_id=f["id"],
                        original_name=f["original_name"],
                        size_bytes=int(f.get("size", 0)),
                        path=f.get("path", ""),
                    )
                    st.rerun()

    st.divider()

    # --- API key ---
    st.subheader("GROQ API Key")
    api_key_input = st.text_input(
        "Enter your key (gsk_...)",
        value=st.session_state.api_key,
        type="password",
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input.strip()

    if st.session_state.api_key:
        is_valid, msg = validate_groq_api_key(st.session_state.api_key)
        st.success("✅ Valid key") if is_valid else st.error(msg)

    st.markdown(
        "Don't have a key? Get one free at [console.groq.com](https://console.groq.com/keys)"
    )
    st.link_button("Get Free GROQ Key", url="https://console.groq.com/keys", use_container_width=True)

    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.conversation = []
        st.rerun()


# ---------------------------------------------------------------------------
# Main — Chat area
# ---------------------------------------------------------------------------
st.title("🤖 DocuChat")
st.caption("Ask questions about your documents — answers are retrieved from your exact content")

# Setup hints when not ready
if not st.session_state.files or not (
    st.session_state.api_key and validate_groq_api_key(st.session_state.api_key)[0]
):
    col1, col2 = st.columns(2)
    with col1:
        st.info("📄 **Step 1** — Upload documents from the sidebar (PDF, DOCX, TXT)")
    with col2:
        st.info("🔑 **Step 2** — Enter your GROQ API key in the sidebar")

# Render conversation history
for msg in st.session_state.conversation:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------
def handle_user_message(user_message: str) -> None:
    if not user_message:
        return

    if not st.session_state.files:
        st.warning("⚠️ Please upload at least one document first.")
        return

    api_key = st.session_state.api_key.strip()
    is_valid, validation_msg = validate_groq_api_key(api_key)
    if not is_valid:
        st.warning(f"⚠️ {validation_msg}")
        return

    # Lazily rebuild vector store if needed
    if not st.session_state.vector_store:
        with st.spinner("Building knowledge base…"):
            _rebuild_vector_store()
        if not st.session_state.vector_store:
            st.error("Could not build knowledge base from the uploaded documents.")
            return

    # Persist user message
    st.session_state.conversation.append(
        {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()}
    )

    # Retrieve + generate
    with st.chat_message("assistant"):
        with st.spinner("Searching documents…"):
            answer = get_ai_response(user_message, st.session_state.vector_store, api_key)
        st.markdown(answer)

    # Persist assistant message
    st.session_state.conversation.append(
        {"role": "assistant", "content": answer, "timestamp": datetime.now().isoformat()}
    )


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if prompt := st.chat_input("Ask a question about your documents…"):
    with st.chat_message("user"):
        st.markdown(prompt)
    handle_user_message(prompt)
