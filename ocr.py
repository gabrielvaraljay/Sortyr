"""
OCR module for Sortyr - macOS Vision framework with pytesseract fallback
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

try:
    from Foundation import NSURL
    from Vision import VNImageRequestHandler, VNRecognizeTextRequest
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

try:
    import pytesseract
    from PIL import Image
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False


def extract_text_with_vision(image_path: str) -> Optional[str]:
    """Extract text using macOS Vision framework (Apple Silicon native)."""
    if not HAS_VISION:
        return None

    try:
        url = NSURL.fileURLWithPath_(image_path)
        request = VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLevel_(0)  # 0 = accurate, 1 = fast
        request.setUsesLanguageCorrection_(True)

        handler = VNImageRequestHandler.alloc().initWithURL_options_(url, None)
        success, error = handler.performRequests_error_([request], None)

        if not success or error:
            logger.error(f"Vision OCR request failed: {error}")
            return None

        results = request.results()
        if not results:
            return None

        # Collect text from all recognized text observations
        lines = []
        for observation in results:
            candidates = observation.topCandidates_(1)
            if candidates:
                lines.append(candidates[0].string())

        return "\n".join(lines) if lines else None

    except Exception as e:
        logger.error(f"Vision OCR failed: {e}")
        return None


def extract_text_with_tesseract(image_path: str) -> Optional[str]:
    """Extract text using pytesseract (fallback)."""
    if not HAS_PYTESSERACT:
        return None

    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        return None


def extract_text_from_image(image_path: str) -> Optional[str]:
    """Extract text from image using best available OCR method."""
    if HAS_VISION:
        text = extract_text_with_vision(image_path)
        if text:
            return text

    if HAS_PYTESSERACT:
        return extract_text_with_tesseract(image_path)

    logger.warning("No OCR backend available (install pyobjc-framework-Vision or pytesseract)")
    return None


def extract_text_from_pdf(pdf_path: str, max_pages: int = 3) -> Optional[str]:
    """Extract text from PDF file using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""

        for page_num in range(min(max_pages, len(doc))):
            page = doc.load_page(page_num)
            text += page.get_text()

        doc.close()
        return text.strip() if text.strip() else None
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return None


def extract_text_from_file(file_path: str) -> Optional[str]:
    """Extract text from a file (PDF or image)."""
    try:
        if file_path.lower().endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        return extract_text_from_image(file_path)
    except Exception as e:
        logger.error(f"Text extraction failed for {file_path}: {e}")
        return None
