"""
Configuration module for Sortyr application
"""

import json
import os
from typing import Dict, Any

def load_config(config_path: str = "./config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default config if file doesn't exist
            return {
                "categories": {
                    "NHS": ["NHS", "hospital", "appointment", "GP", "clinic", "prescription"],
                    "HMRC": ["HMRC", "tax", "self assessment", "PAYE", "national insurance"],
                    "Bank": ["bank", "statement", "transaction", "account", "Monzo", "Barclays"],
                    "Invoices": ["invoice", "receipt", "payment", "order", "Amazon"],
                    "Insurance": ["insurance", "policy", "claim", "premium"],
                    "Utilities": ["electricity", "gas", "water", "broadband", "council tax"],
                    "School": ["school", "nursery", "Ofsted", "term dates"],
                    "Legal": ["solicitor", "court", "contract", "agreement"],
                    "Personal": ["passport", "driving licence", "birth certificate"]
                },
                "input_folder": "./input",
                "output_folder": "./processed",
                "archive_originals": True,
                "max_image_width": 1200,
                "jpeg_quality": 85
            }
    except Exception as e:
        raise Exception(f"Failed to load config: {str(e)}")

def save_config(config: Dict[str, Any], config_path: str = "./config.json"):
    """Save configuration to JSON file."""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save config: {str(e)}")