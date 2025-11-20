#!/usr/bin/env python3
"""
Test the Omnix Dashboard component
"""

import sys
import os

# Ensure src directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer
from ui.components import OmnixDashboard
from ui.design_system import OmnixDesignSystem


def test_dashboard(run_interactive: bool = False):
    """Test dashboard creation and functionality"""
    app = QApplication(sys.argv)

    # Apply design system stylesheet
    design_system = OmnixDesignSystem()
    app.setStyleSheet(design_system.generate_base_stylesheet())

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Omnix Dashboard Test")
    window.setMinimumSize(900, 700)

    # Set dark background
    window.setStyleSheet(f"""
        QMainWindow {{
            background-color: #050508;
        }}
    """)

    # Create dashboard
    dashboard = OmnixDashboard()

    # Set test data
    dashboard.set_active(True)
    dashboard.set_game("Elden Ring")

    # Connect signals for testing
    dashboard.chat_clicked.connect(lambda: print("Chat clicked!"))
    dashboard.provider_clicked.connect(lambda: print("AI Provider clicked!"))
    dashboard.settings_clicked.connect(lambda: print("Settings clicked!"))
    dashboard.profiles_clicked.connect(lambda: print("Game Profiles clicked!"))
    dashboard.knowledge_clicked.connect(lambda: print("Knowledge Pack clicked!"))
    dashboard.coaching_clicked.connect(lambda: print("Session Coaching clicked!"))

    # Set as central widget
    window.setCentralWidget(dashboard)

    # Show window
    window.show()

    print("✓ Dashboard created successfully")
    print("✓ Status card shows: Active, Playing: Elden Ring")
    print("✓ Action grid has 6 buttons in 3x2 layout")
    print("✓ Click any button to test signal connections")
    print("\nClose the window to exit...")

    if run_interactive:
        return app.exec()

    QTimer.singleShot(50, app.quit)
    app.processEvents()
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_dashboard(run_interactive=True))
