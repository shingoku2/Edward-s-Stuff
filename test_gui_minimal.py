#!/usr/bin/env python3
"""
Minimal GUI test to verify PyQt6 and virtual display setup
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import QTimer

def test_gui():
    """Test basic GUI functionality"""
    print("Initializing QApplication...")
    app = QApplication(sys.argv)

    print("Creating main window...")
    window = QMainWindow()
    window.setWindowTitle("Omnix GUI Test")
    window.setGeometry(100, 100, 400, 200)

    label = QLabel("GUI Testing Environment Ready!", window)
    label.setGeometry(50, 50, 300, 100)
    label.setStyleSheet("font-size: 16px; color: #00BFFF;")

    window.show()
    print("Window created successfully!")
    print(f"Display: {app.primaryScreen().name()}")
    print(f"Resolution: {app.primaryScreen().size().width()}x{app.primaryScreen().size().height()}")
    print("GUI test passed! ✓")

    # Auto-close after 2 seconds
    QTimer.singleShot(2000, app.quit)

    return app.exec()

if __name__ == "__main__":
    sys.exit(test_gui())
