"""
Filename generator module for Sortyr application
"""

import os
import re
from typing import Optional
from datetime import datetime

def clean_filename_part(text: str) -> str:
    """Clean a text part to be used in filename."""
    # Remove invalid characters and replace spaces with hyphens  
    cleaned = re.sub(r'[^\w\-\.]', '-', text)
    # Replace multiple hyphens with single hyphen
    cleaned = re.sub(r'-+', '-', cleaned)
    # Remove leading/trailing hyphens
    cleaned = cleaned.strip('-')
    return cleaned

def generate_filename(category: str, date: str, description: str, extension: str) -> str:
    """Generate standardized filename."""
    # Clean the parts
    category_clean = clean_filename_part(category)
    description_clean = clean_filename_part(description)
    
    # Handle case where description is empty
    if not description_clean:
        description_clean = "document"
    
    # Format date (if unknown date, make it 'unknown-date')
    if date == "unknown-date":
        filename = f"{category_clean}-unknown-date-{description_clean}.{extension}"
    else:
        filename = f"{category_clean}-{date}-{description_clean}.{extension}"
        
    return filename

def ensure_unique_filename(filepath: str) -> str:
    """Ensure filename is unique by appending numbers if necessary."""
    if not os.path.exists(filepath):
        return filepath
    
    # If file exists, find a unique name
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    new_filepath = filepath
    while os.path.exists(new_filepath):
        new_name = f"{name}-{counter}{ext}"
        new_filepath = os.path.join(directory, new_name)
        counter += 1
    
    return new_filepath