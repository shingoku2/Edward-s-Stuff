"""
GUI Module
Main application interface with overlay capabilities
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon,
    QMenu, QFrame, QDialog, QRadioButton, QButtonGroup, QMessageBox,
    QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QKeySequence, QShortcut, QIcon, QPixmap, QPainter, QColor
from typing import Optional, Dict
import os
import webbrowser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIWorkerThread(QThread):
    """Background thread for AI API calls to prevent GUI freezing"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_assistant, question, game_context=None):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.question = question
        self.game_context = game_context

    def run(self):
        """Run AI query in background"""
        try:
            response = self.ai_assistant.ask_question(self.question, self.game_context)
            self.response_ready.emit(response)
        except Exception as e:
            logger.error(f"AI worker thread error: {e}", exc_info=True)
            self.error_occurred.emit(str(e))


class GameDetectionThread(QThread):
    """Background thread for game detection"""
    game_detected = pyqtSignal(dict)
    game_lost = pyqtSignal()

    def __init__(self, game_detector):
        super().__init__()
        self.game_detector = game_detector
        self.running = True
        self.current_game = None

    def run(self):
        """Run game detection loop"""
        try:
            while self.running:
                game = self.game_detector.detect_running_game()

                if game and game != self.current_game:
                    self.current_game = game
                    self.game_detected.emit(game)
                    logger.info(f"Game detected: {game.get('name')}")
                elif not game and self.current_game:
                    self.current_game = None
                    self.game_lost.emit()
                    logger.info("Game closed")

                self.msleep(5000)  # Check every 5 seconds
        except Exception as e:
            logger.error(f"Game detection thread error: {e}", exc_info=True)

    def stop(self):
        """Stop the detection thread"""
        self.running = False
        logger.info("Game detection thread stopped")


class ChatWidget(QWidget):
    """Chat interface widget for Q&A interactions with AI assistant"""

    def __init__(self, ai_assistant):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.ai_worker = None
        self.init_ui()

    def init_ui(self):
        """Initialize the chat widget UI components"""
        layout = QVBoxLayout()

        # Chat history display area
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

        # User input area
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
            QPushButton:disabled {
                background-color: #374151;
                color: #6b7280;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Clear chat history button
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
        """Process and send user message to AI assistant"""
        question = self.input_field.text().strip()

        if not question:
            return

        # Check if AI assistant is configured
        if not self.ai_assistant:
            self.add_message(
                "System",
                "⚠️ AI assistant not configured. Please click the ⚙️ Settings button to add your API keys.",
                is_user=False
            )
            self.input_field.clear()
            return

        # Display user's question in chat
        self.add_message("You", question, is_user=True)
        self.input_field.clear()

        # Disable input while processing
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        self.send_button.setText("Thinking...")

        # Create and start worker thread
        self.ai_worker = AIWorkerThread(self.ai_assistant, question)
        self.ai_worker.response_ready.connect(self.on_ai_response)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.start()

    def on_ai_response(self, response: str):
        """Handle AI response"""
        self.add_message("AI Assistant", response, is_user=False)

    def on_ai_error(self, error: str):
        """Handle AI error"""
        self.add_message("System", f"Error: {error}", is_user=False)

    def on_ai_finished(self):
        """Re-enable input after AI finishes"""
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.send_button.setText("Send")
        self.ai_worker = None

    def add_message(self, sender: str, message: str, is_user: bool = True):
        """
        Add a formatted message to the chat display

        Args:
            sender: Name of the message sender
            message: Message content
            is_user: True if message is from user, False if from AI/system
        """
        color = "#14b8a6" if is_user else "#f59e0b"
        # Escape HTML to prevent issues with special characters
        message_escaped = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.chat_display.append(f'<p><span style="color: {color}; font-weight: bold;">{sender}:</span> {message_escaped}</p>')
        # Auto-scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def clear_chat(self):
        """Clear chat display and conversation history"""
        self.chat_display.clear()
        if self.ai_assistant:
            self.ai_assistant.clear_history()
        logger.info("Chat history cleared")


class SettingsDialog(QDialog):
    """Settings dialog for managing API keys and AI provider selection"""

    settings_saved = pyqtSignal(str, str, str, str)  # provider, openai_key, anthropic_key, gemini_key

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 600, 400)
        self.setModal(True)

        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
            }
            QLabel {
                color: #ffffff;
                font-size: 11pt;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
            }
            QRadioButton {
                color: #ffffff;
                font-size: 11pt;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::unchecked {
                border: 2px solid #3a3a3a;
                border-radius: 9px;
                background-color: #2a2a2a;
            }
            QRadioButton::indicator::checked {
                border: 2px solid #14b8a6;
                border-radius: 9px;
                background-color: #14b8a6;
            }
            QGroupBox {
                color: #14b8a6;
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()

        # Title
        title = QLabel("⚙️ AI Assistant Settings")
        title.setStyleSheet("""
            QLabel {
                color: #14b8a6;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(title)

        # Current provider display
        self.current_provider_label = QLabel(f"Current AI Provider: {self.config.ai_provider.upper()}")
        self.current_provider_label.setStyleSheet("""
            QLabel {
                color: #f59e0b;
                font-size: 12pt;
                padding: 5px;
            }
        """)
        layout.addWidget(self.current_provider_label)

        # AI Provider Selection
        provider_group = QGroupBox("Select AI Provider")
        provider_layout = QVBoxLayout()

        self.provider_button_group = QButtonGroup()

        self.anthropic_radio = QRadioButton("Anthropic Claude")
        self.openai_radio = QRadioButton("OpenAI GPT")
        self.gemini_radio = QRadioButton("Google Gemini")

        self.provider_button_group.addButton(self.anthropic_radio, 0)
        self.provider_button_group.addButton(self.openai_radio, 1)
        self.provider_button_group.addButton(self.gemini_radio, 2)

        # Set current provider
        if self.config.ai_provider == "anthropic":
            self.anthropic_radio.setChecked(True)
        elif self.config.ai_provider == "openai":
            self.openai_radio.setChecked(True)
        elif self.config.ai_provider == "gemini":
            self.gemini_radio.setChecked(True)
        else:
            self.anthropic_radio.setChecked(True)  # Default to Anthropic

        provider_layout.addWidget(self.anthropic_radio)
        provider_layout.addWidget(self.openai_radio)
        provider_layout.addWidget(self.gemini_radio)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)

        # API Keys Section
        keys_group = QGroupBox("API Keys")
        keys_layout = QVBoxLayout()

        # OpenAI API Key
        openai_label = QLabel("OpenAI API Key:")
        keys_layout.addWidget(openai_label)

        self.openai_key_input = QLineEdit()
        self.openai_key_input.setPlaceholderText("sk-...")
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.config.openai_api_key:
            self.openai_key_input.setText(self.config.openai_api_key)
        keys_layout.addWidget(self.openai_key_input)

        # Show/Hide OpenAI key button
        self.openai_show_button = QPushButton("Show")
        self.openai_show_button.setFixedWidth(80)
        self.openai_show_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.openai_show_button.clicked.connect(lambda: self.toggle_key_visibility(self.openai_key_input, self.openai_show_button))
        keys_layout.addWidget(self.openai_show_button)

        # Get OpenAI API Key button
        openai_get_key_button = QPushButton("Get API Key")
        openai_get_key_button.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #1a7f64;
            }
        """)
        openai_get_key_button.clicked.connect(lambda: self.open_api_key_page("https://platform.openai.com/api-keys"))
        keys_layout.addWidget(openai_get_key_button)

        keys_layout.addSpacing(10)

        # Anthropic API Key
        anthropic_label = QLabel("Anthropic API Key:")
        keys_layout.addWidget(anthropic_label)

        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setPlaceholderText("sk-ant-...")
        self.anthropic_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.config.anthropic_api_key:
            self.anthropic_key_input.setText(self.config.anthropic_api_key)
        keys_layout.addWidget(self.anthropic_key_input)

        # Show/Hide Anthropic key button
        self.anthropic_show_button = QPushButton("Show")
        self.anthropic_show_button.setFixedWidth(80)
        self.anthropic_show_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.anthropic_show_button.clicked.connect(lambda: self.toggle_key_visibility(self.anthropic_key_input, self.anthropic_show_button))
        keys_layout.addWidget(self.anthropic_show_button)

        # Get Anthropic API Key button
        anthropic_get_key_button = QPushButton("Get API Key")
        anthropic_get_key_button.setStyleSheet("""
            QPushButton {
                background-color: #c96329;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #a44d1f;
            }
        """)
        anthropic_get_key_button.clicked.connect(lambda: self.open_api_key_page("https://console.anthropic.com/settings/keys"))
        keys_layout.addWidget(anthropic_get_key_button)

        keys_layout.addSpacing(10)

        # Gemini API Key
        gemini_label = QLabel("Gemini API Key:")
        keys_layout.addWidget(gemini_label)

        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setPlaceholderText("AIza...")
        self.gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.config.gemini_api_key:
            self.gemini_key_input.setText(self.config.gemini_api_key)
        keys_layout.addWidget(self.gemini_key_input)

        # Show/Hide Gemini key button
        self.gemini_show_button = QPushButton("Show")
        self.gemini_show_button.setFixedWidth(80)
        self.gemini_show_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.gemini_show_button.clicked.connect(lambda: self.toggle_key_visibility(self.gemini_key_input, self.gemini_show_button))
        keys_layout.addWidget(self.gemini_show_button)

        # Get Gemini API Key button
        gemini_get_key_button = QPushButton("Get API Key")
        gemini_get_key_button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        gemini_get_key_button.clicked.connect(lambda: self.open_api_key_page("https://aistudio.google.com/app/apikey"))
        keys_layout.addWidget(gemini_get_key_button)

        keys_layout.addSpacing(10)

        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14b8a6;
            }
        """)
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        logger.info("Settings dialog initialized")

    def toggle_key_visibility(self, input_field, button):
        """Toggle password visibility for API key fields"""
        if input_field.echoMode() == QLineEdit.EchoMode.Password:
            input_field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("Hide")
        else:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("Show")

    def open_api_key_page(self, url):
        """Open API key signup/login page in browser"""
        try:
            webbrowser.open(url)
            logger.info(f"Opening API key page: {url}")
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open browser: {str(e)}")

    def save_settings(self):
        """Save settings and emit signal"""
        # Get selected provider
        if self.anthropic_radio.isChecked():
            provider = "anthropic"
        elif self.openai_radio.isChecked():
            provider = "openai"
        elif self.gemini_radio.isChecked():
            provider = "gemini"
        else:
            provider = "anthropic"  # Default to Anthropic

        # Get API keys
        openai_key = self.openai_key_input.text().strip()
        anthropic_key = self.anthropic_key_input.text().strip()
        gemini_key = self.gemini_key_input.text().strip()

        # Validate that at least one key is provided
        if not openai_key and not anthropic_key and not gemini_key:
            QMessageBox.warning(
                self,
                "Missing API Keys",
                "Please provide at least one API key."
            )
            return

        # Validate that the selected provider has a key
        if provider == "anthropic" and not anthropic_key:
            QMessageBox.warning(
                self,
                "Missing Anthropic Key",
                "You selected Anthropic but didn't provide an API key.\nPlease enter your Anthropic API key."
            )
            return

        if provider == "openai" and not openai_key:
            QMessageBox.warning(
                self,
                "Missing OpenAI Key",
                "You selected OpenAI but didn't provide an API key.\nPlease enter your OpenAI API key."
            )
            return

        if provider == "gemini" and not gemini_key:
            QMessageBox.warning(
                self,
                "Missing Gemini Key",
                "You selected Gemini but didn't provide an API key.\nPlease enter your Gemini API key."
            )
            return

        # Emit signal with settings
        self.settings_saved.emit(provider, openai_key, anthropic_key, gemini_key)

        logger.info(f"Settings saved: provider={provider}")

        # Show success message
        QMessageBox.information(
            self,
            "Settings Saved",
            f"Settings saved successfully!\n\nAI Provider: {provider.upper()}\n\nThe application will now reload with the new settings."
        )

        self.accept()


class MainWindow(QMainWindow):
    """Main application window with game detection and AI chat interface"""

    def __init__(self, game_detector, ai_assistant, info_scraper, config):
        super().__init__()
        self.game_detector = game_detector
        self.ai_assistant = ai_assistant  # Can be None if no API keys configured
        self.info_scraper = info_scraper
        self.config = config

        self.current_game = None
        self.detection_thread = None

        # Worker threads for button actions (prevents garbage collection crashes)
        self.tips_worker = None
        self.overview_worker = None

        # Track if this is first show (for auto-opening settings)
        self.first_show = True

        # Track dragging state
        self.dragging = False
        self.drag_position = None

        # Track resize state
        self.resizing = False
        self.resize_direction = None

        # Track minimized state
        self.is_minimized = config.overlay_minimized
        self.normal_height = config.overlay_height

        self.init_ui()
        self.start_game_detection()

    def init_ui(self):
        """Initialize the main window UI components and styling"""
        self.setWindowTitle("Gaming AI Assistant")

        # Set window position and size from config
        self.setGeometry(
            self.config.overlay_x,
            self.config.overlay_y,
            self.config.overlay_width,
            self.config.overlay_height
        )

        # Enable mouse tracking for resize grips
        self.setMouseTracking(True)

        # Apply dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Application header
        header = self.create_header()
        main_layout.addWidget(header)

        # Game detection status panel
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

        # Quick action buttons
        actions_layout = QHBoxLayout()

        self.tips_button = QPushButton("Get Tips")
        self.tips_button.clicked.connect(self.get_tips)
        self.tips_button.setEnabled(False)

        self.overview_button = QPushButton("Game Overview")
        self.overview_button.clicked.connect(self.get_overview)
        self.overview_button.setEnabled(False)

        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.open_settings)

        # Apply styling to action buttons
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

        # Settings button with distinct styling
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        actions_layout.addWidget(self.settings_button)

        main_layout.addLayout(actions_layout)

        # AI chat interface
        self.chat_widget = ChatWidget(self.ai_assistant)
        main_layout.addWidget(self.chat_widget)

        central_widget.setLayout(main_layout)

        # System tray integration
        self.create_system_tray()

        # Global keyboard shortcuts
        self.create_shortcuts()

        logger.info("Main window initialized")

    def create_header(self) -> QWidget:
        """Create and style the application header widget"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        main_layout = QVBoxLayout()

        # Top row with title and window controls
        top_row = QHBoxLayout()

        # Title section
        title_layout = QVBoxLayout()
        title = QLabel("🎮 Gaming AI Assistant")
        title.setStyleSheet("""
            QLabel {
                color: #14b8a6;
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)

        subtitle = QLabel("Your real-time gaming companion powered by AI")
        subtitle.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 11pt;
            }
        """)
        title_layout.addWidget(subtitle)

        top_row.addLayout(title_layout)
        top_row.addStretch()

        # Window control buttons
        controls_layout = QHBoxLayout()

        self.minimize_button = QPushButton("−")
        self.minimize_button.setToolTip("Minimize/Restore")
        self.minimize_button.clicked.connect(self.toggle_minimize)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 16pt;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:pressed {
                background-color: #1f2937;
            }
        """)
        controls_layout.addWidget(self.minimize_button)

        top_row.addLayout(controls_layout)

        main_layout.addLayout(top_row)

        header.setLayout(main_layout)
        return header

    def create_system_tray(self):
        """Create system tray icon with context menu"""
        self.tray_icon = QSystemTrayIcon(self)

        # Create a simple icon
        icon = self.create_tray_icon()
        self.tray_icon.setIcon(icon)

        # Build tray context menu
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        logger.info("System tray icon created")

    def create_tray_icon(self) -> QIcon:
        """Create a simple icon for the system tray"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setBrush(QColor("#14b8a6"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()

        return QIcon(pixmap)

    def create_shortcuts(self):
        """Register global keyboard shortcuts"""
        # Ctrl+Shift+G: Toggle window visibility
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+Shift+G"), self)
        toggle_shortcut.activated.connect(self.toggle_visibility)

    def toggle_visibility(self):
        """Toggle main window visibility between shown and hidden states"""
        if self.isVisible():
            self.hide()
            logger.info("Window hidden")
        else:
            self.show()
            self.activateWindow()
            logger.info("Window shown")

    def start_game_detection(self):
        """Initialize and start the game detection background thread"""
        self.detection_thread = GameDetectionThread(self.game_detector)
        self.detection_thread.game_detected.connect(self.on_game_detected)
        self.detection_thread.game_lost.connect(self.on_game_lost)
        self.detection_thread.start()
        logger.info("Game detection thread started")

    def on_game_detected(self, game: Dict):
        """
        Handle game detection event

        Args:
            game: Dictionary containing detected game information
        """
        self.current_game = game
        game_name = game.get('name', 'Unknown Game')

        # Update UI to show detected game
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

        # Enable game-specific action buttons
        self.tips_button.setEnabled(True)
        self.overview_button.setEnabled(True)

        # Update AI assistant context with current game
        self.ai_assistant.set_current_game(game)

        # Show notification in chat (no auto-overview to save API costs)
        self.chat_widget.add_message(
            "System",
            f"Detected {game_name}! Click 'Game Overview' for info or ask me any questions.",
            is_user=False
        )

        logger.info(f"Game detected event handled: {game_name}")

    def on_game_lost(self):
        """Handle game close/lost detection event"""
        self.current_game = None

        # Clear AI assistant's game context
        if self.ai_assistant:
            self.ai_assistant.current_game = None
            logger.info("Cleared AI assistant game context")

        # Reset UI to default state
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

        # Disable game-specific action buttons
        self.tips_button.setEnabled(False)
        self.overview_button.setEnabled(False)

        logger.info("Game lost event handled")

    def get_tips(self):
        """Request and display tips for the currently detected game"""
        if not self.current_game:
            return

        # Check if AI assistant is configured
        if not self.ai_assistant:
            self.chat_widget.add_message(
                "System",
                "⚠️ AI assistant not configured. Please click the ⚙️ Settings button to add your API keys.",
                is_user=False
            )
            return

        self.chat_widget.add_message("System", "Getting tips...", is_user=False)
        logger.info("Getting tips for current game")

        # Use worker thread
        self.tips_button.setEnabled(False)

        def get_tips_impl():
            try:
                tips = self.ai_assistant.get_tips_and_strategies()
                return tips
            except Exception as e:
                logger.error(f"Error getting tips: {e}", exc_info=True)
                return f"Error getting tips: {str(e)}"

        class TipsWorker(QThread):
            result_ready = pyqtSignal(str)

            def __init__(self, func):
                super().__init__()
                self.func = func

            def run(self):
                result = self.func()
                self.result_ready.emit(result)

        def cleanup_tips_worker():
            self.tips_button.setEnabled(True)
            self.tips_worker = None  # Clear reference after completion

        # Store worker as instance variable to prevent garbage collection
        self.tips_worker = TipsWorker(get_tips_impl)
        self.tips_worker.result_ready.connect(lambda tips: self.chat_widget.add_message("AI Assistant", tips, is_user=False))
        self.tips_worker.finished.connect(cleanup_tips_worker)
        self.tips_worker.start()

    def get_overview(self):
        """Request and display overview of the currently detected game"""
        if not self.current_game:
            return

        # Check if AI assistant is configured
        if not self.ai_assistant:
            self.chat_widget.add_message(
                "System",
                "⚠️ AI assistant not configured. Please click the ⚙️ Settings button to add your API keys.",
                is_user=False
            )
            return

        game_name = self.current_game.get('name')
        self.chat_widget.add_message("System", f"Getting overview of {game_name}...", is_user=False)
        logger.info(f"Getting overview for {game_name}")

        # Use worker thread
        self.overview_button.setEnabled(False)

        def get_overview_impl():
            try:
                logger.info(f"Requesting game overview for: {game_name}")
                overview = self.ai_assistant.get_game_overview(game_name)
                logger.info("Overview received successfully")
                return overview
            except Exception as e:
                logger.error(f"Error getting overview: {e}", exc_info=True)
                error_msg = f"Sorry, I couldn't get the overview. Error: {str(e)}\n\nPlease check your internet connection and API key."
                return error_msg

        class OverviewWorker(QThread):
            result_ready = pyqtSignal(str)
            error_occurred = pyqtSignal(str)

            def __init__(self, func):
                super().__init__()
                self.func = func

            def run(self):
                try:
                    result = self.func()
                    self.result_ready.emit(result)
                except Exception as e:
                    logger.error(f"Worker thread error: {e}", exc_info=True)
                    self.error_occurred.emit(f"Worker error: {str(e)}")

        def handle_overview_result(overview):
            try:
                self.chat_widget.add_message("AI Assistant", overview, is_user=False)
            except Exception as e:
                logger.error(f"Error displaying overview: {e}", exc_info=True)

        def handle_overview_error(error):
            try:
                self.chat_widget.add_message("System", f"Error: {error}", is_user=False)
            except Exception as e:
                logger.error(f"Error displaying error message: {e}", exc_info=True)

        def cleanup_worker():
            try:
                self.overview_button.setEnabled(True)
                self.overview_worker = None  # Clear reference after completion
            except Exception as e:
                logger.error(f"Error re-enabling button: {e}")

        # Store worker as instance variable to prevent garbage collection
        self.overview_worker = OverviewWorker(get_overview_impl)
        self.overview_worker.result_ready.connect(handle_overview_result)
        self.overview_worker.error_occurred.connect(handle_overview_error)
        self.overview_worker.finished.connect(cleanup_worker)
        self.overview_worker.start()

    def open_settings(self):
        """Open the settings dialog"""
        logger.info("Opening settings dialog")

        dialog = SettingsDialog(self, self.config)
        dialog.settings_saved.connect(self.handle_settings_saved)
        dialog.exec()

    def handle_settings_saved(self, provider, openai_key, anthropic_key, gemini_key):
        """Handle settings being saved"""
        logger.info("Handling settings save...")

        try:
            # Import config module to call save function
            from config import Config

            # Save settings to .env file
            Config.save_to_env(provider, openai_key, anthropic_key, gemini_key)

            # Reload configuration
            self.config = Config()

            # Reinitialize AI assistant with new settings
            from ai_assistant import AIAssistant

            old_ai_assistant = self.ai_assistant
            self.ai_assistant = AIAssistant(
                provider=self.config.ai_provider,
                api_key=self.config.get_api_key()
            )

            # Transfer current game context to new assistant
            if self.current_game:
                self.ai_assistant.set_current_game(self.current_game)

            # Update chat widget's AI assistant reference
            self.chat_widget.ai_assistant = self.ai_assistant

            # Show success message in chat
            self.chat_widget.add_message(
                "System",
                f"Settings updated! Now using {provider.upper()} AI provider.",
                is_user=False
            )

            logger.info(f"Settings applied successfully: provider={provider}")

        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
            self.chat_widget.add_message(
                "System",
                f"Error applying settings: {str(e)}",
                is_user=False
            )
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to apply settings:\n\n{str(e)}"
            )

    def quit_application(self):
        """Quit the application cleanly"""
        logger.info("Quitting application")
        self.cleanup()
        QApplication.quit()

    def cleanup(self):
        """Cleanup resources before closing"""
        logger.info("Cleaning up resources")

        # Stop game detection thread
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            self.detection_thread.wait(3000)  # Wait up to 3 seconds
            if self.detection_thread.isRunning():
                logger.warning("Game detection thread did not stop gracefully")
                self.detection_thread.terminate()

        # Stop any active AI worker threads
        if hasattr(self.chat_widget, 'ai_worker') and self.chat_widget.ai_worker:
            if self.chat_widget.ai_worker.isRunning():
                self.chat_widget.ai_worker.wait(2000)
                if self.chat_widget.ai_worker.isRunning():
                    self.chat_widget.ai_worker.terminate()

        # Stop tips worker if running
        if self.tips_worker and self.tips_worker.isRunning():
            self.tips_worker.wait(2000)
            if self.tips_worker.isRunning():
                logger.warning("Tips worker did not stop gracefully")
                self.tips_worker.terminate()

        # Stop overview worker if running
        if self.overview_worker and self.overview_worker.isRunning():
            self.overview_worker.wait(2000)
            if self.overview_worker.isRunning():
                logger.warning("Overview worker did not stop gracefully")
                self.overview_worker.terminate()

        logger.info("Cleanup complete")

    def showEvent(self, event):
        """
        Handle window show event - auto-open settings on first show if not configured

        Args:
            event: QShowEvent to be handled
        """
        super().showEvent(event)

        # On first show, check if AI assistant is configured
        if self.first_show:
            self.first_show = False

            # If no AI assistant or no API keys configured, auto-open settings
            if not self.ai_assistant or not self.config.is_configured():
                logger.info("No API keys configured - auto-opening settings dialog")

                # Show welcome message in chat
                self.chat_widget.add_message(
                    "System",
                    "Welcome to Gaming AI Assistant! 🎮\n\n"
                    "To get started, please configure your API keys in the Settings dialog.\n\n"
                    "Click the ⚙️ Settings button to enter your OpenAI or Anthropic API key.",
                    is_user=False
                )

                # Schedule settings dialog to open after a short delay (so window is fully shown)
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.open_settings)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking near edges for resize
            pos = event.pos()
            rect = self.rect()
            edge_margin = 10

            # Determine resize direction
            on_left = pos.x() < edge_margin
            on_right = pos.x() > rect.width() - edge_margin
            on_top = pos.y() < edge_margin
            on_bottom = pos.y() > rect.height() - edge_margin

            if on_left or on_right or on_top or on_bottom:
                self.resizing = True
                self.resize_direction = {
                    'left': on_left,
                    'right': on_right,
                    'top': on_top,
                    'bottom': on_bottom
                }
                self.drag_position = event.globalPosition().toPoint()
            else:
                # Start dragging
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging and resizing"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.dragging and self.drag_position is not None:
                # Move window
                self.move(event.globalPosition().toPoint() - self.drag_position)

            elif self.resizing and self.resize_direction is not None:
                # Resize window
                delta = event.globalPosition().toPoint() - self.drag_position
                self.drag_position = event.globalPosition().toPoint()

                geometry = self.geometry()

                if self.resize_direction['left']:
                    geometry.setLeft(geometry.left() + delta.x())
                if self.resize_direction['right']:
                    geometry.setRight(geometry.right() + delta.x())
                if self.resize_direction['top']:
                    geometry.setTop(geometry.top() + delta.y())
                if self.resize_direction['bottom']:
                    geometry.setBottom(geometry.bottom() + delta.y())

                # Enforce minimum size
                if geometry.width() >= 400 and geometry.height() >= 300:
                    self.setGeometry(geometry)

        else:
            # Update cursor based on position
            pos = event.pos()
            rect = self.rect()
            edge_margin = 10

            on_left = pos.x() < edge_margin
            on_right = pos.x() > rect.width() - edge_margin
            on_top = pos.y() < edge_margin
            on_bottom = pos.y() > rect.height() - edge_margin

            if (on_left and on_top) or (on_right and on_bottom):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif (on_right and on_top) or (on_left and on_bottom):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif on_left or on_right:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif on_top or on_bottom:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release and save window position/size"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging or self.resizing:
                # Save window position and size to config
                self.save_window_state()

            self.dragging = False
            self.resizing = False
            self.resize_direction = None
            self.drag_position = None

        super().mouseReleaseEvent(event)

    def save_window_state(self):
        """Save current window position and size to .env file"""
        geometry = self.geometry()
        Config.save_to_env(
            provider=self.config.ai_provider,
            openai_key=self.config.openai_api_key or '',
            anthropic_key=self.config.anthropic_api_key or '',
            gemini_key=self.config.gemini_api_key or '',
            overlay_hotkey=self.config.overlay_hotkey,
            check_interval=self.config.check_interval,
            overlay_x=geometry.x(),
            overlay_y=geometry.y(),
            overlay_width=geometry.width(),
            overlay_height=geometry.height(),
            overlay_minimized=self.is_minimized
        )
        logger.info(f"Saved window state: pos=({geometry.x()}, {geometry.y()}), size=({geometry.width()}x{geometry.height()})")

    def toggle_minimize(self):
        """Toggle window minimized state"""
        if self.is_minimized:
            # Restore
            self.resize(self.width(), self.normal_height)
            self.is_minimized = False
        else:
            # Minimize
            self.normal_height = self.height()
            self.resize(self.width(), 50)  # Minimize to title bar height
            self.is_minimized = True

        self.save_window_state()

    def closeEvent(self, event):
        """
        Handle window close event by minimizing to system tray instead of quitting

        Args:
            event: QCloseEvent to be handled
        """
        # Save window state before closing
        self.save_window_state()

        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Gaming AI Assistant",
            "Application minimized to tray. Press Ctrl+Shift+G to toggle.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
        logger.info("Window close event - minimized to tray")


def run_gui(game_detector, ai_assistant, info_scraper, config):
    """
    Initialize and run the GUI application

    Args:
        game_detector: Game detection service instance
        ai_assistant: AI assistant service instance
        info_scraper: Information scraper service instance
        config: Configuration instance
    """
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Gaming AI Assistant")

        window = MainWindow(game_detector, ai_assistant, info_scraper, config)
        window.show()

        # Handle application quit
        app.aboutToQuit.connect(window.cleanup)

        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"GUI error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Module should be run from main.py with proper dependencies
    print("GUI module - run from main.py")
