#!/bin/bash
set -e

# Clean previous builds
rm -rf build dist *.dmg

# Install deps in venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Build .app with PyInstaller
pyinstaller --noconfirm --windowed \
  --name "Sortyr" \
  --icon icon.icns \
  --add-data "config.json:." \
  --osx-bundle-identifier "com.gabrielvaraljay.sortyr" \
  --hidden-import PIL \
  --hidden-import objc \
  --collect-submodules pyobjc \
  app.py

# Create DMG
DMG_NAME="Sortyr-1.1.0.dmg"
hdiutil create -volname "Sortyr" -srcfolder "dist/Sortyr.app" -ov -format UDZO "$DMG_NAME"

echo "Built: $DMG_NAME"
echo "Size: $(du -h $DMG_NAME | cut -f1)"
