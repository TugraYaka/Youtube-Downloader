#!/bin/bash
# MacOS App & DMG Builder Script

set -e

APP_NAME="YoutubeDownloader"

echo "==========================================="
echo "  Building $APP_NAME for macOS"
echo "==========================================="

echo "\n1. Cleaning up previous builds..."
rm -rf build dist $APP_NAME.spec $APP_NAME.dmg

echo "\n2. Installing/Updating requirements..."
python3 -m venv venv || true
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade
pip install --upgrade yt-dlp

echo "\n3. Compiling standalone Application using PyInstaller (macOS windowed mode)..."
# We exclude rich and customtkinter since we moved to PyQt6 to reduce app size
pyinstaller --noconfirm \
            --windowed \
            --name "$APP_NAME" \
            --clean \
            --noconsole \
            --icon ytdownload.icns \
            --exclude-module tkinter \
            --exclude-module rich \
            main.py

echo "\n4. Creating the Drag-and-Drop .dmg file using dmgbuild..."
# We generate a simple settings.json for dmgbuild on the fly
cat <<EOT > build_settings.py
import os
files = [ 'dist/$APP_NAME.app' ]
symlinks = { 'Applications': '/Applications' }
format = 'UDBZ'
size = '500M'
icon_size = 120
text_size = 14
icon = 'ytdownload.icns'
window_rect = ((100, 100), (600, 400))
icon_locations = {
    '$APP_NAME.app': (140, 120),
    'Applications': (500, 120)
}
EOT

dmgbuild -s build_settings.py -D app="dist/$APP_NAME.app" "$APP_NAME GUI App" "$APP_NAME.dmg"

echo "\nCleaning up build settings..."
rm build_settings.py

echo "==========================================="
echo "  SUCCESS! "
echo "  Your application is ready: $APP_NAME.dmg"
echo "==========================================="
