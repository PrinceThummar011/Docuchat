from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import PyPDF2
import docx
import requests
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store sessions (in production, use Redis or database)
sessions = {}

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
    """Get AI response using Groq API"""
    try:
        print(f"🔑 API Key length: {len(api_key) if api_key else 0}")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""Based on the following document content, please answer the user's question.

Document Content:
{document_content[:3000]}...

User Question: {message}

Please provide a helpful and accurate answer based on the document content."""

        # Try different models if one fails
        models = ['llama-3.1-8b-instant', 'llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
        
        for model in models:
            try:
                print(f"🤖 Trying model: {model}")
                payload = {
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'model': model,
                    'max_tokens': 1000,
                    'temperature': 0.7
                }
                
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                print(f"📡 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ AI response received successfully")
                    return result['choices'][0]['message']['content']
                elif response.status_code == 400:
                    error_data = response.json()
                    print(f"⚠️ Model {model} error: {error_data}")
                    # Try next model if this one is not available
                    continue
                elif response.status_code == 401:
                    print("❌ Authentication failed - Invalid API key")
                    return "Authentication failed. Please check your API key is valid."
                else:
                    print(f"❌ API Error: {response.status_code} - {response.text}")
                    return f"Error from AI service: {response.status_code} - {response.text}"
            except Exception as e:
                print(f"❌ Exception with model {model}: {str(e)}")
                # Try next model
                continue
        
        return "All AI models are currently unavailable. Please try again later or check your API key."
            
    except Exception as e:
        print(f"❌ General error in get_ai_response: {str(e)}")
        return f"Error getting AI response: {str(e)}"

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        session_id = request.form.get('session_id', str(uuid.uuid4()))
        
        if session_id not in sessions:
            sessions[session_id] = {
                'files': [],
                'conversation': []
            }
        
        uploaded_files = []
        
        for file in files:
            if file and file.filename:
                # Validate file type
                allowed_extensions = {'.pdf', '.txt', '.docx', '.doc'}
                file_ext = os.path.splitext(file.filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    continue
                
                # Secure filename and save
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Simple file storage with text extraction
                file_text = extract_text_from_file(file_path, filename)
                sessions[session_id]['files'].append({
                    'id': unique_filename,
                    'original_name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'text_content': file_text,
                    'uploaded_at': datetime.now().isoformat()
                })
                uploaded_files.append({
                    'id': unique_filename,
                    'name': filename,
                    'size': os.path.getsize(file_path)
                })
        
        if not uploaded_files:
            return jsonify({'error': 'No valid files could be processed'}), 400
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'files': uploaded_files,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully'
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

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

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        api_key = data.get('api_key', '').strip()
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session_data = sessions[session_id]
        
        if not session_data['files']:
            return jsonify({'error': 'No documents uploaded'}), 400
        
        # Validate API key if provided
        use_ai = False
        if api_key and api_key != 'no-key-needed':
            is_valid, validation_message = validate_groq_api_key(api_key)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'response': f"❌ **API Key Error**: {validation_message}\n\n📝 **How to get a valid GROQ API key:**\n1. Go to https://console.groq.com/keys\n2. Sign up for free\n3. Create a new API key\n4. Copy the key (starts with 'gsk_')\n\n🧠 **Using Smart Analysis instead** for your question..."
                }), 400
            else:
                use_ai = True
                print(f"✅ Valid GROQ API key provided")
        
        # Get all document content
        all_text = ""
        file_names = []
        for file_data in session_data['files']:
            file_names.append(file_data['original_name'])
            all_text += f"\n\n--- Content from {file_data['original_name']} ---\n"
            all_text += file_data.get('text_content', 'Could not extract text from this file.')
        
        file_list = ", ".join(file_names)
        
        # Use AI API if user provided a valid key, otherwise use smart analysis
        if use_ai:
            try:
                print(f"🤖 Using AI API for enhanced response...")
                response = get_ai_response(message, all_text, api_key)
                # Check if AI response is valid
                if response and not response.startswith("All AI models are currently unavailable"):
                    response = f"🤖 **AI Enhanced Response:**\n\n{response}"
                else:
                    print(f"❌ AI API failed, falling back to smart analysis")
                    response = analyze_document_content(message, all_text)
                    response = f"📄 **Smart Analysis** (AI service unavailable):\n\n{response}"
            except Exception as e:
                print(f"❌ AI API error, using smart analysis: {str(e)}")
                response = analyze_document_content(message, all_text)
                response = f"📄 **Smart Analysis** (AI error):\n\n{response}"
        else:
            # Use smart document analysis
            response = analyze_document_content(message, all_text)
            if api_key and api_key != 'no-key-needed':
                # User tried to use API key but it was invalid - already handled above
                pass
            else:
                response = f"📄 **Smart Analysis:**\n\n{response}\n\n💡 *Tip: Add your own GROQ API key for enhanced AI responses!*"
        
        # Store conversation
        session_data['conversation'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        session_data['conversation'].append({
            'role': 'assistant', 
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        return jsonify({'error': 'Chat request failed'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_session():
    """Clear chat session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id and session_id in sessions:
            # Clear conversation but keep files
            sessions[session_id]['conversation'] = []
            return jsonify({'success': True, 'message': 'Session cleared'})
        
        return jsonify({'error': 'Invalid session'}), 400
        
    except Exception as e:
        print(f"Clear session error: {str(e)}")
        return jsonify({'error': 'Failed to clear session'}), 500

@app.route('/api/remove_file', methods=['POST'])
def remove_file():
    """Remove uploaded file"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        file_id = data.get('file_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session_data = sessions[session_id]
        
        # Find and remove file
        file_to_remove = None
        for i, file_data in enumerate(session_data['files']):
            if file_data['id'] == file_id:
                file_to_remove = session_data['files'].pop(i)
                break
        
        if file_to_remove:
            # Remove physical file
            if os.path.exists(file_to_remove['path']):
                os.remove(file_to_remove['path'])
            
            return jsonify({'success': True, 'message': 'File removed'})
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        print(f"Remove file error: {str(e)}")
        return jsonify({'error': 'Failed to remove file'}), 500

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """Get session information"""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = sessions[session_id]
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'files': [
                {
                    'id': f['id'],
                    'name': f['original_name'], 
                    'size': f['size']
                } for f in session_data['files']
            ],
            'conversation': session_data['conversation']
        })
        
    except Exception as e:
        print(f"Get session error: {str(e)}")
        return jsonify({'error': 'Failed to get session'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting DocuChat Server...")
    print("📄 Upload your documents and start chatting!")
    print("🤖 Smart document analysis included - Add your own API key for AI enhancement!")
    print("🔑 No hardcoded API keys - Users provide their own keys for enhanced features")
    print("🌐 Open your browser and go to: http://localhost:5000")
    
    # Get port from environment for deployment platforms
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        debug=debug, 
        host='0.0.0.0', 
        port=port,
        use_reloader=debug
    )