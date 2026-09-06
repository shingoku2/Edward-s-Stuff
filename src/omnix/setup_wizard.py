"""
First-Run Setup Wizard
Guides users through Ollama setup
"""

import logging
import webbrowser
from typing import List, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from omnix.provider_tester import ProviderTester

logger = logging.getLogger(__name__)


class TestConnectionThread(QThread):
    """Background thread for testing Ollama connection"""

    test_complete = pyqtSignal(bool, str)

    def __init__(self, base_url: str, timeout: float = 15.0):
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout

    def run(self):
        """Run connection test in background"""
        try:
            success, message = ProviderTester.test_ollama(self.base_url, timeout=self.timeout)
            self.test_complete.emit(success, message)
        except Exception as e:
            logger.error(f"Connection test failed: {e}", exc_info=True)
            self.test_complete.emit(False, f"Test failed: {str(e)}")


class FetchModelsThread(QThread):
    """Background thread for fetching Ollama models"""

    models_fetched = pyqtSignal(list)
    fetch_failed = pyqtSignal(str)

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    def run(self):
        """Fetch models from Ollama"""
        try:
            import ollama

            client = ollama.Client(host=self.base_url)
            models_response = client.list()
            models = [m.get("name", "") for m in models_response.get("models", []) if m.get("name")]
            self.models_fetched.emit(models)
        except ImportError:
            self.fetch_failed.emit("Ollama library not installed")
        except Exception as e:
            self.fetch_failed.emit(str(e))


class SetupWizard(QDialog):
    """First-run setup wizard for Ollama configuration"""

    setup_complete = pyqtSignal(str, dict)  # provider ('ollama'), config dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_thread: Optional[TestConnectionThread] = None
        self.fetch_thread: Optional[FetchModelsThread] = None
        self.ollama_host = "http://localhost:11434"
        self.ollama_model = "llama3"
        self.connection_tested = False

        self.init_ui()

    def init_ui(self):
        """Initialize the wizard UI"""
        self.setWindowTitle("Gaming AI Assistant - Setup")
        self.setMinimumSize(650, 500)
        self.setModal(True)

        layout = QVBoxLayout()

        # Stacked widget for wizard pages
        self.pages = QStackedWidget()

        # Create wizard pages
        self.create_welcome_page()
        self.create_setup_page()
        self.create_complete_page()

        layout.addWidget(self.pages)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.previous_page)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        nav_layout.addWidget(self.back_button)

        nav_layout.addStretch()

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #14b8a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0f9688;
            }
            QPushButton:disabled {
                background-color: #374151;
                color: #6b7280;
            }
        """)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

        self.setLayout(layout)
        self.apply_theme()
        self.update_navigation()

    def create_welcome_page(self):
        """Create the welcome page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎮 Welcome to Gaming AI Assistant!")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(30)

        # Introduction
        intro = QLabel(
            "<h3>Local AI, No API Keys Required!</h3>"
            "<p>This assistant uses <b>Ollama</b> to run AI models locally on your computer.</p>"
            "<br>"
            "<h3>Benefits:</h3>"
            "<p>✓ <b>Free</b> - No subscription or API costs</p>"
            "<p>✓ <b>Private</b> - Your data stays on your PC</p>"
            "<p>✓ <b>Fast</b> - No internet latency</p>"
            "<p>✓ <b>Offline</b> - Works without internet</p>"
            "<br>"
            "<h3>Requirements:</h3>"
            "<p>• Ollama installed from <a href='https://ollama.com' style='color: #14b8a6;'>ollama.com</a></p>"
            "<p>• At least one model pulled (e.g., <code>ollama pull llama3</code>)</p>"
            "<p>• 8GB+ RAM recommended for most models</p>"
        )
        intro.setWordWrap(True)
        intro.setOpenExternalLinks(True)
        intro.setStyleSheet("font-size: 11pt; line-height: 1.5;")
        layout.addWidget(intro)

        layout.addStretch()

        page.setLayout(layout)
        self.pages.addWidget(page)

    def create_setup_page(self):
        """Create the Ollama setup page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Configure Ollama")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addSpacing(20)

        # Ollama Configuration Group
        config_group = QGroupBox("Ollama Settings")
        config_layout = QVBoxLayout()

        # Host URL
        host_label = QLabel("Ollama Host URL:")
        host_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        config_layout.addWidget(host_label)

        host_help = QLabel("Default for local: http://localhost:11434")
        host_help.setStyleSheet("font-size: 9pt; color: #9ca3af;")
        config_layout.addWidget(host_help)

        self.host_input = QLineEdit()
        self.host_input.setText(self.ollama_host)
        self.host_input.setPlaceholderText("http://localhost:11434")
        self.host_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
            }
        """)
        config_layout.addWidget(self.host_input)

        config_layout.addSpacing(15)

        # Model selection
        model_label = QLabel("Default Model:")
        model_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        config_layout.addWidget(model_label)

        model_help = QLabel("Select from installed models or type a model name")
        model_help.setStyleSheet("font-size: 9pt; color: #9ca3af;")
        config_layout.addWidget(model_help)

        model_row = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItem("llama3")
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
            }
        """)
        model_row.addWidget(self.model_combo, stretch=1)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_models)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        model_row.addWidget(refresh_btn)

        config_layout.addLayout(model_row)

        config_layout.addSpacing(15)

        # Test connection
        test_row = QHBoxLayout()

        self.test_btn = QPushButton("🔗 Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14b8a6;
            }
            QPushButton:disabled {
                background-color: #374151;
            }
        """)
        test_row.addWidget(self.test_btn)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 10pt;")
        test_row.addWidget(self.status_label, stretch=1)

        config_layout.addLayout(test_row)

        config_group.setLayout(config_layout)
        config_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #1e1e1e;
            }
        """)
        layout.addWidget(config_group)

        # Help section
        help_group = QGroupBox("Need Ollama?")
        help_layout = QVBoxLayout()

        help_text = QLabel(
            "1. Download from <a href='https://ollama.com' style='color: #14b8a6;'>ollama.com</a><br>"
            "2. Install and run Ollama<br>"
            "3. Open terminal and run: <code>ollama pull llama3</code><br>"
            "4. Click 'Test Connection' above"
        )
        help_text.setWordWrap(True)
        help_text.setOpenExternalLinks(True)
        help_text.setStyleSheet("font-size: 10pt;")
        help_layout.addWidget(help_text)

        get_ollama_btn = QPushButton("📥 Get Ollama")
        get_ollama_btn.clicked.connect(lambda: webbrowser.open("https://ollama.com"))
        get_ollama_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        help_layout.addWidget(get_ollama_btn)

        help_group.setLayout(help_layout)
        help_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #1e1e1e;
            }
        """)
        layout.addWidget(help_group)

        layout.addStretch()

        page.setLayout(layout)
        self.pages.addWidget(page)

    def create_complete_page(self):
        """Create the completion page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("✅ Setup Complete!")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(30)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(self.summary_label)

        layout.addSpacing(20)

        tips = QLabel(
            "<h3>Tips:</h3>"
            "<p>• Press <b>Ctrl+Shift+G</b> to toggle the overlay</p>"
            "<p>• Start a game to get game-specific assistance</p>"
            "<p>• Use Settings (⚙️) to change model or host</p>"
            "<br>"
            "<p>Click 'Finish' to start using the assistant!</p>"
        )
        tips.setWordWrap(True)
        tips.setStyleSheet("font-size: 10pt;")
        layout.addWidget(tips)

        layout.addStretch()

        page.setLayout(layout)
        self.pages.addWidget(page)

    def test_connection(self):
        """Test connection to Ollama"""
        base_url = self.host_input.text().strip() or "http://localhost:11434"

        self.test_btn.setEnabled(False)
        self.status_label.setText("Testing connection...")
        self.status_label.setStyleSheet("font-size: 10pt; color: #fbbf24;")

        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.terminate()
            self.test_thread.wait(1000)

        self.test_thread = TestConnectionThread(base_url)
        self.test_thread.test_complete.connect(self.on_test_complete)
        self.test_thread.finished.connect(lambda: self.test_btn.setEnabled(True))
        self.test_thread.start()

    def on_test_complete(self, success: bool, message: str):
        """Handle test completion"""
        self.test_btn.setEnabled(True)
        self.connection_tested = success

        if success:
            self.status_label.setText("✅ Connected!")
            self.status_label.setStyleSheet("font-size: 10pt; color: #10b981; font-weight: bold;")
            self.refresh_models()
        else:
            self.status_label.setText("❌ Failed")
            self.status_label.setStyleSheet("font-size: 10pt; color: #ef4444; font-weight: bold;")
            QMessageBox.warning(self, "Connection Failed", message)

        self.update_navigation()

    def refresh_models(self):
        """Refresh the list of available models"""
        base_url = self.host_input.text().strip() or "http://localhost:11434"

        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait(1000)

        self.fetch_thread = FetchModelsThread(base_url)
        self.fetch_thread.models_fetched.connect(self.on_models_fetched)
        self.fetch_thread.fetch_failed.connect(self.on_models_fetch_failed)
        self.fetch_thread.start()

    def on_models_fetched(self, models: List[str]):
        """Handle successful model fetch"""
        current = self.model_combo.currentText()
        self.model_combo.clear()

        if models:
            self.model_combo.addItems(models)
            if current in models:
                self.model_combo.setCurrentText(current)
            else:
                self.model_combo.setCurrentText(models[0])
        else:
            self.model_combo.addItem("llama3")

    def on_models_fetch_failed(self, error: str):
        """Handle model fetch failure"""
        if self.model_combo.count() == 0:
            self.model_combo.addItem("llama3")

    def update_navigation(self):
        """Update navigation button states"""
        current_index = self.pages.currentIndex()

        self.back_button.setEnabled(current_index > 0)

        if current_index == self.pages.count() - 1:
            self.next_button.setText("Finish")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self.finish_setup)
        else:
            self.next_button.setText("Next →")
            try:
                self.next_button.clicked.disconnect()
            except TypeError:
                pass
            self.next_button.clicked.connect(self.next_page)

        # Enable/disable next based on page
        if current_index == 1:  # Setup page
            self.next_button.setEnabled(self.connection_tested)
        else:
            self.next_button.setEnabled(True)

    def next_page(self):
        """Go to next page"""
        current_index = self.pages.currentIndex()

        # Update summary when going to complete page
        if current_index == 1:
            self.ollama_host = self.host_input.text().strip() or "http://localhost:11434"
            self.ollama_model = self.model_combo.currentText().strip() or "llama3"

            self.summary_label.setText(
                f"<p><b>Ollama Host:</b> {self.ollama_host}</p>"
                f"<p><b>Default Model:</b> {self.ollama_model}</p>"
            )

        if current_index < self.pages.count() - 1:
            self.pages.setCurrentIndex(current_index + 1)
            self.update_navigation()

    def previous_page(self):
        """Go to previous page"""
        current_index = self.pages.currentIndex()
        if current_index > 0:
            self.pages.setCurrentIndex(current_index - 1)
            self.update_navigation()

    def finish_setup(self):
        """Complete the setup wizard"""
        try:
            # Save configuration
            from omnix.config import Config

            Config.save_to_env(
                ollama_host=self.ollama_host,
                ollama_model=self.ollama_model,
                overlay_hotkey="ctrl+shift+g",
                check_interval=5,
            )

            logger.info(f"Setup complete: host={self.ollama_host}, model={self.ollama_model}")

            # Emit completion signal
            self.setup_complete.emit(
                "ollama",
                {"ollama_host": self.ollama_host, "ollama_model": self.ollama_model},
            )

            QMessageBox.information(
                self,
                "Setup Complete",
                f"Ollama is configured!\n\n"
                f"Host: {self.ollama_host}\n"
                f"Model: {self.ollama_model}\n\n"
                f"Press Ctrl+Shift+G to toggle the overlay.",
            )

            self.accept()

        except Exception as e:
            logger.error(f"Setup failed: {e}", exc_info=True)
            QMessageBox.critical(self, "Setup Failed", f"Failed to save configuration:\n{str(e)}")

    def closeEvent(self, event):
        """Clean up threads on close"""
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.terminate()
            self.test_thread.wait(1000)
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait(1000)
        super().closeEvent(event)

    def apply_theme(self):
        """Apply dark theme to the wizard"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2a2a2a;
            }
        """)
