<div align="center">

# 🤖 DocuChat

### RAG-powered document assistant — ask questions, get accurate answers from your own files

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1.2+-1C3C3C?style=flat&logo=chainlink&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=flat)](https://groq.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-0064C8?style=flat)](https://faiss.ai)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](LICENSE)

**[🚀 Live Demo](https://docuchat-by-prince.streamlit.app/)**

</div>

---

## 📌 What is DocuChat?

DocuChat lets you **upload any document** (PDF, DOCX, TXT) and **chat with it** using a full RAG pipeline. Instead of dumping the whole document into a prompt, it semantically retrieves only the most relevant chunks and sends them to Groq's LLM — giving precise, grounded answers.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Multi-format support | Upload PDF, DOCX, and TXT files |
| 🔍 Semantic search | FAISS vector store finds the most relevant passages |
| 🤖 Accurate answers | Only relevant chunks sent to LLM — no hallucination from noise |
| 📚 Multi-document | Query across multiple documents at once |
| ⚡ Fast inference | Powered by Groq's ultra-fast `llama-3.1-8b-instant` |
| 🔒 Private | Your documents never leave your machine |

---

## 🏗️ RAG Architecture

```
  ┌─────────────────────────────────────────────────────────────┐
  │                      INDEXING (on upload)                    │
  │                                                              │
  │   PDF/DOCX/TXT  ──►  Text Extraction  ──►  Text Splitter    │
  │                                              (500 chars)     │
  │                                                  │           │
  │                                                  ▼           │
  │                               HuggingFace Embeddings         │
  │                               (all-MiniLM-L6-v2)            │
  │                                                  │           │
  │                                                  ▼           │
  │                                          FAISS Vector Store  │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │                    RETRIEVAL + GENERATION                    │
  │                                                              │
  │   User Question  ──►  Embed Question  ──►  FAISS Search     │
  │                                          (Top-4 chunks)     │
  │                                                  │           │
  │                                                  ▼           │
  │                            System Prompt + Context + Query   │
  │                                                  │           │
  │                                                  ▼           │
  │                             Groq LLM (llama-3.1-8b-instant) │
  │                                                  │           │
  │                                                  ▼           │
  │                                          Accurate Answer ✅  │
  └─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
Docuchat/
├── docuchat/                   # Main Python package
│   ├── __init__.py             # Package version
│   ├── core/                   # Business logic layer
│   │   ├── __init__.py         # Public API exports
│   │   ├── document.py         # PDF / DOCX / TXT text extraction
│   │   ├── rag.py              # FAISS vector store + RAG pipeline
│   │   └── validator.py        # GROQ API key validation
│   └── ui/                     # Presentation layer
│       ├── __init__.py
│       └── app.py              # Streamlit UI
├── uploads/                    # Temporary uploaded files (gitignored)
├── pyproject.toml              # Project metadata + dependencies (uv)
├── uv.lock                     # Pinned dependency lockfile
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI** | [Streamlit](https://streamlit.io) |
| **LLM Framework** | [LangChain](https://langchain.com) (`langchain-groq`, `langchain-core`) |
| **LLM Provider** | [Groq API](https://groq.com) — `llama-3.1-8b-instant` |
| **Vector Store** | [FAISS](https://faiss.ai) (`faiss-cpu`) |
| **Embeddings** | [HuggingFace](https://huggingface.co) — `all-MiniLM-L6-v2` |
| **Text Splitting** | `langchain-text-splitters` — `RecursiveCharacterTextSplitter` |
| **Doc Parsing** | `PyPDF2`, `python-docx` |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — install with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Install dependencies
```bash
git clone https://github.com/PrinceThummar011/Docuchat.git
cd Docuchat
uv sync
```

### Run the app
```bash
uv run streamlit run docuchat/ui/app.py
```
Open **http://localhost:8501** in your browser.

---

## 🚀 How To Use

```
Step 1 ──► Get a free GROQ API key at https://console.groq.com/keys
           Paste it in the sidebar (starts with gsk_)

Step 2 ──► Upload your documents (PDF / DOCX / TXT)
           Knowledge base builds automatically in the background

Step 3 ──► Ask any question in the chat box
           e.g. "What are the key responsibilities?"
                "Summarize the contract terms"
                "What is the project deadline?"

Step 4 ──► Get accurate, source-grounded answers ✅
```

---

## 🔑 Get a Free GROQ API Key

1. Go to **[console.groq.com/keys](https://console.groq.com/keys)**
2. Sign up / Log in (free)
3. Click **Create API Key**
4. Copy the key (starts with `gsk_`)
5. Paste it in the DocuChat sidebar

> Groq offers a generous free tier — no credit card required.

---

## 🔒 Privacy & Security

- ✅ No API keys are stored or hardcoded in the repo
- ✅ Uploaded documents are stored **locally only** in `uploads/`
- ✅ Your key is used only to call the Groq API on your behalf
- ✅ The embedding model (`all-MiniLM-L6-v2`) runs **100% locally**
- ✅ Only the top-4 most relevant text chunks leave your machine (to Groq)


