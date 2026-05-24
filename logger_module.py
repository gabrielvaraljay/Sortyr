"""
Logger module for Sortyr application
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

def setup_logger(log_dir: str = "./logs"):
    """Setup log directory and return logger function."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    def log(message: str, level: str = "INFO", **kwargs):
        """Log message to JSON file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        
        log_file = os.path.join(log_dir, "sortyr.log")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    return log

def log_processing_start(log_func):
    """Log start of processing."""
    log_func("Processing started", level="INFO")

def log_processing_complete(log_func):
    """Log completion of processing."""
    log_func("Processing completed successfully", level="INFO")

def log_file_processed(log_func, file_path: str, category: str, filename: str):
    """Log successful file processing."""
    log_func("File processed successfully", level="INFO", 
             file_path=file_path, category=category, new_filename=filename)

def log_file_error(log_func, file_path: str, error: str):
    """Log error processing file."""
    log_func("Error processing file", level="ERROR", file_path=file_path, error=error)