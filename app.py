"""
Main application for Sortyr
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from threading import Thread
import time

# Add the current directory to Python path so modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import load_config, save_config
from logger_module import setup_logger, log_processing_start, log_processing_complete, log_file_processed, log_file_error
from ocr import extract_text_from_file
from classifier import classify_document, extract_date_from_text, find_first_meaningful_phrase
from image_processor import resize_image, merge_images_to_pdf
from pdf_processor import extract_text_from_pdf
from file_mover import move_file
from renamer import generate_filename, ensure_unique_filename

IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'tiff'}

class SortyrApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sortyr")
        self.root.geometry("800x600")
        
        # Load configuration
        self.config = load_config()
        
        # Setup logger
        self.log_func = setup_logger()
        
        # Create UI elements
        self.create_widgets()
        
        # Status tracking
        self.is_processing = False
        
    def create_widgets(self):
        # Input folder selection
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W)
        self.input_folder_var = tk.StringVar()
        self.input_folder_entry = ttk.Entry(input_frame, textvariable=self.input_folder_var, width=50)
        self.input_folder_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_input_folder).grid(row=0, column=2, padx=5)
        
        # Output folder selection
        output_frame = ttk.Frame(self.root, padding="10")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W)
        self.output_folder_var = tk.StringVar()
        self.output_folder_entry = ttk.Entry(output_frame, textvariable=self.output_folder_var, width=50)
        self.output_folder_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(row=0, column=2, padx=5)
        
        # Process button
        process_frame = ttk.Frame(self.root, padding="10")
        process_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.process_button = tk.Button(process_frame, text="▶  Process Documents", command=self.start_processing,
                                        bg="#6c5ce7", fg="white", activebackground="#5a4bd1", activeforeground="white",
                                        font=("Helvetica", 14, "bold"), padx=20, pady=10, relief="flat", cursor="hand2")
        self.process_button.grid(row=0, column=0, pady=10)
        
        # Status label
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Idle")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0)
        
        # Log display
        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)
        input_frame.columnconfigure(1, weight=1)
        output_frame.columnconfigure(1, weight=1)
        
    def browse_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder_var.set(folder)
            
    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder_var.set(folder)
    
    def update_status(self, status):
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def log_message(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_processing(self):
        if self.is_processing:
            return
            
        # Get folder paths
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        
        if not input_folder or not output_folder:
            self.log_message("Please select both input and output folders")
            return
            
        # Start processing in a separate thread
        self.is_processing = True
        self.process_button.config(state="disabled", text="⏳  Processing...", bg="#636e72")
        self.update_status("Processing...")
        thread = Thread(target=self.process_documents, args=(input_folder, output_folder))
        thread.daemon = True
        thread.start()
        
    def process_documents(self, input_folder, output_folder):
        """Process all documents in the input folder."""
        try:
            log_processing_start(self.log_func)
            
            # Create necessary directories
            processed_dir = os.path.join(output_folder, "processed")
            archive_dir = os.path.join(output_folder, "archive_originals")
            logs_dir = os.path.join(output_folder, "logs")
            
            for directory in [processed_dir, archive_dir, logs_dir]:
                if not os.path.exists(directory):
                    os.makedirs(directory)
            
            # Pre-process: merge subfolders of images into PDFs
            # (multi-page documents photographed with mobile)
            for entry in os.listdir(input_folder):
                subfolder = os.path.join(input_folder, entry)
                if os.path.isdir(subfolder):
                    images = sorted([
                        os.path.join(subfolder, f) for f in os.listdir(subfolder)
                        if os.path.splitext(f)[1].lower().lstrip('.') in IMAGE_EXTENSIONS
                    ])
                    if images:
                        pdf_name = f"{entry}.pdf"
                        pdf_path = os.path.join(input_folder, pdf_name)
                        self.log_message(f"Merging {len(images)} images from '{entry}/' -> {pdf_name}")
                        result = merge_images_to_pdf(images, pdf_path)
                        if result:
                            self.log_message(f"Created {pdf_name} ({len(images)} pages)")
                            # Remove subfolder after successful merge
                            import shutil as _shutil
                            _shutil.rmtree(subfolder)
                        else:
                            self.log_message(f"Failed to merge images in '{entry}/'")

            # Get all files in input folder
            files = []
            for filename in os.listdir(input_folder):
                filepath = os.path.join(input_folder, filename)
                if os.path.isfile(filepath):
                    files.append(filepath)
            
            self.log_message(f"Found {len(files)} files to process")
            
            # Process each file
            for i, filepath in enumerate(files):
                try:
                    self.log_message(f"Processing file {i+1}/{len(files)}: {os.path.basename(filepath)}")
                    
                    # Check if file is complete (stable size)
                    file_size = os.path.getsize(filepath)
                    time.sleep(0.1)  # Small delay to let any write operations complete
                    if os.path.getsize(filepath) != file_size:
                        self.log_message(f"Skipping incomplete file: {os.path.basename(filepath)}")
                        continue
                    
                    file_extension = os.path.splitext(filepath)[1].lower()[1:]
                    
                    # Determine file type and process accordingly
                    if file_extension in ['pdf']:
                        processed_text = extract_text_from_pdf(filepath)
                        category = "Unknown"
                        date = None
                        description = "document"
                        
                        # If no text, try OCR
                        if not processed_text:
                            self.log_message(f"Attempting OCR for {os.path.basename(filepath)}")
                            ocr_text = extract_text_from_file(filepath)
                            processed_text = ocr_text if ocr_text else ""
                    
                    elif file_extension in ['jpg', 'jpeg', 'png', 'webp', 'tiff']:
                        # Resize large images (mobile photos) to 1000px width
                        max_w = self.config.get('max_image_width', 1000)
                        resized_path = resize_image(filepath, max_w,
                                                   self.config.get('jpeg_quality', 85))
                        if resized_path:
                            filepath = resized_path

                        # Extract text with OCR
                        processed_text = extract_text_from_file(filepath)
                        category = "Unknown"
                        date = None
                        description = "document"
                        
                    else:
                        self.log_message(f"Unsupported file type: {file_extension}")
                        continue
                    
                    # Classify document
                    category = classify_document(processed_text, self.config["categories"])
                    if not processed_text:
                        processed_text = ""
                    
                    # Extract date from content
                    date = extract_date_from_text(processed_text)
                    if not date:
                        # Use file creation date or today's date
                        try:
                            import datetime
                            date = datetime.datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d')
                        except:
                            date = "unknown-date"
                    
                    # Extract meaningful description from content
                    description = find_first_meaningful_phrase(processed_text, 4) if processed_text else "document"
                    
                    # Move file to appropriate category folder
                    new_filepath = move_file(filepath, category, date, description, output_folder, 
                                           self.config.get("archive_originals", True))
                    
                    if new_filepath:
                        self.log_message(f"Successfully moved: {os.path.basename(new_filepath)}")
                        log_file_processed(self.log_func, filepath, category, os.path.basename(new_filepath))
                    else:
                        self.log_message(f"Failed to move file: {os.path.basename(filepath)}")
                        log_file_error(self.log_func, filepath, f"Could not move file to {category}")
                        
                except Exception as e:
                    self.log_message(f"Error processing {os.path.basename(filepath)}: {str(e)}")
                    log_file_error(self.log_func, filepath, str(e))
                    
            log_processing_complete(self.log_func)
            self.log_message("Processing completed successfully!")
            
        except Exception as e:
            self.log_message(f"Error during processing: {str(e)}")
            self.log_func("Processing error", level="ERROR", error=str(e))
        finally:
            self.is_processing = False
            self.process_button.config(state="normal", text="▶  Process Documents", bg="#6c5ce7")
            self.update_status("Completed ✅")

def main():
    root = tk.Tk()
    app = SortyrApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()