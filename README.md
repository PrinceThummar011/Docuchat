# DocuChat - Document Q&A Application

A Streamlit application that allows you to chat with your documents (PDF, images) using AI.

## Features
- Upload and chat with PDF documents
- Upload and ask questions about images
- Support for multiple file types
- Powered by GROQ's fast inference API

## Setup Instructions

### Option 1: Use Online (Recommended)
1. Visit the deployed app: [Your Streamlit Cloud URL]
2. Enter your GROQ API key in the sidebar
3. Start uploading documents and asking questions!

### Option 2: Run Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/PrinceThummar011/Docuchat.git
   cd Docuchat
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get your GROQ API key:
   - Go to https://console.groq.com/keys
   - Sign up/Login
   - Create a new API key

4. Create a `.streamlit/secrets.toml` file:
   ```toml
   GROQ_API_KEY = "your_api_key_here"
   ```

5. Run the app:
   ```bash
   streamlit run app.py
   ```

## How to Get GROQ API Key
1. Visit https://console.groq.com/keys
2. Sign up for a free account
3. Navigate to API Keys section
4. Click "Create API Key"
5. Copy the generated key
6. Paste it in the app's sidebar

## Usage
1. Enter your GROQ API key (if not configured in secrets)
2. Upload your document (PDF or image)
3. Ask questions about the content
4. Get instant AI-powered responses

## Support
If you encounter any issues, please create an issue on GitHub.
