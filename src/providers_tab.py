"""
AI Providers Tab for Settings Dialog
Allows users to manage API keys, test connections, and select default provider
"""

import logging
import webbrowser
from typing import Dict, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal  # noqa: F401
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import Config
from credential_store import CredentialStore
from provider_tester import ProviderTester

logger = logging.getLogger(__name__)


class TestConnectionThread(QThread):
    """Background thread for testing API connections"""

    test_complete = pyqtSignal(bool, str)  # success, message

    def __init__(self, provider: str, api_key: str, base_url: Optional[str] = None):
        super().__init__()
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url

    def run(self):
        """Run connection test in background"""
        try:
            if self.provider == "openai":
                success, message = ProviderTester.test_openai(self.api_key, self.base_url)
            elif self.provider == "anthropic":
                success, message = ProviderTester.test_anthropic(self.api_key)
            elif self.provider == "gemini":
                success, message = ProviderTester.test_gemini(self.api_key)
            else:
                success, message = False, f"Unknown provider: {self.provider}"

            self.test_complete.emit(success, message)
        except Exception as e:
            logger.error(f"Connection test thread error: {e}", exc_info=True)
            self.test_complete.emit(False, f"Test failed: {str(e)}")


class ProvidersTab(QWidget):
    """Tab for managing AI provider API keys and settings"""

    # Signal emitted when provider configuration changes
    provider_config_changed = pyqtSignal(str, dict)  # default_provider, credentials_dict

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.credential_store = CredentialStore()
        self.test_threads = {}

        # Track current keys (masked display vs. actual values)
        self.current_keys = {
            "openai": config.openai_api_key or "",
            "anthropic": config.anthropic_api_key or "",
            "gemini": config.gemini_api_key or "",
        }

        # Track modified keys (only if user enters new value)
        self.modified_keys = {"openai": None, "anthropic": None, "gemini": None}

        self.init_ui()
        self.load_current_config()

    def init_ui(self):
        """Initialize the providers tab UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🔑 AI Provider Configuration")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #14b8a6;")
        layout.addWidget(title)

        layout.addSpacing(10)

        # Instructions
        instructions = QLabel(
            "Manage your AI provider API keys. Your keys are stored securely and encrypted on your PC."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 10pt; color: #9ca3af;")
        layout.addWidget(instructions)

        layout.addSpacing(20)

        # Default provider selector
        default_group = QGroupBox("Default AI Provider")
        default_layout = QVBoxLayout()

        help_text = QLabel("Select which AI provider to use by default:")
        help_text.setStyleSheet("font-size: 10pt;")
        default_layout.addWidget(help_text)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("Anthropic (Claude)", "anthropic")
        self.provider_combo.addItem("OpenAI (GPT)", "openai")
        self.provider_combo.addItem("Google Gemini", "gemini")
        self.provider_combo.setStyleSheet(
            """
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #ffffff;
                width: 6px;
                height: 6px;
                border-top: none;
                border-left: none;
                margin-right: 8px;
            }
        """
        )
        default_layout.addWidget(self.provider_combo)

        default_group.setLayout(default_layout)
        layout.addWidget(default_group)

        layout.addSpacing(20)

        # Provider configuration sections
        self.provider_sections = {}

        # OpenAI
        openai_section = self.create_provider_section(
            "openai",
            "OpenAI (GPT)",
            "sk-...",
            "https://platform.openai.com/api-keys",
            supports_custom_url=True,
        )
        layout.addWidget(openai_section)

        # Anthropic
        anthropic_section = self.create_provider_section(
            "anthropic",
            "Anthropic (Claude)",
            "sk-ant-...",
            "https://console.anthropic.com/settings/keys",
        )
        layout.addWidget(anthropic_section)

        # Gemini
        gemini_section = self.create_provider_section(
            "gemini", "Google Gemini", "AIza...", "https://aistudio.google.com/app/apikey"
        )
        layout.addWidget(gemini_section)

        layout.addStretch()

        # Action buttons
        button_layout = QHBoxLayout()

        # Re-run setup wizard button
        wizard_button = QPushButton("🔄 Re-run Setup Wizard")
        wizard_button.clicked.connect(self.open_setup_wizard)
        wizard_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """
        )
        button_layout.addWidget(wizard_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_provider_section(
        self,
        provider_id: str,
        name: str,
        placeholder: str,
        get_key_url: str,
        supports_custom_url: bool = False,
    ) -> QGroupBox:
        """Create a provider configuration section"""
        group = QGroupBox(name)
        layout = QVBoxLayout()

        # Status display
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))

        status_label = QLabel("Not configured")
        status_label.setStyleSheet("color: #9ca3af;")
        status_layout.addWidget(status_label)
        status_layout.addStretch()

        layout.addLayout(status_layout)

        # API Key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))

        key_input = QLineEdit()
        key_input.setPlaceholderText(placeholder)
        key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_input.textChanged.connect(lambda text, p=provider_id: self.on_key_changed(p, text))
        key_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 6px;
                font-size: 10pt;
                font-family: monospace;
            }
        """
        )
        key_layout.addWidget(key_input, stretch=3)

        # Show/hide toggle
        show_button = QPushButton("👁")
        show_button.setCheckable(True)
        show_button.setFixedWidth(35)
        show_button.toggled.connect(
            lambda checked, inp=key_input: inp.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        show_button.setStyleSheet(
            """
            QPushButton {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 3px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:checked {
                background-color: #14b8a6;
            }
        """
        )
        key_layout.addWidget(show_button)

        layout.addLayout(key_layout)

        # Custom URL (for OpenAI)
        base_url_input = None
        if supports_custom_url:
            url_layout = QHBoxLayout()
            url_layout.addWidget(QLabel("Base URL:"))

            base_url_input = QLineEdit()
            base_url_input.setPlaceholderText("https://api.openai.com/v1 (leave empty for default)")
            base_url_input.setStyleSheet(
                """
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #3a3a3a;
                    border-radius: 5px;
                    padding: 6px;
                    font-size: 9pt;
                }
            """
            )
            url_layout.addWidget(base_url_input, stretch=3)
            url_layout.addSpacing(35)  # Align with show button above

            layout.addLayout(url_layout)

        # Action buttons
        action_layout = QHBoxLayout()

        # Get API Key button
        get_key_button = QPushButton("Get API Key →")
        get_key_button.clicked.connect(lambda checked, url=get_key_url: webbrowser.open(url))
        get_key_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """
        )
        action_layout.addWidget(get_key_button)

        # Test Connection button
        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(lambda checked, p=provider_id: self.test_connection(p))
        test_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14b8a6;
            }
            QPushButton:disabled {
                background-color: #374151;
                color: #6b7280;
            }
        """
        )
        action_layout.addWidget(test_button)

        # Clear Key button
        clear_button = QPushButton("Clear Key")
        clear_button.clicked.connect(lambda checked, p=provider_id: self.clear_key(p))
        clear_button.setStyleSheet(
            """
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
        """
        )
        action_layout.addWidget(clear_button)

        action_layout.addStretch()

        layout.addLayout(action_layout)

        group.setLayout(layout)

        # Store references
        self.provider_sections[provider_id] = {
            "group": group,
            "status_label": status_label,
            "key_input": key_input,
            "base_url_input": base_url_input,
            "test_button": test_button,
            "clear_button": clear_button,
        }

        return group

    def load_current_config(self):
        """Load current configuration into the UI"""
        # Set default provider
        current_provider = self.config.ai_provider
        index = self.provider_combo.findData(current_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        # Load API keys (show masked if they exist)
        for provider_id, key in self.current_keys.items():
            section = self.provider_sections.get(provider_id)
            if not section:
                continue

            if key:
                # Show masked version
                masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                section["key_input"].setPlaceholderText(
                    f"Current: {masked} (enter new key to change)"
                )
                section["status_label"].setText("✅ Configured")
                section["status_label"].setStyleSheet("color: #10b981; font-weight: bold;")
            else:
                section["status_label"].setText("❌ Not configured")
                section["status_label"].setStyleSheet("color: #ef4444;")

    def on_key_changed(self, provider_id: str, text: str):
        """Handle API key text change"""
        text = text.strip()
        if text:
            # User is entering a new key
            self.modified_keys[provider_id] = text

            section = self.provider_sections.get(provider_id)
            if section:
                section["status_label"].setText("⚠️ Modified (not saved)")
                section["status_label"].setStyleSheet("color: #fbbf24;")
        else:
            # User cleared the field
            self.modified_keys[provider_id] = None

    def test_connection(self, provider_id: str):
        """Test connection for a provider"""
        # Use modified key if available, otherwise use current key
        api_key = self.modified_keys.get(provider_id) or self.current_keys.get(provider_id, "")

        if not api_key or not api_key.strip():
            QMessageBox.warning(
                self, "Missing API Key", f"Please enter an API key for {provider_id.title()} first."
            )
            return

        section = self.provider_sections.get(provider_id)
        if not section:
            return

        # Disable button and show testing message
        test_button = section["test_button"]
        status_label = section["status_label"]

        test_button.setEnabled(False)
        status_label.setText("🔄 Testing...")
        status_label.setStyleSheet("color: #fbbf24;")

        # Get base URL if applicable
        base_url = None
        if section["base_url_input"]:
            base_url = section["base_url_input"].text().strip() or None

        # Start test thread
        thread = TestConnectionThread(provider_id, api_key, base_url)
        thread.test_complete.connect(
            lambda success, message, p=provider_id: self.on_test_complete(p, success, message)
        )
        thread.start()
        self.test_threads[provider_id] = thread

    def on_test_complete(self, provider_id: str, success: bool, message: str):
        """Handle test completion"""
        section = self.provider_sections.get(provider_id)
        if not section:
            return

        # Re-enable button
        section["test_button"].setEnabled(True)

        # Update status
        if success:
            section["status_label"].setText("✅ Connected")
            section["status_label"].setStyleSheet("color: #10b981; font-weight: bold;")

            # Show success message
            QMessageBox.information(self, "Connection Successful", message)
        else:
            section["status_label"].setText("❌ Connection Failed")
            section["status_label"].setStyleSheet("color: #ef4444; font-weight: bold;")

            # Show error message
            QMessageBox.warning(self, "Connection Failed", message)

        # Clean up thread
        if provider_id in self.test_threads:
            del self.test_threads[provider_id]

    def clear_key(self, provider_id: str):
        """Clear API key for a provider"""
        reply = QMessageBox.question(
            self,
            "Clear API Key",
            f"Are you sure you want to remove the API key for {provider_id.title()}?\n\n"
            f"This will delete the key from secure storage.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete from credential store
                if provider_id == "openai":
                    self.credential_store.delete("OPENAI_API_KEY")
                elif provider_id == "anthropic":
                    self.credential_store.delete("ANTHROPIC_API_KEY")
                elif provider_id == "gemini":
                    self.credential_store.delete("GEMINI_API_KEY")

                # Update local state
                self.current_keys[provider_id] = ""
                self.modified_keys[provider_id] = None

                # Update UI
                section = self.provider_sections.get(provider_id)
                if section:
                    section["key_input"].clear()
                    section["key_input"].setPlaceholderText("Enter API key...")
                    section["status_label"].setText("❌ Not configured")
                    section["status_label"].setStyleSheet("color: #ef4444;")

                QMessageBox.information(
                    self, "Key Cleared", f"API key for {provider_id.title()} has been removed."
                )

                logger.info(f"Cleared API key for {provider_id}")

            except Exception as e:
                logger.error(f"Failed to clear key for {provider_id}: {e}")
                QMessageBox.critical(self, "Error", f"Failed to clear API key:\n{str(e)}")

    def open_setup_wizard(self):
        """Open the setup wizard"""
        from setup_wizard import SetupWizard

        wizard = SetupWizard(self)
        wizard.setup_complete.connect(self.on_wizard_complete)
        wizard.exec()

    def on_wizard_complete(self, default_provider: str, credentials: Dict[str, str]):
        """Handle wizard completion"""
        # Reload configuration
        for provider_id in ["openai", "anthropic", "gemini"]:
            key_name = f"{provider_id.upper()}_API_KEY"
            if key_name in credentials:
                self.current_keys[provider_id] = credentials[key_name]
            else:
                self.current_keys[provider_id] = ""

        # Reload UI
        self.load_current_config()

        # Update default provider
        index = self.provider_combo.findData(default_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

    def get_provider_config(self) -> tuple:
        """
        Get current provider configuration

        Returns:
            Tuple of (default_provider, credentials_dict)
        """
        # Get default provider
        default_provider = self.provider_combo.currentData()

        # Build credentials dict with only modified keys
        credentials = {}
        for provider_id, new_key in self.modified_keys.items():
            if new_key:  # Only include if user entered a new key
                if provider_id == "openai":
                    credentials["OPENAI_API_KEY"] = new_key
                elif provider_id == "anthropic":
                    credentials["ANTHROPIC_API_KEY"] = new_key
                elif provider_id == "gemini":
                    credentials["GEMINI_API_KEY"] = new_key

        return default_provider, credentials

    def save_provider_config(self) -> bool:
        """
        Save provider configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            default_provider, credentials = self.get_provider_config()

            # Save credentials using config.set_api_key() which updates both
            # the config object AND the credential store
            if self.modified_keys:
                saved_count = 0
                for provider_id, new_key in self.modified_keys.items():
                    if new_key:
                        # Update config object and credential store
                        self.config.set_api_key(provider_id, new_key)

                        # Update local tracking
                        self.current_keys[provider_id] = new_key
                        self.modified_keys[provider_id] = None
                        saved_count += 1

                if saved_count > 0:
                    logger.info(f"Saved {saved_count} modified credentials")

                    # Reload UI to show new masked keys
                    self.load_current_config()

            # Emit signal
            self.provider_config_changed.emit(default_provider, credentials)

            return True

        except Exception as e:
            logger.error(f"Failed to save provider config: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Save Failed", f"Failed to save provider configuration:\n{str(e)}"
            )
            return False
