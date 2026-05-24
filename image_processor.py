"""
Image processor module for Sortyr application
"""

import os
from PIL import Image
from typing import Optional, List

MAX_WIDTH = 1000  # Mobile photos resized to this, aspect ratio preserved


def resize_image(image_path: str, max_width: int = MAX_WIDTH, quality: int = 85) -> Optional[str]:
    """Resize image to max width while maintaining aspect ratio. Overwrites original."""
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            if original_width <= max_width:
                return image_path

            new_height = int((max_width / original_width) * original_height)
            resized_img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Preserve EXIF if present
            exif = img.info.get('exif')
            save_kwargs = {'quality': quality, 'optimize': True}
            if exif:
                save_kwargs['exif'] = exif

            # Overwrite original (no _resized suffix - cleaner)
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                resized_img.save(image_path, 'JPEG', **save_kwargs)
            else:
                resized_img.save(image_path, optimize=True)

            print(f"  Resized {original_width}x{original_height} -> {max_width}x{new_height}")
            return image_path

    except Exception as e:
        print(f"Error resizing image {image_path}: {str(e)}")
        return None


def merge_images_to_pdf(image_paths: List[str], output_pdf: str, max_width: int = MAX_WIDTH, quality: int = 85) -> Optional[str]:
    """
    Merge multiple images into a single PDF. For multi-page documents
    photographed with a mobile phone (e.g., subfolder of pages).
    
    Images are resized to max_width, then combined into one PDF in order.
    
    Args:
        image_paths: List of image file paths (sorted by name)
        output_pdf: Output PDF path
        max_width: Max pixel width per page
        quality: JPEG quality for embedded images
    
    Returns:
        Output PDF path on success, None on failure
    """
    if not image_paths:
        return None

    try:
        pages = []
        for img_path in sorted(image_paths):
            img = Image.open(img_path)

            # Resize if needed
            w, h = img.size
            if w > max_width:
                ratio = max_width / w
                new_h = int(h * ratio)
                img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)

            # Convert to RGB (PDF doesn't support RGBA)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            pages.append(img)

        if not pages:
            return None

        # Save first page, append rest
        first_page = pages[0]
        rest = pages[1:] if len(pages) > 1 else []

        first_page.save(
            output_pdf, 'PDF', resolution=150,
            save_all=True, append_images=rest
        )

        # Close all images
        for p in pages:
            p.close()

        print(f"  Merged {len(pages)} images -> {os.path.basename(output_pdf)}")
        return output_pdf

    except Exception as e:
        print(f"Error merging images to PDF: {str(e)}")
        return None
