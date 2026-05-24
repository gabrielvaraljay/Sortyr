"""
File mover module for Sortyr application
"""

import os
import shutil
from typing import Optional
from renamer import generate_filename, ensure_unique_filename

def move_file(file_path: str, category: str, date: str, description: str, 
              output_folder: str, archive_originals: bool = True) -> Optional[str]:
    """Move file to appropriate category folder with standardized filename."""
    try:
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        
        # Generate new filename
        new_filename = generate_filename(category, date, description, ext[1:])
        
        # Create category directory if it doesn't exist
        category_folder = os.path.join(output_folder, category)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
        
        # Check for uniqueness and get final filepath
        final_filepath = os.path.join(category_folder, new_filename)
        final_filepath = ensure_unique_filename(final_filepath)
        
        # Move the file
        shutil.move(file_path, final_filepath)
        
        # Archive original if requested
        if archive_originals:
            archive_folder = os.path.join(os.path.dirname(output_folder), "archive_originals")
            if not os.path.exists(archive_folder):
                os.makedirs(archive_folder)
            
            # Get a unique archive path (this handles duplicate filenames)
            archive_path = os.path.join(archive_folder, os.path.basename(file_path))
            counter = 1
            while os.path.exists(archive_path):
                name, ext = os.path.splitext(os.path.basename(file_path))
                archive_path = os.path.join(archive_folder, f"{name}-{counter}{ext}")
                counter += 1
            
            shutil.copy(file_path, archive_path)  # Copy original to archive
        
        return final_filepath
    except Exception as e:
        print(f"Error moving file {file_path}: {str(e)}")
        return None