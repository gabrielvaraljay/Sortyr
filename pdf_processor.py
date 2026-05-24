"""
PDF processor module for Sortyr application.
Handles text extraction with proper OCR fallback for scanned/image PDFs.
"""

import os
import tempfile
from typing import Optional


def extract_text_from_pdf(pdf_path: str, max_pages: int = 3) -> Optional[str]:
    """Extract text from PDF. Falls back to rendering pages as images + Vision OCR."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        text = ""

        # First try native text extraction
        for page_num in range(min(max_pages, len(doc))):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text

        # If we got meaningful text, return it
        if text.strip() and len(text.strip()) > 20:
            doc.close()
            return text.strip()

        # Fallback: render pages as images and OCR them
        from ocr import extract_text_from_image

        ocr_text = ""
        tmp_dir = tempfile.mkdtemp(prefix="sortyr_ocr_")

        try:
            for page_num in range(min(max_pages, len(doc))):
                page = doc.load_page(page_num)
                # Render at 300 DPI for good OCR quality
                pix = page.get_pixmap(dpi=300)
                img_path = os.path.join(tmp_dir, f"page_{page_num}.png")
                pix.save(img_path)

                page_text = extract_text_from_image(img_path)
                if page_text:
                    ocr_text += page_text + "\n"

                # Clean up temp image
                os.remove(img_path)
        finally:
            try:
                os.rmdir(tmp_dir)
            except OSError:
                pass

        doc.close()
        return ocr_text.strip() if ocr_text.strip() else None

    except Exception as e:
        print(f"PDF text extraction failed: {str(e)}")
        return None
