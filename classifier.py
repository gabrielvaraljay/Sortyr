"""
Classifier module for Sortyr application
"""

import re
from typing import Dict, List, Optional
from datetime import datetime

def extract_date_from_text(text: str) -> Optional[str]:
    """Extract date from text using various patterns."""
    if not text:
        return None
        
    # Define date patterns (in order of preference)
    patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',       # 22/05/2026
        r'\b(\d{1,2}-\d{1,2}-\d{4})\b',       # 22-05-2026
        r'\b(\d{4}-\d{1,2}-\d{1,2})\b',       # 2026-05-22
        r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',  # 22 May 2026
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'  # May 22, 2026
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            date_str = matches[0]
            try:
                # Parse different date formats
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                elif '-' in date_str:
                    if len(date_str.split('-')[0]) == 4:  # YYYY-MM-DD
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:  # DD-MM-YYYY
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                else:  # Month DD, YYYY or DD Month YYYY
                    if ',' in date_str:
                        date_obj = datetime.strptime(date_str, '%B %d, %Y')
                    else:
                        date_obj = datetime.strptime(date_str, '%d %B %Y')
                
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    return None

def classify_document(text: str, categories: Dict[str, List[str]]) -> str:
    """Classify document based on keywords."""
    if not text:
        return "Unknown"
        
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Count matches per category
    scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += 1
        scores[category] = score
    
    # Find the highest scoring category
    max_score = max(scores.values())
    
    # If no matches or only one match at max score, return Unknown
    if max_score == 0:
        return "Unknown"
    
    # Get all categories with maximum score
    best_categories = [cat for cat, score in scores.items() if score == max_score]
    
    # If there's a tie, use the first category found (maintaining order)
    return best_categories[0]

def find_first_meaningful_phrase(text: str, max_words: int = 4) -> str:
    """Extract the first meaningful phrase from text for filename generation."""
    if not text:
        return "document"
    
    # Clean up whitespace and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # If we have more than max_words, take the first part
    if len(words) > max_words:
        words = words[:max_words]
    
    # Join the words with hyphens and title-case
    phrase = '-'.join(words).title()
    
    # Make sure it's not empty
    return phrase if phrase else "document"