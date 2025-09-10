# config.py - Enhanced Configuration management with multi-file support

import streamlit as st
import os

class Config:
    """Application configuration with multi-file support"""
    
    # API Configuration
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except (KeyError, AttributeError):
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    
    # File upload limits
    MAX_FILE_SIZE =  10 * 1024 * 1024  # 10MB per file
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB per image
    MAX_FILES_COUNT = 10  # Maximum number of files that can be uploaded at once
    MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total for all files combined
    
    # Processing parameters
    CHUNK_SIZE = 400
    OVERLAP = 80
    TOP_K_CHUNKS = 8  # Increased for multi-file support
    SIMILARITY_THRESHOLD = 0.05
    
    # Multi-file specific settings
    MAX_CHUNKS_PER_FILE = 1000  # Prevent any single file from dominating
    ENABLE_CROSS_FILE_REFERENCES = True  # Enable references across files
    
    # Model settings
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    LLM_MODEL = 'llama-3.3-70b-versatile'  # Groq model
    
    # Image processing
    SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp']
    
    # Document processing
    SUPPORTED_DOCUMENT_FORMATS = {
        'pdf': ['pdf'],
        'word': ['docx'],
        'text': ['txt'],
        'markdown': ['md', 'markdown']
    }
    
    # OCR Enhancement
    ENABLE_OCR = True  # Set to False to disable OCR processing
    OCR_CONFIDENCE_THRESHOLD = 60  # Minimum confidence for OCR text
    
    # Multi-file processing settings
    ENABLE_FILE_COMPARISON = True  # Enable cross-file comparison features
    FILE_SIMILARITY_THRESHOLD = 0.7  # Threshold for detecting similar content across files
    
    @classmethod
    def get_supported_extensions(cls):
        """Get all supported file extensions"""
        extensions = []
        for format_list in cls.SUPPORTED_DOCUMENT_FORMATS.values():
            extensions.extend(format_list)
        return extensions
    
    @classmethod
    def get_file_type_icon(cls, file_extension):
        """Get emoji icon for file type"""
        icons = {
            'pdf': '📄',
            'docx': '📝',
            'txt': '📃',
            'md': '📋',
            'markdown': '📋'
        }
        return icons.get(file_extension.lower(), '📄')
    
    @classmethod
    def is_file_size_valid(cls, file_size, is_multi_file=False):
        """Check if file size is within limits"""
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File size exceeds {cls.MAX_FILE_SIZE // (1024*1024)}MB limit"
        return True, "OK"
    
    @classmethod
    def is_total_size_valid(cls, total_size):
        """Check if total size of all files is within limits"""
        if total_size > cls.MAX_TOTAL_SIZE:
            return False, f"Total size exceeds {cls.MAX_TOTAL_SIZE // (1024*1024)}MB limit"
        return True, "OK"
    
    @classmethod
    def is_file_count_valid(cls, file_count):
        """Check if number of files is within limits"""
        if file_count > cls.MAX_FILES_COUNT:
            return False, f"Maximum {cls.MAX_FILES_COUNT} files allowed"
        return True, "OK"