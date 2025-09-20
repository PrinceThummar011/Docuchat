# DocuChat - Document Q&A Application

A modern Flask web application that allows you to chat with your documents using smart analysis and optional AI enhancement.

## 🚀 Features
- 🧠 **Smart Document Analysis** - Works immediately without any setup
- 🤖 **Optional AI Enhancement** - Add your own GROQ API key for advanced AI responses
- 📄 **Multiple File Support** - PDF, DOCX, TXT documents
- 🔒 **Privacy First** - No hardcoded API keys, you control your data
- 🌙 **Modern Dark UI** - ChatGPT-inspired interface
- 📱 **Mobile Responsive** - Works on all devices
- ✅ **Real-time API Key Validation** - Professional format checking

## 🎯 Quick Start with GitHub Codespaces (FREE)

### Deploy in 30 seconds:
1. **Fork/Clone this repository**
2. **Open in Codespaces**: Click "Code" → "Codespaces" → "Create codespace"
3. **Automatic Setup**: Wait 30 seconds for installation
4. **Your app is live!**: Click the port 5000 link when it appears

### Your live URL will be:
`https://[username]-docuchat-[id].github.dev`

## 🔧 Local Development

```bash
# Clone the repository
git clone https://github.com/PrinceThummar011/Docuchat.git
cd Docuchat

# Install dependencies
pip install -r requirements.txt

# Run the app
python simple_app.py

# Open browser to http://localhost:5000
```

## 🔑 API Key Setup (Optional)

For enhanced AI responses:
1. Get a free GROQ API key from [console.groq.com/keys](https://console.groq.com/keys)
2. Enter your API key in the app's "Enhanced AI Features" section
3. The app validates the key format (must start with `gsk_`)

## 📁 Project Structure

```
DocuChat/
├── simple_app.py          # Main Flask application
├── templates/             # HTML templates
│   └── index.html        # Main UI template
├── static/               # CSS and JavaScript
│   ├── style.css        # Dark theme styling
│   └── script.js        # Frontend functionality
├── .devcontainer/        # GitHub Codespaces configuration
├── .github/workflows/    # CI/CD automation
├── requirements.txt      # Python dependencies
├── GITHUB_DEPLOYMENT.md  # Detailed deployment guide
└── README.md            # This file
```

## 🌍 Live Demo

Try the live version deployed on GitHub Codespaces: [View Demo](https://github.com/PrinceThummar011/Docuchat)

## 🛠️ Technology Stack

- **Backend**: Flask 2.3+, Python 3.11
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Document Processing**: PyPDF2, python-docx
- **AI Integration**: GROQ API (user-provided keys)
- **Deployment**: GitHub Codespaces (FREE)

## 📝 How It Works

1. **Upload Documents**: Drag & drop PDF, DOCX, or TXT files
2. **Smart Analysis**: Get intelligent answers without any setup
3. **Enhanced AI**: Optional GROQ API key for advanced responses
4. **Real-time Validation**: API key format checking with helpful errors
5. **Mobile Ready**: Beautiful dark theme that works everywhere

## 🔒 Privacy & Security

- ✅ **No hardcoded secrets** - You provide your own API keys
- ✅ **Local processing** - Smart analysis works offline
- ✅ **User-controlled data** - Your documents, your API access
- ✅ **Format validation** - Prevents invalid API key usage

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/PrinceThummar011/Docuchat/issues)
- 📖 **Documentation**: See `GITHUB_DEPLOYMENT.md` for detailed setup
- 💡 **Features**: Smart analysis works without any API dependencies

---

**Ready to deploy?** Just create a GitHub Codespace and your DocuChat will be live in 30 seconds! 🚀
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
