import os
import re
import PyPDF2
import docx
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Load embeddings once at module level (downloads ~90MB model on first run)
_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def validate_groq_api_key(api_key):
    """Validate GROQ API key format and structure"""
    if not api_key or not isinstance(api_key, str):
        return False, "API key is required"
    
    # Remove whitespace
    api_key = api_key.strip()
    
    # Check if it's the placeholder value
    if api_key in ['no-key-needed', '123', 'test', 'demo']:
        return False, "Please enter a valid GROQ API key"
    
    # GROQ API keys typically start with 'gsk_' and have specific length
    if not api_key.startswith('gsk_'):
        return False, "Invalid GROQ API key format. Keys should start with 'gsk_'"
    
    # Check length (GROQ keys are typically around 56 characters)
    if len(api_key) < 30:
        return False, "API key too short. Please check your GROQ API key"
    
    if len(api_key) > 100:
        return False, "API key too long. Please check your GROQ API key"
    
    # Check if it contains only valid characters (letters, numbers, underscores)
    if not re.match(r'^gsk_[A-Za-z0-9_]+$', api_key):
        return False, "Invalid characters in API key. Only letters, numbers, and underscores allowed"
    
    return True, "API key format is valid"

def extract_text_from_file(file_path, filename):
    """Extract text content from uploaded files"""
    try:
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext == '.pdf':
            return extract_pdf_text(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_ext in ['.docx']:
            return extract_docx_text(file_path)
        else:
            return "Could not extract text from this file type."
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return f"Error reading file: {str(e)}"

def extract_pdf_text(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_docx_text(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def build_vector_store(files):
    """
    Build a FAISS vector store from uploaded files.
    files: list of dicts with 'original_name' and 'text_content'
    Returns a FAISS vector store or None if no content.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    for f in files:
        content = f.get("text_content", "").strip()
        if not content:
            continue
        chunks = splitter.create_documents(
            [content],
            metadatas=[{"source": f["original_name"]}]
        )
        docs.extend(chunks)
    if not docs:
        return None
    return FAISS.from_documents(docs, _embeddings)


def get_ai_response(message, vector_store, api_key):
    """Get accurate RAG-based answer using FAISS retrieval + Groq LLM"""
    try:
        # Step 1: Retrieve the top-4 most relevant document chunks
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(message)
        context = "\n\n".join(doc.page_content for doc in docs)

        # Step 2: Send context + question to Groq LLM
        llm = ChatGroq(
            api_key=api_key,
            model_name="llama-3.1-8b-instant",
            max_tokens=1000,
            temperature=0.3,
        )
        messages = [
            SystemMessage(content="You are a helpful assistant. Answer the question using only the provided document context. If the answer is not in the context, say so clearly."),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {message}")
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        error_msg = str(e)
        if any(w in error_msg.lower() for w in ['401', 'authentication', 'invalid api key', 'unauthorized']):
            return "Authentication failed. Please check your API key."
        return f"Error: {error_msg}"

__all__ = [
    'validate_groq_api_key',
    'extract_text_from_file',
    'extract_pdf_text',
    'extract_docx_text',
    'build_vector_store',
    'get_ai_response',
]