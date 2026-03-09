import os
import uuid
from datetime import datetime

import streamlit as st

# Reuse existing logic without changes
from simple_app import (
    validate_groq_api_key,
    extract_text_from_file,
    build_vector_store,
    get_ai_response,
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
    st.session_state.known_files = set()

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None


def _rebuild_vector_store():
    """Rebuild FAISS vector store from all current files."""
    if st.session_state.files:
        st.session_state.vector_store = build_vector_store(st.session_state.files)
    else:
        st.session_state.vector_store = None


def _remove_file(file_id: str, original_name: str, size_bytes: int, path: str) -> None:
    """Remove a file from disk and session state."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    st.session_state.files = [x for x in st.session_state.files if x.get("id") != file_id]
    st.session_state.known_files.discard(f"{original_name}:{size_bytes}")
    _rebuild_vector_store()


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
        new_files_added = False
        for file in uploaded:
            try:
                original_name = file.name
                size_bytes = getattr(file, 'size', None) or len(file.getbuffer())
                unique_key = f"{original_name}:{size_bytes}"
                if unique_key in st.session_state.known_files:
                    continue
                file_id = f"{uuid.uuid4()}_{original_name}"
                file_path = os.path.join(UPLOAD_DIR, file_id)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
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
                st.toast(f"✅ Uploaded {original_name}")
                new_files_added = True
            except Exception as e:
                st.warning(f"Failed to process {file.name}: {e}")
        if new_files_added:
            with st.spinner("Building knowledge base..."):
                _rebuild_vector_store()

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
    st.subheader("GROQ API Key")
    api_key_input = st.text_input("Enter your GROQ API Key (gsk_...)", value=st.session_state.api_key, type="password")
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
st.title("🤖 DocuChat")
st.caption("RAG-powered document assistant — ask questions, get accurate answers")

# Setup guide when not ready
if not st.session_state.files or not (st.session_state.api_key and validate_groq_api_key(st.session_state.api_key)[0]):
    col1, col2 = st.columns(2)
    with col1:
        st.info("📄 **Step 1:** Upload your documents from the sidebar (PDF, DOCX, TXT)")
    with col2:
        st.info("🔑 **Step 2:** Enter your GROQ API key in the sidebar to start chatting")

chat_container = st.container()
with chat_container:
    for msg in st.session_state.conversation:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])


def handle_user_message(user_message: str):
    if not user_message:
        return
    if not st.session_state.files:
        st.warning("⚠️ Please upload at least one document first.")
        return

    api_key = st.session_state.api_key.strip() if st.session_state.api_key else ""
    is_valid, msg = validate_groq_api_key(api_key)
    if not is_valid:
        st.warning(f"⚠️ Please enter a valid GROQ API key. {msg}")
        return

    if not st.session_state.vector_store:
        with st.spinner("Building knowledge base..."):
            _rebuild_vector_store()
        if not st.session_state.vector_store:
            st.error("Could not build knowledge base from uploaded documents.")
            return

    st.session_state.conversation.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat(),
    })

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            response = get_ai_response(user_message, st.session_state.vector_store, api_key)
        st.markdown(response)

    st.session_state.conversation.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat(),
    })


prompt = st.chat_input("Ask a question about your documents...")
if prompt is not None:
    with st.chat_message("user"):
        st.markdown(prompt)
    handle_user_message(prompt)


