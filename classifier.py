"""
Classifier module for Sortyr application.
Smart classification: extracts vendor/organisation name from document text.
No predefined keyword lists needed - the document content IS the category.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime

# Known organisation patterns - maps variations to clean folder names
# Users can add to this, but it works without it too
KNOWN_ORGS = {
    'nhs': 'NHS',
    'national health service': 'NHS',
    'hmrc': 'HMRC',
    'hm revenue': 'HMRC',
    'metropolitan police': 'Police',
    'met police': 'Police',
    'dvla': 'DVLA',
    'home office': 'Home-Office',
    'amazon': 'Amazon',
    'godaddy': 'GoDaddy',
    'google': 'Google',
    'apple': 'Apple',
    'adobe': 'Adobe',
    'github': 'GitHub',
    'aws': 'AWS',
    'amazon web services': 'AWS',
    'tesla': 'Tesla',
    'monzo': 'Monzo',
    'starling': 'Starling',
    'wise': 'Wise',
    'transferwise': 'Wise',
    'barclays': 'Barclays',
    'hsbc': 'HSBC',
    'lloyds': 'Lloyds',
    'natwest': 'NatWest',
    'council tax': 'Council-Tax',
    'hetzner': 'Hetzner',
    'cloudflare': 'Cloudflare',
    'fly.io': 'Fly-io',
    'vodafone': 'Vodafone',
    'ee': 'EE',
    'bt': 'BT',
    'sky': 'Sky',
    'virgin media': 'Virgin-Media',
    'ofsted': 'Ofsted',
}


def extract_organisation(text: str) -> str:
    """
    Extract the primary organisation/vendor from document text.
    Checks known orgs first, then tries to find the most prominent entity.
    Returns a filesystem-safe folder name.
    """
    if not text:
        return "Unknown"

    text_lower = text.lower()

    # 1. Check known organisations (longest match first to avoid partial matches)
    sorted_orgs = sorted(KNOWN_ORGS.keys(), key=len, reverse=True)
    for org_key in sorted_orgs:
        if org_key in text_lower:
            return KNOWN_ORGS[org_key]

    # 2. Try to extract from common document patterns
    # "From: Company Name" or "Company Name Ltd/Inc/LLC"
    patterns = [
        r'(?:from|sender|issued by|billed by)[:\s]+([A-Z][A-Za-z0-9\s&]{2,30})',
        r'([A-Z][A-Za-z0-9\s&]{2,25})\s+(?:Ltd|Limited|Inc|LLC|PLC|plc|LLP)',
        r'([A-Z][A-Za-z0-9\s&]{2,25})\s+(?:Invoice|Receipt|Statement|Bill)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            # Clean up and make filesystem-safe
            name = re.sub(r'[^A-Za-z0-9\s-]', '', name).strip()
            if len(name) > 2:
                return name.replace(' ', '-')

    # 3. Fallback: first prominent capitalised phrase (likely header/letterhead)
    lines = text.strip().split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if len(line) > 2 and len(line) < 40:
            # If line is mostly uppercase or title case, likely an org name
            words = line.split()
            if len(words) <= 5 and any(w[0].isupper() for w in words if w):
                clean = re.sub(r'[^A-Za-z0-9\s-]', '', line).strip()
                if len(clean) > 2:
                    return clean.replace(' ', '-')

    return "Unknown"


def extract_date_from_text(text: str) -> Optional[str]:
    """Extract date from text using various patterns."""
    if not text:
        return None

    patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
        r'\b(\d{1,2}-\d{1,2}-\d{4})\b',
        r'\b(\d{4}-\d{1,2}-\d{1,2})\b',
        r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',
        r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            date_str = matches[0]
            try:
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                elif '-' in date_str:
                    if len(date_str.split('-')[0]) == 4:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                else:
                    if ',' in date_str:
                        date_obj = datetime.strptime(date_str.replace(',', ''), '%B %d %Y')
                    else:
                        date_obj = datetime.strptime(date_str, '%d %B %Y')
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue

    return None


def classify_document(text: str, categories: Dict[str, List[str]] = None) -> str:
    """
    Classify document. Uses smart org extraction.
    categories param kept for backward compatibility but no longer required.
    """
    return extract_organisation(text)


def find_first_meaningful_phrase(text: str, max_words: int = 4) -> str:
    """Extract the first meaningful phrase from text for filename generation."""
    if not text:
        return "document"

    words = re.findall(r'\b\w+\b', text.lower())
    if len(words) > max_words:
        words = words[:max_words]

    phrase = '-'.join(words).title()
    return phrase if phrase else "document"
