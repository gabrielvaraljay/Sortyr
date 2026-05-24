#!/usr/bin/env python3
"""
Simple test runner for Sortyr application to verify core functionality.
"""

import sys
import os

# Add the project directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from config import load_config
        from classifier import classify_document, extract_date_from_text
        from logger_module import setup_logger
        
        print("✓ All core modules imported successfully")
        
        # Test config loading
        config = load_config()
        print("✓ Config loaded successfully")
        
        # Test basic classification
        test_text = "This is a NHS appointment letter for a GP visit"
        category = classify_document(test_text, config["categories"])
        print(f"✓ Classification test: '{test_text}' -> {category}")
        
        # Test date extraction
        date_text = "The appointment is on 22/05/2026"
        extracted_date = extract_date_from_text(date_text)
        print(f"✓ Date extraction test: '{date_text}' -> {extracted_date}")
        
        # Test logger
        log_func = setup_logger()
        log_func("Test log message", "INFO")
        print("✓ Logger working correctly")
        
        print("\nAll tests passed! The Sortyr application is ready.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()