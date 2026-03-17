# YouTube Download Manager

A lightweight macOS desktop application for downloading YouTube videos and audio.

## Features

- Download YouTube videos in MP4 format
- Extract audio from YouTube videos in MP3 format (192 kbps)
- Real-time progress bar showing download speed and status
- Dark-themed, minimal square UI
- Packaged as a standalone macOS application (no Python required)

## Installation

1. Open `YoutubeDownloader.dmg`.
2. Drag the `YoutubeDownloader` app into your `Applications` folder.
3. Launch the app from Applications or Launchpad.

> Note: Since this app is not notarized by Apple, macOS may block it on first launch.  
> To allow it, go to System Settings -> Privacy and Security -> and click "Open Anyway".

## Usage

1. Copy a YouTube video URL from your browser.
2. Paste it into the input field in the app.
3. Select the desired format: `Video (MP4)` or `Audio (MP3)`.
4. Click the `Download` button.
5. The file will be saved to your `Downloads` folder automatically.

## Audio (MP3) Note

MP3 extraction requires `ffmpeg` to be installed on your system.  
If you do not have it, install it via Homebrew:

```bash
brew install ffmpeg
```

## Building from Source

### Requirements

- Python 3.10 or later (recommended)
- pip

### Steps

```bash
# Clone or download the project folder
cd Youtube-Download-Manager

# Install dependencies
pip install -r requirements.txt

# Run directly
python3 main.py

# Or build the macOS app and DMG
./build_macos.sh
```

## Dependencies

| Package | Purpose |
|---|---|
| `yt-dlp` | Core video/audio downloading engine |
| `PyQt6` | GUI framework |
| `pyinstaller` | Compiles app into a standalone `.app` bundle |
| `dmgbuild` | Packages the `.app` into a macOS `.dmg` installer |

## License

This project is for personal use only. Downloading copyrighted content may violate YouTube's Terms of Service.
