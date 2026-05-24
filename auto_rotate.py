"""
Auto-rotate images based on OCR confidence.
Tries all 4 rotations, picks the one with best OCR text output.
Uses macOS Vision framework.
"""

import os
from typing import Optional
from PIL import Image

try:
    from Foundation import NSURL
    from Vision import VNImageRequestHandler, VNRecognizeTextRequest
    HAS_VISION = True
except ImportError:
    HAS_VISION = False


def ocr_confidence(image_path: str) -> float:
    """Run OCR and return total confidence score (sum of all observation confidences)."""
    if not HAS_VISION:
        return 0.0

    try:
        url = NSURL.fileURLWithPath_(image_path)
        request = VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLevel_(1)  # Fast mode for rotation detection
        request.setUsesLanguageCorrection_(False)

        handler = VNImageRequestHandler.alloc().initWithURL_options_(url, None)
        success, error = handler.performRequests_error_([request], None)

        if not success or not request.results():
            return 0.0

        total_confidence = 0.0
        total_chars = 0
        for obs in request.results():
            candidates = obs.topCandidates_(1)
            if candidates:
                conf = candidates[0].confidence()
                text_len = len(candidates[0].string())
                total_confidence += conf * text_len
                total_chars += text_len

        return total_confidence

    except Exception:
        return 0.0


def auto_rotate_image(image_path: str) -> str:
    """
    Try 0, 90, 180, 270 degree rotations. Keep the one with best OCR confidence.
    Overwrites the original file if rotation needed.
    Returns the path (same file, possibly rotated).
    """
    if not HAS_VISION:
        return image_path

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.tiff', '.webp'):
        return image_path

    # Test original first
    best_score = ocr_confidence(image_path)
    best_rotation = 0

    # Try 90, 180, 270
    tmp_path = image_path + '.rotate_tmp'
    for degrees in [90, 180, 270]:
        try:
            with Image.open(image_path) as img:
                rotated = img.rotate(-degrees, expand=True)
                rotated.save(tmp_path)

            score = ocr_confidence(tmp_path)
            if score > best_score:
                best_score = score
                best_rotation = degrees

        except Exception:
            continue

    # Clean up temp
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    # Apply best rotation if not 0
    if best_rotation != 0:
        try:
            with Image.open(image_path) as img:
                exif = img.info.get('exif')
                rotated = img.rotate(-best_rotation, expand=True)
                save_kwargs = {}
                if exif:
                    save_kwargs['exif'] = exif
                if ext in ('.jpg', '.jpeg'):
                    rotated.save(image_path, 'JPEG', quality=85, optimize=True, **save_kwargs)
                else:
                    rotated.save(image_path, optimize=True)
            print(f"  Auto-rotated {best_rotation} degrees (confidence: {best_score:.1f})")
        except Exception as e:
            print(f"  Warning: rotation failed: {e}")

    return image_path
