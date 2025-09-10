# 📄 DocuChat - AI Document Assistant

An intelligent document chat application that allows you to upload multiple documents and have natural conversations about their content using advanced AI technology.

## 🌟 Features

- **📁 Multi-Format Support**: Upload PDF, DOCX, TXT, and Markdown files
- **�📚 Multi-File Processing**: Upload and chat with multiple documents simultaneously
- **🤖 AI-Powered Conversations**: Chat naturally about your documents using Groq's fast LLM models
- **🔍 Cross-Document Search**: Find relevant information across all uploaded documents
- **📍 Source References**: Get exact citations with file names, page numbers, paragraphs, and line references
- **💡 Smart Suggestions**: Auto-generated questions to help explore your document collection
- **💬 Chat History**: Maintain conversation context throughout your session
- **⚡ Fast Performance**: Optimized document processing with chunking and caching
- **🗂️ Document Management**: View, remove, and organize your uploaded documents

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd docu-chat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
   
   Or set environment variable:
   ```bash
   set GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🏗️ Project Structure

```
docu-chat/
├── main.py                 # Main Streamlit application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .streamlit/
│   ├── secrets.toml        # API keys (create this)
│   └── secrets.toml.example # Template for secrets
├── services/
│   ├── document_service.py # Document processing & embeddings
│   └── chat_service.py     # AI chat functionality
├── ui/
│   └── components.py       # UI components and rendering
└── utils/
    └── session_manager.py  # Session state management
```

## 🔧 Configuration

Edit `config.py` to customize:

- **Model Settings**: Change LLM model, temperature, max tokens
- **Document Processing**: Adjust chunk size, overlap, max file size
- **Multi-File Settings**: Configure max files per session, total size limits
- **UI Behavior**: Modify suggestions count, chat history limits

## 📋 Usage

### Single Document Mode
1. **Upload Document**: Drag and drop or browse for a file (PDF, DOCX, TXT, MD)
2. **Wait for Processing**: Document is automatically chunked and indexed
3. **Start Chatting**: Ask questions about your document content

### Multi-Document Mode
1. **Upload Multiple Files**: 
   - Use the file uploader to select multiple documents at once
   - Or upload files one by one to build your document collection
2. **Document Management**:
   - View all uploaded documents in the sidebar
   - Remove unwanted documents with the delete button
   - See processing status for each file
3. **Cross-Document Conversations**:
   - Ask questions that span across all your documents
   - Compare information between different files
   - Get comprehensive answers from your entire document collection
4. **Source Tracking**:
   - All responses include file names and specific locations
   - Easily identify which document contains the information

### Advanced Features
- **Explore Suggestions**: Use auto-generated questions to discover insights
- **View Sources**: Click on references to see exact document locations
- **Filter by Document**: Ask questions about specific files
- **Comparative Analysis**: Compare data across multiple documents

## 📊 Multi-File Examples

### Example Queries for Multiple Documents:
```
"Compare the budget allocations mentioned in all the financial reports"
"What are the common themes across these research papers?"
"Summarize the key points from all uploaded meeting minutes"
"Find discrepancies between the contract terms in different files"
"What information about Project X is mentioned across all documents?"
```

## 🔐 Security Features

- ✅ File type validation for all uploads
- ✅ Individual and total file size limits
- ✅ Secure API key handling
- ✅ Input sanitization
- ✅ Error handling and logging
- ✅ Session isolation for multi-user environments

## 🛠️ Technical Details

### AI Models
- **LLM**: Groq's Llama models for fast inference
- **Embeddings**: Sentence Transformers for semantic search
- **Search**: Cosine similarity for document retrieval across all files

### Multi-Document Processing
- **Unified Index**: All documents are processed into a single searchable index
- **Source Tracking**: Each chunk maintains file origin and location metadata
- **Batch Processing**: Efficient handling of multiple file uploads
- **Memory Management**: Optimized storage for large document collections

### Document Processing
- **Chunking**: Smart text splitting with overlap for each document
- **Metadata**: Extracts file names, page numbers, sections, and line references
- **Caching**: Efficient processing with session state management
- **Cross-Referencing**: Links related content across different documents

## 📊 Supported File Types

| Format | Extension | Multi-File Features |
|--------|-----------|-------------------|
| PDF | `.pdf` | Page numbers, cross-document search |
| Word | `.docx` | Paragraph tracking, document comparison |
| Text | `.txt` | Line numbers, simple merging |
| Markdown | `.md` | Section headers, structured comparison |

## 🚀 Performance Tips

### Single Document
- **File Size**: Keep documents under 10MB for best performance
- **Chunk Size**: Larger chunks (1000+ chars) work better for complex queries

### Multiple Documents
- **Total Size**: Recommended limit of 50MB total across all files
- **File Count**: Optimal performance with 2-10 documents
- **Processing**: Upload files gradually for better user experience
- **Memory**: Clear document collection periodically for long sessions

## 📈 Multi-File Limits

| Metric | Recommended | Maximum |
|--------|-------------|---------|
| Files per session | 5-10 | 20 |
| Total file size | 50MB | 100MB |
| Individual file size | 10MB | 25MB |
| Processing time | <30s | <2min |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**"No API key found"**
- Ensure `GROQ_API_KEY` is set in `.streamlit/secrets.toml` or environment variables

**"Document processing failed"**
- Check file format and size limits
- Ensure files are not corrupted or password-protected
- Try uploading files one at a time

**"Slow response times with multiple files"**
- Reduce the number of uploaded documents
- Try using a faster Groq model in `config.py`
- Clear document collection and re-upload essential files only

**"Memory issues with large document collections"**
- Reduce chunk size in configuration
- Upload fewer documents per session
- Restart the application to clear memory

**"Cross-document search not working"**
- Ensure all documents are fully processed (check status indicators)
- Try more specific queries that mention file names
- Verify document content is text-extractable

## 📞 Support

- **Issues**: [GitHub Issues](link-to-issues)
- **Documentation**: Check inline code comments
- **API Documentation**: [Groq API Docs](https://console.groq.com/docs)

## 🎯 Roadmap

- [x] Multi-file upload and processing
- [x] Cross-document search and comparison
- [ ] Support for more file formats (PPT, CSV, JSON, XLSX)
- [ ] Document clustering and organization
- [ ] Advanced multi-document analytics
- [ ] Export comprehensive reports
- [ ] Document versioning and history
- [ ] User authentication and document sharing
- [ ] Real-time collaboration features
- [ ] Advanced search filters and faceted search

## 🆕 Recent Updates

### v2.0 - Multi-File Support
- ✅ Upload and process multiple documents simultaneously
- ✅ Cross-document search and question answering
- ✅ Enhanced source referencing with file names
- ✅ Document management interface
- ✅ Improved performance for document collections
- ✅ Batch processing capabilities

---

**Developed by Prince**

*Last updated: 04 September 2025 - Multi-File Edition*