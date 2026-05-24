# Sortyr

> Smart document sorting for macOS

A macOS document sorting app for Apple Silicon. Automatically organizes documents into categories based on content analysis.

## Features

- **Native macOS OCR** — Uses Apple's Vision framework directly, no Tesseract needed
- **PDF & image support** — PDF, JPEG, PNG, WebP, TIFF
- **Smart classification** — Auto-detects vendor/organisation name from document content (no keyword config needed)
- **Automatic date extraction** — Detects dates in document content
- **Smart file naming** — `CATEGORY-YYYY-MM-DD-Description.ext`
- **Duplicate handling** — Auto-numbered suffixes
- **Auto-rotation** — Detects and fixes rotated/upside-down scans via OCR confidence
- **7-day trash** — Originals kept in `_trash/` for 7 days before auto-cleanup
- **Original archiving** — Keeps originals safely backed up
- **Persistent settings** — Folder paths survive app updates (`~/Library/Application Support/Sortyr/`)
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

Settings are stored in `~/Library/Application Support/Sortyr/config.json` and persist across app updates.

Classification is automatic -- the app reads the document and extracts the vendor/organisation name to use as the folder name. Common orgs (NHS, HMRC, Amazon, etc.) are normalised to clean names. No keyword config needed.

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
├── auto_rotate.py      # OCR-based rotation detection
├── config.json         # Default configuration
├── requirements.txt
└── test_app.py         # Basic tests
```

## Changelog

### v1.2.2 — 2026-05-24
- **Smart classifier**: auto-detects vendor/org name from document text, no keyword lists needed
- **Auto-rotation**: tries all 4 orientations, picks the one with best OCR confidence
- **7-day trash**: originals saved to `_trash/` before processing, auto-cleaned after 7 days
- **Persistent settings**: folder paths saved to `~/Library/Application Support/Sortyr/`, survive rebuilds
- **Subfolder merge safety**: originals backed up to trash before merge + delete

### v1.1.0 — 2026-05-24
- **Image resizing**: mobile photos auto-resized to 1000px width (was 1200), aspect ratio preserved, EXIF kept
- **Multi-page documents**: put photos in a subfolder inside input → auto-merged into single PDF, then OCR + classify as one document
- **Subfolder cleanup**: merged subfolders removed automatically after PDF creation

### v1.0.0 — 2026-05-23
- Initial release
- macOS native OCR via Apple Vision framework
- PDF + image support (PDF, JPEG, PNG, WebP, TIFF)
- Rule-based keyword classification with configurable categories
- Automatic date extraction from document content
- Smart file naming: `CATEGORY-YYYY-MM-DD-Description.ext`
- Duplicate handling with auto-numbered suffixes
- Original file archiving
- tkinter GUI with folder selection + processing
- JSON logging

## License

MIT — see [LICENSE](LICENSE)
