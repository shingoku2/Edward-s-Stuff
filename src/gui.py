"""
GUI Module
Main application interface with overlay capabilities
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon,
    QMenu, QFrame, QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QAction, QFont, QPalette, QColor, QKeySequence, QShortcut
from typing import Optional, Dict
import os


class GameDetectionThread(QThread):
    """Background thread for game detection"""
    game_detected = pyqtSignal(dict)
    game_lost = pyqtSignal()

    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.running = True
        self.current_game = None

    def run(self):
        """Run game detection loop"""
        while self.running:
            game = self.detector.detect_running_game()

            if game and game != self.current_game:
                self.current_game = game
                self.game_detected.emit(game)
            elif not game and self.current_game:
                self.current_game = None
                self.game_lost.emit()

            self.msleep(5000)  # Check every 5 seconds

    def stop(self):
        """Stop the detection thread"""
        self.running = False


class ChatWidget(QWidget):
    """Chat widget for Q&A with AI"""

    def __init__(self, ai_assistant):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 10px;
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask a question about the game...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14b8a6;
            }
            QPushButton:pressed {
                background-color: #0a5a5d;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Clear button
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
        """)
        self.clear_button.clicked.connect(self.clear_chat)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def send_message(self):
        """Send message to AI"""
        question = self.input_field.text().strip()

        if not question:
            return

        # Display user message
        self.add_message("You", question, is_user=True)
        self.input_field.clear()

        # Get AI response
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")

        try:
            response = self.ai_assistant.ask_question(question)
            self.add_message("AI Assistant", response, is_user=False)
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}", is_user=False)

        self.send_button.setEnabled(True)
        self.send_button.setText("Send")

    def add_message(self, sender: str, message: str, is_user: bool = True):
        """Add message to chat display"""
        color = "#14b8a6" if is_user else "#f59e0b"
        self.chat_display.append(f'<p><span style="color: {color}; font-weight: bold;">{sender}:</span> {message}</p>')
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.clear()
        self.ai_assistant.clear_history()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, game_detector, ai_assistant, info_scraper):
        super().__init__()
        self.game_detector = game_detector
        self.ai_assistant = ai_assistant
        self.info_scraper = info_scraper

        self.current_game = None
        self.detection_thread = None

        self.init_ui()
        self.start_game_detection()

    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Gaming AI Assistant")
        self.setGeometry(100, 100, 900, 700)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Game info panel
        self.game_info_label = QLabel("No game detected")
        self.game_info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #14b8a6;
                padding: 15px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        self.game_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.game_info_label)

        # Quick actions
        actions_layout = QHBoxLayout()

        self.tips_button = QPushButton("Get Tips")
        self.tips_button.clicked.connect(self.get_tips)
        self.tips_button.setEnabled(False)

        self.overview_button = QPushButton("Game Overview")
        self.overview_button.clicked.connect(self.get_overview)
        self.overview_button.setEnabled(False)

        for button in [self.tips_button, self.overview_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6366f1;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 11pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #818cf8;
                }
                QPushButton:disabled {
                    background-color: #374151;
                    color: #6b7280;
                }
            """)
            actions_layout.addWidget(button)

        main_layout.addLayout(actions_layout)

        # Chat widget
        self.chat_widget = ChatWidget(self.ai_assistant)
        main_layout.addWidget(self.chat_widget)

        central_widget.setLayout(main_layout)

        # System tray
        self.create_system_tray()

        # Keyboard shortcuts
        self.create_shortcuts()

    def create_header(self) -> QWidget:
        """Create header widget"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("🎮 Gaming AI Assistant")
        title.setStyleSheet("""
            QLabel {
                color: #14b8a6;
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("Your real-time gaming companion powered by AI")
        subtitle.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 11pt;
            }
        """)
        layout.addWidget(subtitle)

        header.setLayout(layout)
        return header

    def create_system_tray(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)

        # Create menu
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def create_shortcuts(self):
        """Create keyboard shortcuts"""
        # Toggle visibility
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+Shift+G"), self)
        toggle_shortcut.activated.connect(self.toggle_visibility)

    def toggle_visibility(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def start_game_detection(self):
        """Start game detection thread"""
        self.detection_thread = GameDetectionThread(self.game_detector)
        self.detection_thread.game_detected.connect(self.on_game_detected)
        self.detection_thread.game_lost.connect(self.on_game_lost)
        self.detection_thread.start()

    def on_game_detected(self, game: Dict):
        """Handle game detection"""
        self.current_game = game
        game_name = game.get('name', 'Unknown Game')

        self.game_info_label.setText(f"🎮 Now Playing: {game_name}")
        self.game_info_label.setStyleSheet("""
            QLabel {
                background-color: #14532d;
                color: #22c55e;
                padding: 15px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)

        # Enable buttons
        self.tips_button.setEnabled(True)
        self.overview_button.setEnabled(True)

        # Update AI context
        self.ai_assistant.set_current_game(game)

        # Auto-get overview
        self.get_overview()

    def on_game_lost(self):
        """Handle game close"""
        self.current_game = None
        self.game_info_label.setText("No game detected")
        self.game_info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #14b8a6;
                padding: 15px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)

        # Disable buttons
        self.tips_button.setEnabled(False)
        self.overview_button.setEnabled(False)

    def get_tips(self):
        """Get tips for current game"""
        if not self.current_game:
            return

        game_name = self.current_game.get('name')
        self.chat_widget.add_message("System", "Getting tips...", is_user=False)

        try:
            tips = self.ai_assistant.get_tips_and_strategies()
            self.chat_widget.add_message("AI Assistant", tips, is_user=False)
        except Exception as e:
            self.chat_widget.add_message("System", f"Error: {str(e)}", is_user=False)

    def get_overview(self):
        """Get game overview"""
        if not self.current_game:
            return

        game_name = self.current_game.get('name')
        self.chat_widget.add_message("System", f"Getting overview of {game_name}...", is_user=False)

        try:
            overview = self.ai_assistant.get_game_overview(game_name)
            self.chat_widget.add_message("AI Assistant", overview, is_user=False)
        except Exception as e:
            self.chat_widget.add_message("System", f"Error: {str(e)}", is_user=False)

    def closeEvent(self, event):
        """Handle window close"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Gaming AI Assistant",
            "Application minimized to tray. Press Ctrl+Shift+G to toggle.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


def run_gui(game_detector, ai_assistant, info_scraper):
    """Run the GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Gaming AI Assistant")

    window = MainWindow(game_detector, ai_assistant, info_scraper)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # This would normally import from other modules
    print("GUI module - run from main.py")
