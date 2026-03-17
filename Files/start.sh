#!/bin/bash
# Script to setup and run the YouTube Downloader App

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt --upgrade
pip install --upgrade yt-dlp

echo "Starting Application..."
python main.py
