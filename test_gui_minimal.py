#!/usr/bin/env python3
"""
Minimal GUI test to verify PyQt6 and virtual display setup
"""
import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


def test_gui():
    """Test basic GUI functionality in offscreen mode or skip gracefully."""
    # Ensure offscreen platform for headless CI
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    try:
        app = QApplication.instance() or QApplication(sys.argv)

        # Create window but don't show it in headless environments to avoid plugin crashes
        window = QMainWindow()
        window.setWindowTitle("Omnix GUI Test")
        window.setGeometry(100, 100, 400, 200)

        label = QLabel("GUI Testing Environment Ready!", window)
        label.setGeometry(50, 50, 300, 100)
        label.setStyleSheet("font-size: 16px; color: #00BFFF;")

        # Process events briefly to exercise widget creation
        app.processEvents()

    except Exception:
        # If we cannot initialize the Qt platform in this environment, skip the test
        import pytest

        pytest.skip("GUI tests require an available Qt platform plugin")

    # Auto-close after 100ms and return success
    QTimer.singleShot(100, app.quit)
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_gui())
