import os
import re
import PyPDF2
import docx
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

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
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def get_ai_response(message, document_content, api_key):
    """Get AI response using LangChain + Groq"""
    print(f"🔑 API Key length: {len(api_key) if api_key else 0}")

    models = ['llama-3.1-8b-instant', 'llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']

    messages = [
        SystemMessage(content="You are a helpful assistant that answers questions based on document content."),
        HumanMessage(content=f"""Based on the following document content, please answer the user's question.

Document Content:
{document_content[:3000]}...

User Question: {message}

Please provide a helpful and accurate answer based on the document content.""")
    ]

    for model in models:
        try:
            print(f"🤖 Trying model: {model}")
            llm = ChatGroq(
                api_key=api_key,
                model_name=model,
                max_tokens=1000,
                temperature=0.7
            )
            response = llm.invoke(messages)
            print("✅ AI response received successfully")
            return response.content
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Exception with model {model}: {error_msg}")
            if any(word in error_msg.lower() for word in ['401', 'authentication', 'invalid api key', 'unauthorized']):
                return "Authentication failed. Please check your API key is valid."
            # Try next model
            continue

    return "All AI models are currently unavailable. Please try again later or check your API key."

def analyze_document_content(message, document_content):
    """Analyze document content and provide intelligent responses without API"""
    message_lower = message.lower()
    content_words = document_content.lower().split()
    
    # Extract key information from document
    lines = document_content.split('\n')
    sentences = document_content.split('.')
    
    if "summary" in message_lower or "summarize" in message_lower:
        # Create summary from first few lines and key sentences
        summary_lines = [line.strip() for line in lines[:10] if line.strip() and len(line.strip()) > 10]
        return f"**Document Summary:**\n\n" + "\n".join(summary_lines[:5]) + f"\n\n*Document contains {len(content_words)} words across {len(lines)} lines.*"
    
    elif "main topic" in message_lower or "about" in message_lower:
        # Extract key topics from first paragraph
        first_paragraph = ""
        for line in lines[:15]:
            if line.strip():
                first_paragraph += line.strip() + " "
            if len(first_paragraph) > 300:
                break
        return f"**Main Topic:**\n\n{first_paragraph[:500]}..."
    
    elif "key points" in message_lower or "important" in message_lower:
        # Find lines that might contain key points
        key_lines = []
        for line in lines:
            line = line.strip()
            if line and (len(line) > 20 and len(line) < 200):
                if any(word in line.lower() for word in ['position', 'role', 'responsibility', 'salary', 'date', 'location', 'company', 'department']):
                    key_lines.append(f"• {line}")
        
        if key_lines:
            return f"**Key Points Found:**\n\n" + "\n".join(key_lines[:8])
        else:
            return f"**Key Information:**\n\n" + "\n".join([f"• {line.strip()}" for line in lines[:8] if line.strip() and len(line.strip()) > 10])
    
    elif "find" in message_lower or "search" in message_lower:
        # Search for specific terms in the message
        search_terms = [word for word in message.split() if len(word) > 3 and word.lower() not in ['find', 'search', 'about', 'what', 'where', 'when', 'which']]
        
        found_lines = []
        for line in lines:
            for term in search_terms:
                if term.lower() in line.lower():
                    found_lines.append(f"• {line.strip()}")
                    break
        
        if found_lines:
            return f"**Found information related to '{' '.join(search_terms)}':**\n\n" + "\n".join(found_lines[:6])
        else:
            return f"**Search Results:**\nI searched for '{' '.join(search_terms)}' but didn't find specific matches. Here's the document overview:\n\n" + "\n".join([line.strip() for line in lines[:5] if line.strip()])[:400] + "..."
    
    elif any(word in message_lower for word in ['company', 'organization', 'employer']):
        # Find company/organization information
        company_lines = []
        for line in lines:
            if any(word in line.lower() for word in ['company', 'ltd', 'inc', 'corp', 'organization', 'pvt']):
                company_lines.append(f"• {line.strip()}")
        return f"**Company/Organization Information:**\n\n" + ("\n".join(company_lines[:5]) if company_lines else "Company information not clearly identified in the document.")
    
    elif any(word in message_lower for word in ['date', 'when', 'time']):
        # Find dates in the document
        date_lines = []
        for line in lines:
            if any(char.isdigit() for char in line) and any(word in line.lower() for word in ['date', '2024', '2023', '2025', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
                date_lines.append(f"• {line.strip()}")
        return f"**Date Information:**\n\n" + ("\n".join(date_lines[:5]) if date_lines else "No clear date information found.")
    
    else:
        # General question - provide overview
        overview_lines = [line.strip() for line in lines[:12] if line.strip() and len(line.strip()) > 15]
        return f"**Document Overview:**\n\nRegarding your question: *{message}*\n\n" + "\n".join(overview_lines[:6])

__all__ = [
    'validate_groq_api_key',
    'extract_text_from_file',
    'extract_pdf_text',
    'extract_docx_text',
    'get_ai_response',
    'analyze_document_content',
]