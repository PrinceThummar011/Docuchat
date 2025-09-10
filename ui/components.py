import streamlit as st
import time
from config import Config

class UIComponents:
    """Handle all UI rendering with multi-file support"""
    
    def render_header(self):
        """Render main header"""
        st.title("📄 DocuChat")
        st.subheader("Your AI-Powered Document Assistant")
        st.markdown("Upload one or multiple documents and ask questions about their content!")
    
    def show_api_key_error(self):
        """Show API key configuration error"""
        st.error("""
        🔑 **API Key Required!** 
        
        Please set up your Groq API key using one of these methods:
        
        **Method 1: Environment Variable**
        ```bash
        export GROQ_API_KEY="your-api-key-here"
        ```
        
        **Method 2: Streamlit Secrets**
        1. Create folder: `.streamlit` in your project directory
        2. Create file: `.streamlit/secrets.toml`
        3. Add: `GROQ_API_KEY = "your-api-key-here"`
        
        **Get API Key:** [Groq Console](https://console.groq.com)
        """)
    
    def render_sidebar(self, document_service, session_manager):
        """Render sidebar with multi-file upload"""
        st.header("📁 Document Upload")
        
        # Show supported formats
        st.markdown("""
        **Supported formats:**
        - 📄 PDF files (.pdf)
        - 📝 Word documents (.docx)
        - 📃 Text files (.txt)
        - 📋 Markdown files (.md)
        
        ✨ **New: Upload multiple files at once!**
        """)
        
        # Multi-file uploader
        uploaded_files = st.file_uploader(
            "Choose document files",
            type=["pdf", "docx", "txt", "md", "markdown"],
            help=f"Maximum file size: {Config.MAX_FILE_SIZE // (1024*1024)}MB per file",
            accept_multiple_files=True  # Enable multiple file selection
        )
        
        if uploaded_files:
            # Check file sizes
            valid_files = []
            total_size = 0
            
            for uploaded_file in uploaded_files:
                if uploaded_file.size > Config.MAX_FILE_SIZE:
                    st.error(f"File {uploaded_file.name} ({uploaded_file.size / (1024*1024):.1f}MB) exceeds the maximum limit.")
                else:
                    valid_files.append(uploaded_file)
                    total_size += uploaded_file.size
            
            if valid_files:
                # Show file list with info
                st.markdown("**📋 Selected Files:**")
                for i, file in enumerate(valid_files, 1):
                    file_type = file.name.split('.')[-1].upper()
                    file_size = file.size / 1024
                    st.markdown(f"{i}. **{file.name}** ({file_type}, {file_size:.1f} KB)")
                
                # Show total info
                if len(valid_files) > 1:
                    st.info(f"📊 **Total:** {len(valid_files)} files, {total_size / 1024:.1f} KB")
                
                # Process button
                button_text = f"🚀 Process {len(valid_files)} Document{'s' if len(valid_files) > 1 else ''}"
                if st.button(button_text, type="primary"):
                    with st.spinner(f"Processing {len(valid_files)} document(s)..."):
                        document_data = document_service.process_document(valid_files)
                        if document_data:
                            session_manager.set_document_data(document_data)
                            st.success(f"✅ {len(valid_files)} document(s) processed successfully!")
                            st.balloons()  # Celebration for multiple files!
                            st.rerun()
        
        # Show document info if processed
        if session_manager.is_document_processed():
            self._render_document_info(session_manager)
    
    def apply_custom_styling(self):
        """Apply minimal CSS styling"""
        st.markdown("""
        <style>
            .stTextInput > div > div > input {
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            
            .stButton > button {
                border-radius: 6px;
            }
            
            .stFileUploader {
                border-radius: 8px;
            }
            
            .stChatInput > div > div > input {
                border-radius: 20px;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render_welcome_screen(self):
        """Render welcome screen"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 10px; margin: 2rem 0;">
                <h3>👋 Welcome to DocuChat!</h3>
                <p>Upload single or multiple documents to get started.</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_document_info(self, session_manager):
        """Render document information"""
        st.markdown("---")
        doc_data = session_manager.get_document_data()
        
        if session_manager.is_multi_file_session():
            st.markdown("**🗂️ Document Collection:**")
            st.success(f"📚 **{doc_data['file_count']} files loaded**")
        else:
            st.markdown("**📋 Current Document:**")
            st.info(f"📄 {doc_data['name']}")
        
        if st.button("🗑️ Start New Chat", type="secondary"):
            session_manager.clear_session()
            st.rerun()
    
    def render_chat_interface(self, chat_service, session_manager):
        """Render main chat interface with multi-file support"""
        doc_data = session_manager.get_document_data()
        
        # Enhanced header for multi-file sessions
        if session_manager.is_multi_file_session():
            st.markdown(f"### 💬 Chatting with: **{doc_data['file_count']} Documents**")
            with st.expander("📂 View Document Collection", expanded=False):
                for file_name in doc_data['file_list']:
                    st.markdown(f"• {file_name}")
        else:
            file_type = doc_data.get('file_type', 'unknown').upper()
            st.markdown(f"### 💬 Chatting with: `{doc_data['name']}` ({file_type})")
        
        # Show suggested questions if no chat history
        chat_history = session_manager.get_chat_history()
        if not chat_history:
            self._render_suggested_questions(chat_service, session_manager, doc_data)
        
        # Display chat messages
        self._render_chat_messages(chat_history)
        
        # Chat input
        self._render_chat_input(chat_service, session_manager, doc_data)
    
    def _render_chat_messages(self, chat_history):
        """Render chat message history"""
        for message in chat_history:
            if message['type'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
    
    def _render_chat_input(self, chat_service, session_manager, doc_data):
        """Render chat input form with multi-file context"""
        st.markdown("---")
        
        # Show context hint for multi-file sessions
        if session_manager.is_multi_file_session():
            st.markdown("""
            <div style="background-color: #f0f8ff; border: 2px solid #4CAF50; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; color: #2c3e50;">
                💡 <strong style="color: #27ae60;">Multi-File Tip:</strong> You can ask questions that compare information across all your documents!
            </div>
            """, unsafe_allow_html=True)
        
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])
            
            with col1:
                placeholder_text = "Ask a question about your document"
                if session_manager.is_multi_file_session():
                    placeholder_text += "s (e.g., Which file mentions pricing? Compare the conclusions...)"
                else:
                    placeholder_text += " (e.g., What are the main findings? Who are the key people mentioned?)"
                
                user_input = st.text_input(
                    f"Ask a question about your document{'s' if session_manager.is_multi_file_session() else ''}:",
                    placeholder=placeholder_text,
                    label_visibility="collapsed"
                )
            
            with col2:
                submit_button = st.form_submit_button("Send", type="primary")
        
        if submit_button and user_input.strip():
            self._process_question(user_input, chat_service, session_manager, doc_data)
    
    def _process_question(self, question, chat_service, session_manager, doc_data):
        """Process user question and generate response with multi-file context"""
        session_manager.add_message('user', question)
        
        search_message = "🤔 Searching through your document"
        if session_manager.is_multi_file_session():
            search_message += f"s ({doc_data['file_count']} files)"
        search_message += "..."
        
        with st.spinner(search_message):
            try:
                from services.document_service import DocumentService
                document_service = DocumentService()
                
                relevant_chunks = document_service.find_relevant_chunks(
                    question, doc_data['chunks'], doc_data['embeddings']
                )
                
                if not relevant_chunks:
                    if session_manager.is_multi_file_session():
                        answer = "I could not find an answer to that in any of your documents. Could you try rephrasing your question or asking about something else?"
                    else:
                        answer = "I could not find an answer to that in the document. Could you try rephrasing your question or asking about something else?"
                else:
                    answer = chat_service.generate_answer(question, relevant_chunks)
                
                session_manager.add_message('assistant', answer)
                
            except Exception as e:
                session_manager.add_message('assistant', f"Sorry, I encountered an error: {str(e)}")
        
        st.rerun()
    
    def _render_suggested_questions(self, chat_service, session_manager, doc_data):
        """Render suggested questions with multi-file awareness"""
        st.markdown("#### 💡 Suggested Questions:")
        
        # Get suggestions based on whether it's multi-file or single file
        if session_manager.is_multi_file_session():
            suggested_questions = self._get_multi_file_suggestions(doc_data)
        else:
            suggested_questions = chat_service.get_suggested_questions(doc_data['chunks'])
        
        # Render suggestion buttons
        if len(suggested_questions) <= 3:
            cols = st.columns(len(suggested_questions))
            for i, question in enumerate(suggested_questions):
                with cols[i]:
                    if st.button(f"❓ {question}", key=f"suggestion_{i}"):
                        self._process_question(question, chat_service, session_manager, doc_data)
        else:
            # If more than 3 suggestions, use 2 rows
            cols1 = st.columns(3)
            cols2 = st.columns(max(1, len(suggested_questions) - 3))
            
            for i, question in enumerate(suggested_questions):
                if i < 3:
                    with cols1[i]:
                        if st.button(f"❓ {question}", key=f"suggestion_{i}"):
                            self._process_question(question, chat_service, session_manager, doc_data)
                else:
                    with cols2[i-3]:
                        if st.button(f"❓ {question}", key=f"suggestion_{i}"):
                            self._process_question(question, chat_service, session_manager, doc_data)
    
    def _get_multi_file_suggestions(self, doc_data):
        """Get suggestions specifically for multi-file sessions"""
        suggestions = [
            "What topics are covered across all documents?",
            "Compare the main points from different files",
            "Which document contains information about...?"
        ]
        
        # Add content-specific suggestions
        all_text = " ".join([chunk['text'][:100] for chunk in doc_data['chunks'] if chunk['type'] == 'text'][:10])
        text_lower = all_text.lower()
        
        if 'price' in text_lower or 'cost' in text_lower or '$' in all_text:
            suggestions.append("Compare costs mentioned in different documents")
        elif 'date' in text_lower or 'deadline' in text_lower:
            suggestions.append("What are the key dates across all files?")
        elif 'requirement' in text_lower:
            suggestions.append("What are the requirements mentioned in each document?")
        
        return suggestions[:4]
