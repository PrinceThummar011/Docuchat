import streamlit as st
from config import Config
from ui.components import UIComponents
from services.document_service import DocumentService
from services.chat_service import ChatService
from utils.session_manager import SessionManager

def main():
    """Main application entry point"""
    # Configure page
    st.set_page_config(
        page_title="DocuChat - AI Document Assistant",
        page_icon="📄",  # Fixed emoji encoding
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize services
    session_manager = SessionManager()
    document_service = DocumentService()
    chat_service = ChatService()
    ui = UIComponents()
    
    # Check API configuration
    if not Config.GROQ_API_KEY:
        ui.show_api_key_error()
        return
    
    # Render main UI
    ui.render_header()
    
    # Sidebar for document upload
    with st.sidebar:
        ui.render_sidebar(document_service, session_manager)
    
    # Main chat interface
    if session_manager.is_document_processed():
        ui.render_chat_interface(chat_service, session_manager)
    else:
        ui.render_welcome_screen()
    
    # Footer and styling
    ui.apply_custom_styling()

if __name__ == "__main__":
    main()