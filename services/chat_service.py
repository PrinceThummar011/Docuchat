# chat_service.py - Enhanced Chat and AI response logic with multi-file support

from groq import Groq
from typing import List, Dict
import streamlit as st
from config import Config
import base64
import io
from collections import defaultdict

class ChatService:
    """Handle chat operations and AI responses with multi-file support"""
    
    def __init__(self):
        if Config.GROQ_API_KEY:
            self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        else:
            self.groq_client = None
    
    def is_image_related_query(self, query: str) -> bool:
        """Check if query is related to images"""
        image_keywords = [
            'image', 'picture', 'chart', 'graph', 'diagram', 'figure', 
            'photo', 'illustration', 'visual', 'drawing', 'map', 'table',
            'screenshot', 'logo', 'icon', 'what do you see', 'describe the'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in image_keywords)
    
    def is_multi_file_query(self, query: str) -> bool:
        """Check if query is asking about multiple files or comparisons"""
        multi_file_keywords = [
            'compare', 'difference', 'similar', 'contrast', 'both', 'all files', 
            'documents', 'which document', 'which file', 'across', 'between',
            'different files', 'each document', 'in common', 'varies'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in multi_file_keywords)
    
    def generate_answer(self, query: str, relevant_chunks: List[Dict]) -> str:
        """Generate answer using Groq with multi-file awareness"""
        
        # Check if this is a multi-file context
        files_in_chunks = set(chunk.get('file_name', 'Unknown') for chunk in relevant_chunks)
        is_multi_file_context = len(files_in_chunks) > 1
        
        if self.is_image_related_query(query):
            return self.handle_image_query_with_groq(query, relevant_chunks, is_multi_file_context)
        else:
            return self.handle_text_query(query, relevant_chunks, is_multi_file_context)
    
    def handle_image_query_with_groq(self, query: str, relevant_chunks: List[Dict], is_multi_file: bool = False) -> str:
        """Handle image queries using OCR text and Groq with multi-file support"""
        image_chunks = [chunk for chunk in relevant_chunks if chunk['type'] == 'image']
        text_chunks = [chunk for chunk in relevant_chunks if chunk['type'] == 'text']
        
        if not image_chunks:
            context_msg = "any of your documents" if is_multi_file else "the document"
            return f"I couldn't find any images in the relevant sections of {context_msg} that relate to your question."
        
        # Prepare context with OCR text from images, organized by file
        context = ""
        sources_by_file = defaultdict(set)
        
        # Group chunks by file for better organization
        if is_multi_file:
            files_with_images = defaultdict(list)
            for chunk in image_chunks:
                files_with_images[chunk.get('file_name', 'Unknown')].append(chunk)
            
            for file_name, file_chunks in files_with_images.items():
                context += f"\n=== Images from {file_name} ===\n"
                for chunk in file_chunks:
                    if chunk.get('ocr_text') and chunk['ocr_text'].strip():
                        context += f"[Text from image on page {chunk['page']}]: {chunk['ocr_text']}\n\n"
                    else:
                        context += f"[Image on page {chunk['page']} - no text extracted]\n\n"
                    sources_by_file[file_name].add(chunk['page'])
        else:
            # Single file context
            for chunk in image_chunks:
                if chunk.get('ocr_text') and chunk['ocr_text'].strip():
                    context += f"[Text from image on page {chunk['page']}]: {chunk['ocr_text']}\n\n"
                else:
                    context += f"[Image on page {chunk['page']} - no text extracted]\n\n"
                sources_by_file[chunk.get('file_name', 'Document')].add(chunk['page'])
        
        # Add surrounding text context
        for chunk in text_chunks:
            file_name = chunk.get('file_name', 'Unknown')
            context += f"[Text from {file_name} page {chunk['page']}]: {chunk['text']}\n\n"
            sources_by_file[file_name].add(chunk['page'])
        
        if not context.strip():
            return "I found images related to your query but cannot analyze their visual content. Only text extracted from images (if any) can be processed."
        
        # Enhanced prompt for multi-file context
        prompt = f"""Based on the following content extracted from {'multiple documents' if is_multi_file else 'a document'} (including text found in images), answer the user's question about images/visual content.

{'Multi-Document' if is_multi_file else 'Document'} Content:
{context}

User Question: {query}

Instructions:
- Focus on information that relates to images, charts, diagrams, or visual elements
- Use the text extracted from images to answer questions about their content
- If no relevant text was extracted from images, explain what limitations exist
- Be specific about which {'files and' if is_multi_file else ''} pages contain the visual elements
{'- When multiple files are involved, clearly distinguish between them' if is_multi_file else ''}

Answer:"""

        try:
            response = self.groq_client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1200
            )
            
            answer = response.choices[0].message.content
            
            # Add source references with file information
            if sources_by_file:
                answer += "\n\n🖼️ *Image sources:*\n"
                for file_name, pages in sources_by_file.items():
                    pages_list = sorted(list(pages))
                    if is_multi_file:
                        answer += f"• **{file_name}**: pages {', '.join(map(str, pages_list))}\n"
                    else:
                        answer += f"• Pages {', '.join(map(str, pages_list))}\n"
            
            return answer
            
        except Exception as e:
            return f"Error processing image-related query: {str(e)}"
    
    def handle_text_query(self, query: str, relevant_chunks: List[Dict], is_multi_file: bool = False) -> str:
        """Handle regular text queries using Groq with multi-file support"""
        if not self.groq_client:
            return "⚠️ Groq API key not configured. Please add your API key to continue."
        
        try:
            # Prepare context from relevant chunks, organized by file
            context = ""
            sources_by_file = defaultdict(set)
            
            if is_multi_file:
                # Group by file for multi-file queries
                files_with_content = defaultdict(list)
                for chunk in relevant_chunks:
                    files_with_content[chunk.get('file_name', 'Unknown')].append(chunk)
                
                for file_name, file_chunks in files_with_content.items():
                    context += f"\n=== Content from {file_name} ===\n"
                    for chunk in file_chunks:
                        if chunk['type'] == 'text':
                            context += f"[Page {chunk['page']}]: {chunk['text']}\n\n"
                        elif chunk['type'] == 'image' and chunk.get('ocr_text'):
                            context += f"[Image text on page {chunk['page']}]: {chunk['ocr_text']}\n\n"
                        sources_by_file[file_name].add(chunk['page'])
            else:
                # Single file context
                for chunk in relevant_chunks:
                    if chunk['type'] == 'text':
                        context += f"[Page {chunk['page']}]: {chunk['text']}\n\n"
                    elif chunk['type'] == 'image' and chunk.get('ocr_text'):
                        context += f"[Image text on page {chunk['page']}]: {chunk['ocr_text']}\n\n"
                    sources_by_file[chunk.get('file_name', 'Document')].add(chunk['page'])
            
            # Enhanced prompt for multi-file awareness
            is_comparison_query = self.is_multi_file_query(query)
            
            prompt = f"""Based on the following content from {'multiple documents' if is_multi_file else 'a document'}, answer the user's question accurately and concisely.

{'Multi-Document' if is_multi_file else 'Document'} Content:
{context}

User Question: {query}

Instructions:
- Only use information from the provided document content
- If the answer cannot be found in the {'documents' if is_multi_file else 'document'}, say so clearly
- Be specific and accurate
- Keep the answer concise but complete
{'- When comparing or contrasting information, clearly distinguish between different files' if is_multi_file and is_comparison_query else ''}
{'- If information varies between documents, highlight the differences' if is_multi_file else ''}
{'- Organize your response by document when relevant' if is_multi_file else ''}

Answer:"""

            response = self.groq_client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1200
            )
            
            answer = response.choices[0].message.content
            
            # Add source references with file information
            if sources_by_file and "I could not find" not in answer.lower():
                answer += "\n\n📄 *Sources:*\n"
                for file_name, pages in sources_by_file.items():
                    pages_list = sorted(list(pages))
                    if is_multi_file:
                        answer += f"• **{file_name}**: pages {', '.join(map(str, pages_list))}\n"
                    else:
                        answer += f"• Pages {', '.join(map(str, pages_list))}\n"
            
            return answer
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def get_suggested_questions(self, chunks: List[Dict]) -> List[str]:
        """Generate suggested questions based on document content with multi-file awareness"""
        if not chunks:
            return []
        
        # Check if this is a multi-file context
        files_in_chunks = set(chunk.get('file_name', 'Unknown') for chunk in chunks)
        is_multi_file = len(files_in_chunks) > 1
        
        # Check content characteristics
        has_images = any(chunk['type'] == 'image' for chunk in chunks)
        has_ocr_text = any(chunk.get('ocr_text', '').strip() for chunk in chunks if chunk['type'] == 'image')
        
        # Sample text from documents
        text_chunks = [chunk for chunk in chunks if chunk['type'] == 'text']
        sample_text = " ".join([chunk['text'][:200] for chunk in text_chunks[:5]])
        text_lower = sample_text.lower()
        
        # Generate suggestions based on context
        if is_multi_file:
            suggestions = [
                "Compare the main topics across all documents",
                "What information is common between the files?",
                "Which document contains the most relevant information?"
            ]
            
            # Add multi-file specific suggestions
            if 'price' in text_lower or 'cost' in text_lower or '$' in sample_text:
                suggestions.append("Compare pricing information across documents")
            elif 'date' in text_lower or 'deadline' in text_lower:
                suggestions.append("What are the key dates in each document?")
            elif 'requirement' in text_lower or 'must' in text_lower:
                suggestions.append("How do the requirements differ between documents?")
            else:
                suggestions.append("What are the key differences between the documents?")
        else:
            # Single file suggestions
            suggestions = [
                "What is the main topic of this document?",
                "Can you summarize the key points?"
            ]
            
            # Content-specific suggestions
            if 'price' in text_lower or 'cost' in text_lower or '$' in sample_text:
                suggestions.append("What are the costs mentioned?")
            elif 'date' in text_lower or 'deadline' in text_lower:
                suggestions.append("What are the important dates?")
            elif 'requirement' in text_lower or 'must' in text_lower:
                suggestions.append("What are the key requirements?")
            else:
                suggestions.append("What are the important details?")
        
        # Add image-related suggestion
        if has_images:
            if has_ocr_text:
                suggestions.append("What text is visible in the images?")
            else:
                suggestions.append("What pages contain images?")
        
        return suggestions[:4]  # Return up to 4 suggestions