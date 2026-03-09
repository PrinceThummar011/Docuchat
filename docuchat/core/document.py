"""Document text extraction for PDF, DOCX, and TXT files."""

import os

import PyPDF2
import docx


def extract_text_from_file(file_path: str, filename: str) -> str:
    """
    Extract plain text from a file based on its extension.

    Args:
        file_path: Absolute path to the saved file on disk.
        filename:  Original filename (used to determine file type).

    Returns:
        Extracted text string, or an error message on failure.
    """
    try:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return _extract_pdf(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            return _extract_docx(file_path)
        return f"Unsupported file type: '{ext}'"
    except Exception as e:
        return f"Error reading file: {e}"


def _extract_pdf(file_path: str) -> str:
    """Extract text from a PDF file page by page."""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()
    except Exception as e:
        return f"Error reading PDF: {e}"


def _extract_docx(file_path: str) -> str:
    """Extract text from a DOCX file paragraph by paragraph."""
    try:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"
