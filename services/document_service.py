# document_service.py - Enhanced Document processing with multi-file support

import PyPDF2
import fitz  # PyMuPDF
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import re
import streamlit as st
from config import Config
from PIL import Image
import io
import pytesseract
from docx import Document as DocxDocument
import tempfile
import os

class DocumentService:
    """Handle all document processing operations with multi-file support"""
    
    def __init__(self):
        self.embedding_model = None
    
    @st.cache_resource
    def _load_embedding_model(_self):
        """Load and cache the embedding model"""
        return SentenceTransformer(Config.EMBEDDING_MODEL)
    
    def get_embedding_model(self):
        """Get the embedding model instance"""
        if not self.embedding_model:
            self.embedding_model = self._load_embedding_model()
        return self.embedding_model
    
    def extract_content_from_pdf(self, pdf_file, file_index: int = 0) -> List[Dict]:
        """Extract both text and images from PDF"""
        try:
            # Reset file pointer
            pdf_file.seek(0)
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            content_chunks = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    content_chunks.append({
                        'type': 'text',
                        'content': text,
                        'page': page_num + 1,
                        'file_name': pdf_file.name,
                        'file_index': file_index,
                        'chunk_id': len(content_chunks)
                    })
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            
                            # Try to extract text from image using OCR
                            try:
                                image_pil = Image.open(io.BytesIO(img_data))
                                ocr_text = pytesseract.image_to_string(image_pil)
                                ocr_text = ocr_text.strip()
                            except:
                                ocr_text = ""
                            
                            content_chunks.append({
                                'type': 'image',
                                'content': img_data,
                                'ocr_text': ocr_text,
                                'page': page_num + 1,
                                'file_name': pdf_file.name,
                                'file_index': file_index,
                                'image_id': f"file_{file_index}_page_{page_num + 1}_img_{img_index}",
                                'chunk_id': len(content_chunks)
                            })
                        pix = None
                    except Exception as e:
                        print(f"Error extracting image: {str(e)}")
                        continue
            
            doc.close()
            return content_chunks
            
        except Exception as e:
            st.error(f"Error reading PDF {pdf_file.name}: {str(e)}")
            # Fallback to text-only extraction
            return self.extract_text_only_fallback(pdf_file, file_index)
    
    def extract_content_from_docx(self, docx_file, file_index: int = 0) -> List[Dict]:
        """Extract content from DOCX file"""
        try:
            docx_file.seek(0)
            doc = DocxDocument(docx_file)
            content_chunks = []
            
            for para_num, paragraph in enumerate(doc.paragraphs, 1):
                if paragraph.text.strip():
                    content_chunks.append({
                        'type': 'text',
                        'content': paragraph.text,
                        'page': para_num,  # Using paragraph number as reference
                        'file_name': docx_file.name,
                        'file_index': file_index,
                        'chunk_id': len(content_chunks)
                    })
            
            return content_chunks
            
        except Exception as e:
            st.error(f"Error reading DOCX {docx_file.name}: {str(e)}")
            return []
    
    def extract_content_from_txt(self, txt_file, file_index: int = 0) -> List[Dict]:
        """Extract content from TXT file"""
        try:
            txt_file.seek(0)
            content = txt_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            lines = content.split('\n')
            content_chunks = []
            
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    content_chunks.append({
                        'type': 'text',
                        'content': line,
                        'page': line_num,  # Using line number as reference
                        'file_name': txt_file.name,
                        'file_index': file_index,
                        'chunk_id': len(content_chunks)
                    })
            
            return content_chunks
            
        except Exception as e:
            st.error(f"Error reading TXT {txt_file.name}: {str(e)}")
            return []
    
    def extract_content_from_markdown(self, md_file, file_index: int = 0) -> List[Dict]:
        """Extract content from Markdown file"""
        try:
            md_file.seek(0)
            content = md_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Split by headers and sections
            sections = re.split(r'\n#+\s+', content)
            content_chunks = []
            
            for section_num, section in enumerate(sections, 1):
                if section.strip():
                    content_chunks.append({
                        'type': 'text',
                        'content': section,
                        'page': section_num,  # Using section number as reference
                        'file_name': md_file.name,
                        'file_index': file_index,
                        'chunk_id': len(content_chunks)
                    })
            
            return content_chunks
            
        except Exception as e:
            st.error(f"Error reading Markdown {md_file.name}: {str(e)}")
            return []
    
    def extract_text_only_fallback(self, pdf_file, file_index: int = 0) -> List[Dict]:
        """Fallback to text-only extraction using PyPDF2"""
        try:
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            content_chunks = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    content_chunks.append({
                        'type': 'text',
                        'content': page_text,
                        'page': page_num,
                        'file_name': pdf_file.name,
                        'file_index': file_index,
                        'chunk_id': len(content_chunks)
                    })
            
            return content_chunks
        except Exception as e:
            st.error(f"Error with fallback text extraction for {pdf_file.name}: {str(e)}")
            return []
    
    def chunk_content(self, content_chunks: List[Dict]) -> List[Dict]:
        """Split content into overlapping chunks with file information"""
        final_chunks = []
        
        for content in content_chunks:
            if content['type'] == 'text':
                # Chunk text content
                words = content['content'].split()
                for i in range(0, len(words), Config.CHUNK_SIZE - Config.OVERLAP):
                    chunk_words = words[i:i + Config.CHUNK_SIZE]
                    chunk_text = " ".join(chunk_words)
                    
                    final_chunks.append({
                        'text': chunk_text,
                        'type': 'text',
                        'page': content['page'],
                        'file_name': content['file_name'],
                        'file_index': content['file_index'],
                        'chunk_id': len(final_chunks)
                    })
            
            elif content['type'] == 'image':
                # For images, include OCR text if available
                image_text = f"[IMAGE from {content['file_name']} on page {content['page']}]"
                if content.get('ocr_text'):
                    image_text += f" Text found in image: {content['ocr_text']}"
                
                final_chunks.append({
                    'text': image_text,
                    'type': 'image',
                    'page': content['page'],
                    'file_name': content['file_name'],
                    'file_index': content['file_index'],
                    'image_data': content['content'],
                    'image_id': content['image_id'],
                    'ocr_text': content.get('ocr_text', ''),
                    'chunk_id': len(final_chunks)
                })
        
        return final_chunks
    
    def create_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """Create embeddings for text chunks"""
        model = self.get_embedding_model()
        texts = [chunk['text'] for chunk in chunks]
        return model.encode(texts)
    
    def find_relevant_chunks(self, query: str, chunks: List[Dict], embeddings: np.ndarray) -> List[Dict]:
        """Find most relevant chunks for a query"""
        model = self.get_embedding_model()
        query_embedding = model.encode([query])
        similarities = cosine_similarity(query_embedding, embeddings)[0]
    
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[-Config.TOP_K_CHUNKS:][::-1]
    
        relevant_chunks = []
        for idx in top_indices:
            if similarities[idx] > Config.SIMILARITY_THRESHOLD:
                chunk = chunks[idx].copy()
                chunk['similarity'] = similarities[idx]
                relevant_chunks.append(chunk)
        
        return relevant_chunks
    
    def process_single_document(self, uploaded_file, file_index: int = 0) -> List[Dict]:
        """Process a single document and return content chunks"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return self.extract_content_from_pdf(uploaded_file, file_index)
        elif file_extension == 'docx':
            return self.extract_content_from_docx(uploaded_file, file_index)
        elif file_extension == 'txt':
            return self.extract_content_from_txt(uploaded_file, file_index)
        elif file_extension in ['md', 'markdown']:
            return self.extract_content_from_markdown(uploaded_file, file_index)
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return []
    
    def process_document(self, uploaded_files):
        """Process single or multiple documents"""
        try:
            # Handle both single file and multiple files
            if not isinstance(uploaded_files, list):
                uploaded_files = [uploaded_files]
            
            all_content_chunks = []
            processed_files = []
            
            # Process each file
            for file_index, uploaded_file in enumerate(uploaded_files):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    content_chunks = self.process_single_document(uploaded_file, file_index)
                    if content_chunks:
                        all_content_chunks.extend(content_chunks)
                        processed_files.append(uploaded_file.name)
                    else:
                        st.warning(f"Could not process {uploaded_file.name}")
            
            if not all_content_chunks:
                st.error("No content could be extracted from the uploaded files.")
                return None
            
            # Create searchable chunks
            final_chunks = self.chunk_content(all_content_chunks)
            
            # Create embeddings
            embeddings = self.create_embeddings(final_chunks)
            
            # Determine combined filename
            if len(processed_files) == 1:
                combined_name = processed_files[0]
            else:
                combined_name = f"{len(processed_files)} files: {', '.join(processed_files[:2])}" + \
                              (f" and {len(processed_files) - 2} more" if len(processed_files) > 2 else "")
            
            return {
                'chunks': final_chunks,
                'embeddings': embeddings,
                'filename': combined_name,
                'file_list': processed_files,
                'file_count': len(processed_files),
                'has_images': any(chunk['type'] == 'image' for chunk in final_chunks)
            }
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")
            return None