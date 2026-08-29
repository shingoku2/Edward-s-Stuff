"""
Ollama Configuration Tab
Simplified settings for local AI inference via Ollama
"""

import logging
import webbrowser
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QGroupBox,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, QThread

from src.config import Config
from src.provider_tester import ProviderTester

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
            success, message = ProviderTester.test_ollama(
                self.base_url, timeout=self.timeout
            )
            self.test_complete.emit(success, message)
        except Exception as e:
            logger.error(f"Connection test failed: {e}", exc_info=True)
            self.test_complete.emit(False, f"Test failed: {str(e)}")


class FetchModelsThread(QThread):
    """Background thread for fetching available Ollama models"""

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

            # Support both the older dict-shaped response and the current
            # ollama library's ListResponse/Model pydantic objects.
            raw_models = (
                models_response.get("models", [])
                if isinstance(models_response, dict)
                else getattr(models_response, "models", [])
            )

            models = []
            for m in raw_models:
                if isinstance(m, dict):
                    name = m.get("name") or m.get("model") or ""
                else:
                    name = getattr(m, "model", "") or getattr(m, "name", "")
                if name:
                    models.append(name)

            self.models_fetched.emit(models)
        except ImportError:
            self.fetch_failed.emit(
                "Ollama library not installed. Run: pip install ollama"
            )
        except Exception as e:
            logger.warning(f"Failed to fetch models: {e}")
            self.fetch_failed.emit(str(e))


class ProvidersTab(QWidget):
    """Ollama configuration tab for settings dialog"""

    config_changed = pyqtSignal(dict)  # Emitted when config changes
    provider_config_changed = pyqtSignal(str, dict)  # For compatibility

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.test_thread: Optional[TestConnectionThread] = None
        self.fetch_thread: Optional[FetchModelsThread] = None

        self.init_ui()
        self.load_config()

        # Auto-fetch models on init
        self.refresh_models()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Header
        header = QLabel("🤖 Ollama Configuration")
        header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #14b8a6;")
        layout.addWidget(header)

        # Description
        desc = QLabel(
            "Omnix uses Ollama for local AI inference. No API keys required!\n"
            "Just install Ollama and pull a model to get started."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 10pt; color: #9ca3af; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Ollama Configuration Group
        ollama_group = QGroupBox("Ollama Settings")
        ollama_layout = QVBoxLayout()

        # Host URL
        host_label = QLabel("Ollama Host URL:")
        host_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        ollama_layout.addWidget(host_label)

        host_help = QLabel(
            "Default: http://localhost:11434 (local). Can point to remote Ollama instances."
        )
        host_help.setStyleSheet("font-size: 9pt; color: #9ca3af;")
        ollama_layout.addWidget(host_help)

        self.host_input = QLineEdit()
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
            QLineEdit:focus {
                border-color: #14b8a6;
            }
        """)
        ollama_layout.addWidget(self.host_input)

        ollama_layout.addSpacing(15)

        # Model Selection
        model_label = QLabel("Default Model:")
        model_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        ollama_layout.addWidget(model_label)

        model_help = QLabel(
            "Select a model from your Ollama installation, or type a model name."
        )
        model_help.setStyleSheet("font-size: 9pt; color: #9ca3af;")
        ollama_layout.addWidget(model_help)

        model_row = QHBoxLayout()

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 10pt;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #14b8a6;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #14b8a6;
            }
        """)
        model_row.addWidget(self.model_combo, stretch=1)

        self.refresh_btn = QPushButton("🔄 Refresh Models")
        self.refresh_btn.clicked.connect(self.refresh_models)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:disabled {
                background-color: #1f2937;
                color: #6b7280;
            }
        """)
        model_row.addWidget(self.refresh_btn)

        ollama_layout.addLayout(model_row)

        ollama_layout.addSpacing(15)

        # Test Connection
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
                color: #6b7280;
            }
        """)
        test_row.addWidget(self.test_btn)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 10pt;")
        test_row.addWidget(self.status_label, stretch=1)

        ollama_layout.addLayout(test_row)

        ollama_group.setLayout(ollama_layout)
        ollama_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #1e1e1e;
            }
            QGroupBox::title {
                color: #14b8a6;
                font-weight: bold;
            }
        """)
        layout.addWidget(ollama_group)

        # Help Section
        help_group = QGroupBox("Getting Started")
        help_layout = QVBoxLayout()

        help_text = QLabel(
            "<b>Step 1:</b> Install Ollama from <a href='https://ollama.com' style='color: #14b8a6;'>ollama.com</a><br><br>"
            "<b>Step 2:</b> Pull a model (in terminal):<br>"
            "<code style='background-color: #2a2a2a; padding: 2px 6px;'>ollama pull llama3</code><br><br>"
            "<b>Step 3:</b> Make sure Ollama is running, then test the connection above.<br><br>"
            "<b>Popular Models:</b> llama3, mistral, codellama, gemma2, phi3"
        )
        help_text.setWordWrap(True)
        help_text.setOpenExternalLinks(True)
        help_text.setStyleSheet("font-size: 10pt; line-height: 1.6;")
        help_layout.addWidget(help_text)

        # Quick links
        links_row = QHBoxLayout()

        ollama_link = QPushButton("📥 Get Ollama")
        ollama_link.clicked.connect(lambda: webbrowser.open("https://ollama.com"))
        ollama_link.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        links_row.addWidget(ollama_link)

        models_link = QPushButton("📚 Browse Models")
        models_link.clicked.connect(
            lambda: webbrowser.open("https://ollama.com/library")
        )
        models_link.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        links_row.addWidget(models_link)

        links_row.addStretch()
        help_layout.addLayout(links_row)

        help_group.setLayout(help_layout)
        help_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #1e1e1e;
            }
            QGroupBox::title {
                color: #9ca3af;
                font-weight: bold;
            }
        """)
        layout.addWidget(help_group)

        layout.addStretch()

        self.setLayout(layout)

    def load_config(self):
        """Load current configuration into UI"""
        self.host_input.setText(self.config.ollama_host or "http://localhost:11434")
        self.model_combo.setCurrentText(self.config.ollama_model or "llama3")

    def load_current_config(self):
        """Alias for load_config for compatibility"""
        self.load_config()

    def get_config(self) -> dict:
        """Get current configuration from UI"""
        return {
            "ollama_host": self.host_input.text().strip() or "http://localhost:11434",
            "ollama_model": self.model_combo.currentText().strip() or "llama3",
        }

    def get_provider_config(self) -> tuple:
        """Get provider config for compatibility - returns (provider, credentials)"""
        return ("ollama", {})

    def apply_config(self):
        """Apply configuration changes"""
        config_values = self.get_config()
        self.config.ollama_host = config_values["ollama_host"]
        self.config.ollama_model = config_values["ollama_model"]
        self.config_changed.emit(config_values)
        logger.info(
            f"Applied Ollama config: host={config_values['ollama_host']}, model={config_values['ollama_model']}"
        )

    def save_provider_config(self) -> bool:
        """Save provider configuration"""
        try:
            config_values = self.get_config()
            self.config.ollama_host = config_values["ollama_host"]
            self.config.ollama_model = config_values["ollama_model"]

            # Save to .env file
            try:
                Config.save_to_env(
                    ollama_host=config_values["ollama_host"],
                    ollama_model=config_values["ollama_model"],
                    overlay_hotkey=self.config.overlay_hotkey,
                    check_interval=self.config.check_interval,
                )
                logger.info("Configuration saved to .env file")
            except Exception as save_error:
                logger.warning(f"Failed to save to .env: {save_error}")

            self.config_changed.emit(config_values)
            self.provider_config_changed.emit("ollama", {})

            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Save Failed", f"Failed to save configuration:\n{str(e)}"
            )
            return False

    def test_connection(self):
        """Test connection to Ollama"""
        base_url = self.host_input.text().strip() or "http://localhost:11434"

        self.test_btn.setEnabled(False)
        self.status_label.setText("Testing connection...")
        self.status_label.setStyleSheet("font-size: 10pt; color: #fbbf24;")

        # Stop any existing test
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

        if success:
            self.status_label.setText("✅ Connected!")
            self.status_label.setStyleSheet(
                "font-size: 10pt; color: #10b981; font-weight: bold;"
            )
            # Also refresh models on successful connection
            self.refresh_models()
        else:
            self.status_label.setText("❌ Failed")
            self.status_label.setStyleSheet(
                "font-size: 10pt; color: #ef4444; font-weight: bold;"
            )
            QMessageBox.warning(self, "Connection Failed", message)

    def refresh_models(self):
        """Refresh the list of available Ollama models"""
        base_url = self.host_input.text().strip() or "http://localhost:11434"

        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("🔄 Loading...")

        # Stop any existing fetch
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait(1000)

        self.fetch_thread = FetchModelsThread(base_url)
        self.fetch_thread.models_fetched.connect(self.on_models_fetched)
        self.fetch_thread.fetch_failed.connect(self.on_fetch_failed)
        self.fetch_thread.finished.connect(self.on_fetch_finished)
        self.fetch_thread.start()

    def refresh_ollama_models(self):
        """Alias for refresh_models for compatibility"""
        self.refresh_models()

    def on_models_fetched(self, models: List[str]):
        """Handle successful model fetch"""
        current = self.model_combo.currentText()
        self.model_combo.clear()

        if models:
            self.model_combo.addItems(models)
            # Restore previous selection if it exists
            if current in models:
                self.model_combo.setCurrentText(current)
            else:
                self.model_combo.setCurrentText(models[0])
        else:
            # No models installed - add placeholder
            self.model_combo.addItem("llama3")
            self.model_combo.setCurrentText("llama3")

    def on_fetch_failed(self, error: str):
        """Handle model fetch failure"""
        logger.warning(f"Model fetch failed: {error}")
        # Keep current model or use default
        if self.model_combo.count() == 0:
            self.model_combo.addItem("llama3")
            self.model_combo.setCurrentText("llama3")

    def on_fetch_finished(self):
        """Handle fetch thread completion"""
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh Models")

    def closeEvent(self, event):
        """Clean up threads on close"""
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.terminate()
            self.test_thread.wait(1000)
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait(1000)
        super().closeEvent(event)
