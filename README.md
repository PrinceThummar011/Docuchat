# DocuChat - AI Document Assistant

A simple web application that allows you to chat with your documents using AI. Upload PDF, DOCX, or TXT files and ask questions about their content.

## 🚀 Live Demo

Try the live demo: **[DocuChat Live Demo](https://upgraded-space-bassoon-r47rv6pgv6x9fvqg-5000.app.github.dev/)**

*Note: The demo uses a limited API quota. For full functionality, please run the application locally with your own Groq API key.*

## Features

- 📄 Upload and extract text from PDF, DOCX, and TXT files
- 🤖 Chat with your documents using AI (powered by Groq API)
- 💬 Interactive chat interface
- 🎨 Clean and modern web interface
- 📱 Responsive design

## Requirements

- Python 3.7+
- Groq API Key

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python simple_app.py
   ```

2. Open your web browser and go to `http://localhost:5000`

3. Enter your Groq API key when prompted

4. Upload a document (PDF, DOCX, or TXT file)

5. Start chatting with your document!

## How to Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into the application

## Supported File Types

- PDF files (.pdf)
- Word documents (.docx)
- Text files (.txt)

## Project Structure

```
Docuchat/
├── simple_app.py          # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # CSS styles
│   └── script.js         # JavaScript functionality
└── uploads/              # Uploaded files storage
```

