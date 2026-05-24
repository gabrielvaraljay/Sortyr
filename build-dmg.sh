#!/bin/bash
set -e

# Clean previous builds
rm -rf build dist

# Install deps in venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install py2app

# Build .app
python setup.py py2app

# Create DMG
DMG_NAME="Sortyr-1.0.0.dmg"
hdiutil create -volname "Sortyr" -srcfolder dist/Sortyr.app -ov -format UDZO "$DMG_NAME"

echo "Built: $DMG_NAME"