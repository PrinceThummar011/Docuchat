"""RAG pipeline: vector store construction and retrieval-augmented generation."""

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Embedding model — cached across Streamlit sessions/reruns so it is loaded
# only once per server process (avoids repeated 90 MB downloads).
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading embedding model…")
def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

_CHUNK_SIZE = 1000      # larger chunks preserve full sentences and paragraphs
_CHUNK_OVERLAP = 200    # bigger overlap avoids losing info at chunk boundaries
_TOP_K = 6              # retrieve more candidates for better coverage
_FETCH_K = 20           # candidate pool for MMR diversity re-ranking
_SCORE_THRESHOLD = 0.25 # discard chunks below this relevance score
_MAX_HISTORY = 3        # last N conversation turns passed as context
_LLM_MODEL = "llama-3.3-70b-versatile"  # more accurate model for better answers

_SYSTEM_PROMPT = (
    "You are an expert document analyst. Answer the user's question STRICTLY "
    "based on the provided document context.\n\n"
    "Rules:\n"
    "1. Only use information from the context. Do NOT rely on outside knowledge.\n"
    "2. If the answer is not in the context, say: "
    "'I could not find this information in the uploaded documents.'\n"
    "3. Reference the source document when relevant (e.g. [Source: filename]).\n"
    "4. Be accurate, concise, and well-structured.\n"
    "5. For follow-up questions, use the conversation history to understand context."
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
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
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


def get_ai_response(
    question: str,
    vector_store: FAISS,
    api_key: str,
    conversation_history: list[dict] | None = None,
) -> str:
    """
    Answer a question with RAG: retrieve relevant chunks, then query the LLM.

    Args:
        question:             The user's question.
        vector_store:         FAISS index built from uploaded documents.
        api_key:              Groq API key (``gsk_...``).
        conversation_history: List of past ``{"role": ..., "content": ...}`` dicts
                              used to support follow-up questions.

    Returns:
        Answer string from the LLM, or a descriptive error message.
    """
    try:
        # Step 1 — MMR retrieval for diverse, relevant chunks
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": _TOP_K, "fetch_k": _FETCH_K, "lambda_mult": 0.7},
        )
        mmr_docs = retriever.invoke(question)

        # Step 2 — Score filtering: keep only chunks above the relevance threshold
        scored = vector_store.similarity_search_with_relevance_scores(question, k=_TOP_K)
        good_docs = [doc for doc, score in scored if score >= _SCORE_THRESHOLD]
        # Fall back to unfiltered MMR docs if all chunks score below threshold
        final_docs = good_docs if good_docs else mmr_docs

        # Step 3 — Build context string with source labels
        context_parts = []
        for i, doc in enumerate(final_docs, 1):
            source = doc.metadata.get("source", "Unknown")
            context_parts.append(f"[Source {i}: {source}]\n{doc.page_content}")
        context = "\n\n---\n\n".join(context_parts)

        # Step 4 — Build message list: system prompt + recent history + current question
        messages: list = [SystemMessage(content=_SYSTEM_PROMPT)]
        if conversation_history:
            for turn in conversation_history[-(_MAX_HISTORY * 2):]:
                if turn["role"] == "user":
                    messages.append(HumanMessage(content=turn["content"]))
                elif turn["role"] == "assistant":
                    messages.append(AIMessage(content=turn["content"]))
        messages.append(
            HumanMessage(
                content=f"Document Context:\n{context}\n\nQuestion: {question}"
            )
        )

        # Step 5 — Generate answer
        llm = ChatGroq(
            api_key=api_key,
            model_name=_LLM_MODEL,
            max_tokens=2048,
            temperature=0.1,
        )
        return llm.invoke(messages).content

    except Exception as e:
        error = str(e)
        if any(
            token in error.lower()
            for token in ["401", "authentication", "invalid api key", "unauthorized"]
        ):
            return "Authentication failed. Please check your API key."
        return f"Error: {error}"
