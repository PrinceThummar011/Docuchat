"""RAG pipeline: vector store construction and retrieval-augmented generation."""

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Embedding model — cached across Streamlit sessions/reruns so it is loaded
# only once per server process (avoids repeated 90 MB downloads).
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading embedding model…")
def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50
_TOP_K = 4
_LLM_MODEL = "llama-3.1-8b-instant"

_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question using only the provided "
    "document context. If the answer is not present in the context, say so clearly."
)


def build_vector_store(files: list[dict]) -> FAISS | None:
    """
    Build a FAISS vector store from a list of uploaded files.

    Each file dict must contain:
        - ``original_name`` (str): display name used as chunk metadata source.
        - ``text_content``  (str): extracted plain text of the document.

    Args:
        files: List of file metadata dicts.

    Returns:
        A FAISS vector store ready for similarity search, or ``None`` if all
        files have empty content.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
    )
    docs = []
    for file in files:
        content = file.get("text_content", "").strip()
        if not content:
            continue
        chunks = splitter.create_documents(
            [content],
            metadatas=[{"source": file["original_name"]}],
        )
        docs.extend(chunks)

    return FAISS.from_documents(docs, _get_embeddings()) if docs else None


def get_ai_response(question: str, vector_store: FAISS, api_key: str) -> str:
    """
    Answer a question with RAG: retrieve relevant chunks, then query the LLM.

    Args:
        question:     The user's question.
        vector_store: FAISS index built from uploaded documents.
        api_key:      Groq API key (``gsk_...``).

    Returns:
        Answer string from the LLM, or a descriptive error message.
    """
    try:
        # Step 1 — Semantic retrieval
        retriever = vector_store.as_retriever(search_kwargs={"k": _TOP_K})
        relevant_docs = retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in relevant_docs)

        # Step 2 — Generation
        llm = ChatGroq(
            api_key=api_key,
            model_name=_LLM_MODEL,
            max_tokens=1000,
            temperature=0.3,
        )
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]
        return llm.invoke(messages).content

    except Exception as e:
        error = str(e)
        if any(
            token in error.lower()
            for token in ["401", "authentication", "invalid api key", "unauthorized"]
        ):
            return "Authentication failed. Please check your API key."
        return f"Error: {error}"
