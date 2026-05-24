"""
PDF processor module for Sortyr application
"""

import os
from typing import Optional
from ocr import extract_text_from_file

def extract_text_from_pdf(pdf_path: str, max_pages: int = 3) -> Optional[str]:
    """Extract text from PDF file with OCR fallback for scanned documents."""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        text = ""
        
        # Extract text from first few pages
        for page_num in range(min(max_pages, len(doc))):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text
            
        doc.close()
        
        # If no text found, try OCR
        if not text.strip():
            # Try OCR on first page as fallback
            return extract_text_from_file(pdf_path)
            
        return text.strip() if text.strip() else None
    except Exception as e:
        print(f"PDF text extraction failed: {str(e)}")
        return None