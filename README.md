# DocuChat (Streamlit)

Chat with your documents using smart local analysis or optional AI‑enhanced answers powered by your own GROQ API key.

## Features
- Upload and read PDF, DOCX, and TXT files
- Ask questions and receive summarized or extracted answers
- Two modes:
  - 📄 Smart Mode (no API key required)
  - 🤖 AI Enhanced (add your `gsk_...` GROQ API key)

## Requirements
- Python 3.9+
- pip

## Setup
```bash
pip install -r requirements.txt
```

## Run Locally
```bash
streamlit run streamlit_app.py
```
Then open `http://localhost:8501`.

## How To Use
1) Upload one or more documents from the left sidebar (PDF/DOCX/TXT)
2) Optional: paste your GROQ API key (starts with `gsk_`) for AI Enhanced answers
3) Ask your question in the chat box at the bottom
4) Remove any file using the trash icon if needed

## Get a GROQ API Key (optional)
- Create a free key in the GROQ Console: https://console.groq.com/keys
- Paste it in the Streamlit sidebar to enable AI Enhanced mode
- Without a key, the app uses Smart Mode automatically

## Deploy to Streamlit Cloud
- App file: `streamlit_app.py`
- Python version: auto from `requirements.txt` (3.9+)
- Optional secrets: set `GROQ_API_KEY` in Streamlit Cloud Secrets (shared across all users)
- Note: Files saved in `uploads/` are ephemeral in Streamlit Cloud (cleared on restart)

## Project Structure
```
Docuchat/
├─ streamlit_app.py    # Streamlit UI (primary entry)
├─ simple_app.py       # Reusable logic: parsing, analysis, and GROQ call
├─ requirements.txt    # Python dependencies
├─ README.md           # This file
└─ uploads/            # Temporary user files (gitignored)
```

## Privacy
- No hardcoded API keys in the repo
- Your key, if provided, is only used to call GROQ on your behalf
- Smart Mode runs locally without external calls

## License
This project is provided as-is for educational and personal use.
