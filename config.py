"""
Configuration module for Sortyr application.
Settings persist in ~/Library/Application Support/Sortyr/config.json
so they survive app updates.
"""

import json
import os
from typing import Dict, Any

# Stable config location outside the app bundle
CONFIG_DIR = os.path.expanduser("~/Library/Application Support/Sortyr")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "input_folder": "",
    "output_folder": "",
    "archive_originals": True,
    "max_image_width": 1200,
    "jpeg_quality": 85,
}


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from stable location."""
    path = config_path or CONFIG_PATH
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                saved = json.load(f)
            # Merge with defaults (new keys get default values)
            merged = {**DEFAULT_CONFIG, **saved}
            return merged
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)


def save_config(config: Dict[str, Any], config_path: str = None):
    """Save configuration to stable location."""
    path = config_path or CONFIG_PATH
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: could not save config: {e}")
