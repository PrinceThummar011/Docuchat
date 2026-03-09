# DocuChat (Streamlit)

Chat with your documents using smart local analysis or optional AI‑enhanced answers powered by your own GROQ API key.

## Live Demo
- Open: https://docuchat-by-prince.streamlit.app/

## Features
- Upload and read PDF, DOCX, and TXT files
- Ask questions and get accurate answers using RAG (Retrieval-Augmented Generation)
- FAISS vector store for semantic document search
- Powered by Groq LLM (`llama-3.1-8b-instant`)
- Supports multiple documents simultaneously

## Requirements
- Python 3.9+
- [uv](https://github.com/astral-sh/uv)

## Setup
```bash
uv sync
```

## Run Locally
```bash
uv run streamlit run streamlit_app.py
```
Then open `http://localhost:8501`.

## How To Use
1) Enter your GROQ API key in the sidebar (starts with `gsk_`)
2) Upload one or more documents (PDF/DOCX/TXT) — knowledge base builds automatically
3) Ask your question in the chat box
4) Get accurate answers retrieved from your documents

## Get a GROQ API Key (optional)
- Create a free key in the GROQ Console: https://console.groq.com/keys
- Paste it in the Streamlit sidebar to enable AI Enhanced mode
- Without a key, the app uses Smart Mode automatically

## Tech Stack
- **UI** — Streamlit
- **LLM Framework** — LangChain (`langchain-groq`, `langchain-core`)
- **LLM Provider** — Groq API (`llama-3.1-8b-instant`)
- **Vector Store** — FAISS (`faiss-cpu`)
- **Embeddings** — HuggingFace (`all-MiniLM-L6-v2` via `langchain-huggingface`)
- **Text Splitting** — `langchain-text-splitters` (`RecursiveCharacterTextSplitter`)
- **Doc Parsing** — PyPDF2, python-docx
- **Package Manager** — uv (`pyproject.toml`)

## Project Structure
```
Docuchat/
├─ streamlit_app.py    # Streamlit UI (primary entry)
├─ simple_app.py       # Reusable logic: parsing, analysis, and LangChain+Groq call
├─ pyproject.toml      # Python dependencies (uv)
├─ uv.lock             # Lockfile
├─ README.md           # This file
└─ uploads/            # Temporary user files (gitignored)
```

## Privacy
- No hardcoded API keys in the repo
- Your key, if provided, is only used to call GROQ on your behalf
- Smart Mode runs locally without external calls


