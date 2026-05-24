# Sortyr

> Smart document sorting for macOS

A macOS document sorting app for Apple Silicon. Automatically organizes documents into categories based on content analysis.

## Features

- **Native macOS OCR** — Uses Apple's Vision framework directly, no Tesseract needed
- **PDF & image support** — PDF, JPEG, PNG, WebP, TIFF
- **Rule-based classification** — Configurable keyword categories
- **Automatic date extraction** — Detects dates in document content
- **Smart file naming** — `CATEGORY-YYYY-MM-DD-Description.ext`
- **Duplicate handling** — Auto-numbered suffixes
- **Original archiving** — Keeps originals safely backed up
- **Simple GUI** — tkinter-based, no dependencies beyond Python

## Requirements

- macOS (Apple Silicon — M1/M2/M3/M4)
- Python 3.9+

## Installation

```bash
git clone https://github.com/gabrielvaraljay/sortyr.git
cd sortyr
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
source venv/bin/activate
python app.py
```

1. Select input folder (where your unsorted documents are)
2. Select output folder (where sorted documents will go)
3. Click **Process Documents**

Files are sorted into category subfolders with standardized filenames:

```
processed/
├── NHS/
│   └── NHS-2026-05-22-Hospital-Appointment.pdf
├── HMRC/
│   └── HMRC-2026-01-15-Self-Assessment.pdf
├── Bank/
│   └── Bank-2026-03-10-Monthly-Statement.pdf
└── Unknown/
    └── Unknown-2026-05-22-Document.png
```

## Configuration

Edit `config.json` to customize categories and keywords:

```json
{
  "categories": {
    "NHS": ["NHS", "hospital", "appointment", "GP"],
    "HMRC": ["HMRC", "tax", "self assessment", "PAYE"],
    "Bank": ["bank", "statement", "transaction"],
    "Invoices": ["invoice", "receipt", "payment"]
  },
  "input_folder": "./input",
  "output_folder": "./processed",
  "archive_originals": true,
  "max_image_width": 1200,
  "jpeg_quality": 85
}
```

## How OCR Works

On macOS, Sortyr uses Apple's **Vision framework** via `pyobjc-framework-Vision` for native, high-quality text recognition. This runs entirely on-device using the Neural Engine on Apple Silicon — no external OCR engine needed.

If you need cross-platform support, install `pytesseract` as an optional fallback:

```bash
pip install pytesseract
brew install tesseract
```

## Project Structure

```
sortyr/
├── app.py              # Main entry + tkinter GUI
├── config.py           # Load/save config.json
├── ocr.py              # OCR (macOS Vision framework, pytesseract fallback)
├── classifier.py       # Rule-based keyword classification
├── renamer.py          # Standardized filename generation
├── image_processor.py  # Image resizing
├── pdf_processor.py    # PDF text extraction with OCR fallback
├── file_mover.py       # File sorting + duplicate handling
├── logger_module.py    # JSON logging
├── config.json         # Category configuration
├── requirements.txt
└── test_app.py         # Basic tests
```

## License

MIT — see [LICENSE](LICENSE)
