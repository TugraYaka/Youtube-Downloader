import sys
import os
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QProgressBar, QMessageBox, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class DownloadThread(QThread):
    progress_update = pyqtSignal(float, str)
    status_update = pyqtSignal(str)
    download_complete = pyqtSignal(str, bool) # True if success, False if error

    def __init__(self, url, format_type):
        super().__init__()
        self.url = url
        self.format_type = format_type

    def run(self):
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        ydl_opts = {
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'sleep_interval': 1,
            'max_sleep_interval': 3,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }

        if self.format_type == "Audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })

        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    progress_pct = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024
                        status = f"Downloading... {speed_mb:.1f} MB/s"
                    else:
                        status = "Downloading..."
                    self.progress_update.emit(progress_pct, status)
            elif d['status'] == 'finished':
                self.progress_update.emit(100.0, "Processing file...")

        ydl_opts['progress_hooks'] = [progress_hook]

        try:
            self.status_update.emit("Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.download_complete.emit(f"Saved to Downloads\n{self.url}", True)
        except Exception as e:
            self.download_complete.emit(f"Error: {str(e)}", False)


class YouTubeDownloaderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Downloader")
        self.setFixedSize(300, 300) # Small square UI

        # Set dark theme palette (macOS style dark mode)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(40, 42, 54))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        self.setPalette(palette)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title Label
        title = QLabel("Video Downloader")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #f8f8f2; margin-bottom: 10px;")
        layout.addWidget(title)

        # URL Input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube link here...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #6272a4;
                border-radius: 5px;
                background-color: #44475a;
                color: white;
            }
        """)
        layout.addWidget(self.url_input)

        # Format Selector
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video (MP4)", "Audio (MP3)"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #6272a4;
                border-radius: 5px;
                background-color: #44475a;
                color: white;
            }
        """)
        layout.addWidget(self.format_combo)

        # Download Button
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.on_download_clicked)
        self.download_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #50fa7b;
                color: #282a36;
                font-weight: bold;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #69ff94;
            }
            QPushButton:disabled {
                background-color: #6272a4;
                color: #282a36;
            }
        """)
        layout.addWidget(self.download_btn)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #282a36;
            }
            QProgressBar::chunk {
                background-color: #50fa7b;
                border-radius: 4px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #8be9fd;")
        layout.addWidget(self.status_label)

        layout.addStretch() # Push everything up
        central_widget.setLayout(layout)

    # --- Download Logic ---
    def on_download_clicked(self):
        url = self.url_input.text().strip()
        if not url or ("youtube.com" not in url and "youtu.be" not in url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid YouTube video URL.")
            return

        format_str = "Video" if self.format_combo.currentIndex() == 0 else "Audio"
        
        # UI State update
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.url_input.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Downloading...")
        
        # Start Thread
        self.thread = DownloadThread(url, format_str)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.status_update.connect(self.update_status)
        self.thread.download_complete.connect(self.download_finished)
        self.thread.start()

    def update_progress(self, pct, status):
        self.progress_bar.setValue(int(pct))
        self.status_label.setText(status)

    def update_status(self, status):
        self.status_label.setText(status)

    def download_finished(self, message, success):
        self.progress_bar.hide()
        
        # Reset UI State
        self.url_input.setEnabled(True)
        self.url_input.clear()
        self.format_combo.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Download")
        
        if success:
            self.status_label.setStyleSheet("color: #50fa7b;") # Green
            self.status_label.setText("Success!")
            QMessageBox.information(self, "Download Complete", message)
        else:
            self.status_label.setStyleSheet("color: #ff5555;") # Red
            self.status_label.setText("Failed")
            QMessageBox.critical(self, "Download Failed", message)
            
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #8be9fd;")

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloaderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
