# session_manager.py - Enhanced session state management for multi-file support

import streamlit as st
import time
from typing import Dict, Any, List

class SessionManager:
    """Manage Streamlit session state with multi-file support"""
    
    def __init__(self):
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'document_processed': False,
            'chat_history': [],
            'document_chunks': [],
            'chunk_embeddings': None,
            'document_name': "",
            'file_list': [],  # List of processed files
            'file_count': 0,  # Number of files processed
            'has_images': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def is_document_processed(self) -> bool:
        """Check if document(s) are processed"""
        return st.session_state.get('document_processed', False)
    
    def set_document_data(self, document_data: Dict[str, Any]):
        """Store processed document data (single or multiple files)"""
        st.session_state.document_chunks = document_data['chunks']
        st.session_state.chunk_embeddings = document_data['embeddings']
        st.session_state.document_name = document_data['filename']
        st.session_state.file_list = document_data.get('file_list', [])
        st.session_state.file_count = document_data.get('file_count', 1)
        st.session_state.has_images = document_data.get('has_images', False)
        st.session_state.document_processed = True
        st.session_state.chat_history = []
    
    def add_message(self, message_type: str, content: str):
        """Add message to chat history"""
        st.session_state.chat_history.append({
            'type': message_type,
            'content': content,
            'timestamp': time.time()
        })
    
    def clear_session(self):
        """Clear all session data"""
        for key in ['document_processed', 'chat_history', 'document_chunks', 
                   'chunk_embeddings', 'document_name', 'file_list', 'file_count', 'has_images']:
            if key in st.session_state:
                del st.session_state[key]
        self._initialize_session_state()
    
    def get_chat_history(self):
        """Get chat history"""
        return st.session_state.get('chat_history', [])
    
    def get_document_data(self):
        """Get current document data"""
        return {
            'chunks': st.session_state.get('document_chunks', []),
            'embeddings': st.session_state.get('chunk_embeddings', None),
            'name': st.session_state.get('document_name', ""),
            'file_list': st.session_state.get('file_list', []),
            'file_count': st.session_state.get('file_count', 0),
            'has_images': st.session_state.get('has_images', False)
        }
    
    def get_file_statistics(self) -> Dict[str, int]:
        """Get statistics about processed files"""
        chunks = st.session_state.get('document_chunks', [])
        
        # Count chunks by file
        file_stats = {}
        for chunk in chunks:
            file_name = chunk.get('file_name', 'Unknown')
            if file_name not in file_stats:
                file_stats[file_name] = {'text_chunks': 0, 'image_chunks': 0}
            
            if chunk['type'] == 'text':
                file_stats[file_name]['text_chunks'] += 1
            elif chunk['type'] == 'image':
                file_stats[file_name]['image_chunks'] += 1
        
        return file_stats
    
    def is_multi_file_session(self) -> bool:
        """Check if current session has multiple files"""
        return st.session_state.get('file_count', 0) > 1