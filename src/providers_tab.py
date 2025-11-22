"""
AI Providers Tab for Settings Dialog
Allows users to manage API keys, test connections, and select default provider
"""

import logging
import webbrowser
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread

from credential_store import CredentialStore
from provider_tester import ProviderTester
from config import Config

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
            elif self.provider == "ollama":
                success, message = ProviderTester.test_ollama(self.base_url or "http://localhost:11434")
            else:
                success, message = False, f"Unknown provider: {self.provider}"

            self.test_complete.emit(success, message)
        except Exception as e:
            logger.error(f"Connection test thread error: {e}", exc_info=True)
            self.test_complete.emit(False, f"Test failed: {str(e)}")


class FetchOllamaModelsThread(QThread):
    """Background thread for fetching Ollama models"""
    models_fetched = pyqtSignal(list)  # List of model names
    fetch_failed = pyqtSignal(str)  # Error message

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    def run(self):
        """Fetch models in background"""
        try:
            import ollama

            client = ollama.Client(host=self.base_url)
            models_response = client.list()
            models = models_response.get("models", [])
            model_names = [model.get("name", "") for model in models if model.get("name")]

            self.models_fetched.emit(model_names)
        except ImportError:
            self.fetch_failed.emit("Ollama library not installed. Install with: pip install ollama")
        except Exception as e:
            logger.debug(f"Failed to fetch Ollama models: {e}")
            self.fetch_failed.emit(str(e))


class ProvidersTab(QWidget):
    """Tab for managing AI provider API keys and settings"""

    # Signal emitted when provider configuration changes
    provider_config_changed = pyqtSignal(str, dict)  # default_provider, credentials_dict

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.credential_store = CredentialStore()
        self.test_threads = {}
        self.fetch_models_thread = None
        self.provider_base_urls = {
            'openai': None,
            'ollama': self.config.ollama_host,
        }

        # Track current keys (masked display vs. actual values)
        self.current_keys = {
            'openai': config.openai_api_key or '',
            'anthropic': config.anthropic_api_key or '',
            'gemini': config.gemini_api_key or '',
            'ollama': config.ollama_api_key or ''
        }

        # Track modified keys (only if user enters new value)
        self.modified_keys = {
            'openai': None,
            'anthropic': None,
            'gemini': None,
            'ollama': None
        }

        self.ollama_host = config.ollama_host

        self.init_ui()
        self.load_current_config()

        # Automatically fetch Ollama models on initialization
        self.auto_fetch_ollama_models()

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
        self.provider_combo.addItem("Ollama (Local)", "ollama")
        self.provider_combo.setStyleSheet("""
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
        """)
        default_layout.addWidget(self.provider_combo)

        default_group.setLayout(default_layout)
        layout.addWidget(default_group)

        layout.addSpacing(20)

        # Provider configuration sections
        self.provider_sections = {}

        # OpenAI
        openai_section = self.create_provider_section(
            'openai',
            'OpenAI (GPT)',
            'sk-...',
            'https://platform.openai.com/api-keys',
            supports_custom_url=True
        )
        layout.addWidget(openai_section)

        # Anthropic
        anthropic_section = self.create_provider_section(
            'anthropic',
            'Anthropic (Claude)',
            'sk-ant-...',
            'https://console.anthropic.com/settings/keys'
        )
        layout.addWidget(anthropic_section)

        # Gemini
        gemini_section = self.create_provider_section(
            'gemini',
            'Google Gemini',
            'AIza...',
            'https://aistudio.google.com/app/apikey'
        )
        layout.addWidget(gemini_section)

        # Ollama
        ollama_section = self.create_provider_section(
            'ollama',
            'Ollama (Local or Remote)',
            'Not required',
            'https://ollama.com',
            supports_custom_url=True,
            key_optional=True,
            default_base_url=self.ollama_host
        )

        # Add model selector to Ollama section
        ollama_layout = ollama_section.layout()
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))

        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.addItem(self.config.ollama_model or "llama3")
        self.ollama_model_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 6px;
                font-size: 10pt;
            }
        """)
        model_layout.addWidget(self.ollama_model_combo, stretch=3)

        # Refresh models button
        refresh_button = QPushButton("🔄 Refresh Models")
        refresh_button.clicked.connect(self.refresh_ollama_models)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 3px;
                padding: 5px 10px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        model_layout.addWidget(refresh_button)

        # Insert model selector before action buttons
        ollama_layout.insertLayout(ollama_layout.count() - 1, model_layout)

        layout.addWidget(ollama_section)

        layout.addStretch()

        # Action buttons
        button_layout = QHBoxLayout()

        # Re-run setup wizard button
        wizard_button = QPushButton("🔄 Re-run Setup Wizard")
        wizard_button.clicked.connect(self.open_setup_wizard)
        wizard_button.setStyleSheet("""
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
        """)
        button_layout.addWidget(wizard_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_provider_section(self, provider_id: str, name: str, placeholder: str,
                                 get_key_url: str, supports_custom_url: bool = False,
                                 key_optional: bool = False, default_base_url: Optional[str] = None) -> QGroupBox:
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
        key_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 6px;
                font-size: 10pt;
                font-family: monospace;
            }
        """)
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
        show_button.setStyleSheet("""
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
        """)
        key_layout.addWidget(show_button)

        layout.addLayout(key_layout)

        # Custom URL (for OpenAI)
        base_url_input = None
        if supports_custom_url:
            url_layout = QHBoxLayout()
            url_layout.addWidget(QLabel("Base URL:"))

            base_url_input = QLineEdit()
            if provider_id == 'ollama':
                base_url_input.setPlaceholderText("http://localhost:11434")
            else:
                base_url_input.setPlaceholderText("https://api.openai.com/v1 (leave empty for default)")
            if default_base_url:
                base_url_input.setText(default_base_url)
            base_url_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #3a3a3a;
                    border-radius: 5px;
                    padding: 6px;
                    font-size: 9pt;
                }
            """)
            url_layout.addWidget(base_url_input, stretch=3)
            url_layout.addSpacing(35)  # Align with show button above

            layout.addLayout(url_layout)

        # Action buttons
        action_layout = QHBoxLayout()

        # Get API Key button
        get_key_button = QPushButton("Get API Key →")
        if get_key_url:
            get_key_button.clicked.connect(lambda checked, url=get_key_url: webbrowser.open(url))
        else:
            get_key_button.setEnabled(False)
        get_key_button.setStyleSheet("""
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
        """)
        action_layout.addWidget(get_key_button)

        # Test Connection button
        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(lambda checked, p=provider_id: self.test_connection(p))
        test_button.setStyleSheet("""
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
        """)
        action_layout.addWidget(test_button)

        # Clear Key button
        clear_button = QPushButton("Clear Key")
        clear_button.clicked.connect(lambda checked, p=provider_id: self.clear_key(p))
        clear_button.setStyleSheet("""
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
        """)
        action_layout.addWidget(clear_button)

        action_layout.addStretch()

        layout.addLayout(action_layout)

        group.setLayout(layout)

        # Store references
        self.provider_sections[provider_id] = {
            'group': group,
            'status_label': status_label,
            'key_input': key_input,
            'base_url_input': base_url_input,
            'test_button': test_button,
            'clear_button': clear_button,
            'key_optional': key_optional
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
                section['key_input'].setPlaceholderText(f"Current: {masked} (enter new key to change)")
                section['status_label'].setText("✅ Configured")
                section['status_label'].setStyleSheet("color: #10b981; font-weight: bold;")
            elif section.get('key_optional'):
                section['status_label'].setText("✅ Ready (no key required)")
                section['status_label'].setStyleSheet("color: #10b981; font-weight: bold;")
            else:
                section['status_label'].setText("❌ Not configured")
                section['status_label'].setStyleSheet("color: #ef4444;")

            if section.get('base_url_input') and section['base_url_input'].text().strip() == "" and provider_id == 'ollama':
                section['base_url_input'].setText(self.ollama_host)

    def on_key_changed(self, provider_id: str, text: str):
        """Handle API key text change"""
        text = text.strip()
        if text:
            # User is entering a new key
            self.modified_keys[provider_id] = text

            section = self.provider_sections.get(provider_id)
            if section:
                section['status_label'].setText("⚠️ Modified (not saved)")
                section['status_label'].setStyleSheet("color: #fbbf24;")
        else:
            # User cleared the field
            self.modified_keys[provider_id] = None

    def auto_fetch_ollama_models(self):
        """Automatically fetch Ollama models on initialization (silent)"""
        # Get base URL from config
        base_url = self.ollama_host or "http://localhost:11434"

        # Start background thread
        self.fetch_models_thread = FetchOllamaModelsThread(base_url)
        self.fetch_models_thread.models_fetched.connect(self.on_models_fetched)
        self.fetch_models_thread.fetch_failed.connect(self.on_models_fetch_failed)
        self.fetch_models_thread.start()

        # Update UI to show loading state
        if hasattr(self, 'ollama_model_combo'):
            self.ollama_model_combo.clear()
            self.ollama_model_combo.addItem("Loading models...")
            self.ollama_model_combo.setEnabled(False)

    def refresh_ollama_models(self):
        """Refresh the list of available Ollama models (user-triggered)"""
        # Get base URL from input or use default
        base_url = self.provider_sections.get('ollama', {}).get('base_url_input')
        if base_url:
            base_url = base_url.text().strip() or self.ollama_host
        else:
            base_url = self.ollama_host

        # Update UI to show loading state
        current_model = self.ollama_model_combo.currentText()
        self.ollama_model_combo.clear()
        self.ollama_model_combo.addItem("🔄 Refreshing...")
        self.ollama_model_combo.setEnabled(False)

        # Start background thread
        if self.fetch_models_thread and self.fetch_models_thread.isRunning():
            self.fetch_models_thread.wait()

        self.fetch_models_thread = FetchOllamaModelsThread(base_url)
        self.fetch_models_thread.models_fetched.connect(
            lambda models: self.on_models_fetched(models, show_message=True)
        )
        self.fetch_models_thread.fetch_failed.connect(
            lambda error: self.on_models_fetch_failed(error, show_message=True)
        )
        self.fetch_models_thread.start()

    def on_models_fetched(self, model_names: list, show_message: bool = False):
        """Handle successful model fetching"""
        # Get current selection before clearing
        current_model = self.config.ollama_model or "llama3"

        # Clear and repopulate combo box
        self.ollama_model_combo.clear()
        self.ollama_model_combo.setEnabled(True)

        if model_names:
            for model_name in model_names:
                self.ollama_model_combo.addItem(model_name)

            # Try to restore previous selection
            index = self.ollama_model_combo.findText(current_model)
            if index >= 0:
                self.ollama_model_combo.setCurrentIndex(index)
            else:
                # If current model not found, select first one
                self.ollama_model_combo.setCurrentIndex(0)

            if show_message:
                QMessageBox.information(
                    self,
                    "Models Refreshed",
                    f"Found {len(model_names)} Ollama models:\n\n" + "\n".join(model_names)
                )
        else:
            # No models found
            self.ollama_model_combo.addItem(current_model)
            if show_message:
                QMessageBox.information(
                    self,
                    "No Models Found",
                    "No models found. You may need to pull a model first:\n\n"
                    "ollama pull llama3"
                )

        logger.info(f"Loaded {len(model_names)} Ollama models")

    def on_models_fetch_failed(self, error: str, show_message: bool = False):
        """Handle failed model fetching"""
        # Restore to default
        current_model = self.config.ollama_model or "llama3"
        self.ollama_model_combo.clear()
        self.ollama_model_combo.addItem(current_model)
        self.ollama_model_combo.setEnabled(True)

        logger.debug(f"Failed to fetch Ollama models: {error}")

        if show_message:
            if "not installed" in error.lower():
                QMessageBox.warning(
                    self,
                    "Ollama Not Installed",
                    f"The Ollama library is not installed. Please install it with:\n\n"
                    f"pip install ollama"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Refresh Failed",
                    f"Failed to refresh Ollama models:\n\n{error}"
                )

    def test_connection(self, provider_id: str):
        """Test connection for a provider"""
        # Use modified key if available, otherwise use current key
        api_key = self.modified_keys.get(provider_id) or self.current_keys.get(provider_id, '')

        if not api_key or not api_key.strip():
            section = self.provider_sections.get(provider_id)
            key_optional = section.get('key_optional') if section else False
            if not key_optional:
                QMessageBox.warning(self, "Missing API Key", f"Please enter an API key for {provider_id.title()} first.")
                return

        section = self.provider_sections.get(provider_id)
        if not section:
            return

        # Disable button and show testing message
        test_button = section['test_button']
        status_label = section['status_label']

        test_button.setEnabled(False)
        status_label.setText("🔄 Testing...")
        status_label.setStyleSheet("color: #fbbf24;")

        # Get base URL if applicable
        base_url = None
        if section['base_url_input']:
            base_url = section['base_url_input'].text().strip() or None
            if provider_id == 'ollama':
                self.provider_base_urls['ollama'] = base_url or self.ollama_host

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
        section['test_button'].setEnabled(True)

        # Update status
        if success:
            section['status_label'].setText("✅ Connected")
            section['status_label'].setStyleSheet("color: #10b981; font-weight: bold;")

            # Show success message
            QMessageBox.information(self, "Connection Successful", message)
        else:
            section['status_label'].setText("❌ Connection Failed")
            section['status_label'].setStyleSheet("color: #ef4444; font-weight: bold;")

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
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete from credential store
                if provider_id == 'openai':
                    self.credential_store.delete('OPENAI_API_KEY')
                elif provider_id == 'anthropic':
                    self.credential_store.delete('ANTHROPIC_API_KEY')
                elif provider_id == 'gemini':
                    self.credential_store.delete('GEMINI_API_KEY')
                elif provider_id == 'ollama':
                    self.credential_store.delete('OLLAMA_API_KEY')
                    self.provider_base_urls['ollama'] = 'http://localhost:11434'
                    self.ollama_host = 'http://localhost:11434'

                # Update local state
                self.current_keys[provider_id] = ''
                self.modified_keys[provider_id] = None

                # Update UI
                section = self.provider_sections.get(provider_id)
                if section:
                    section['key_input'].clear()
                    section['key_input'].setPlaceholderText("Enter API key...")
                    if section.get('key_optional'):
                        section['status_label'].setText("✅ Ready (no key required)")
                        section['status_label'].setStyleSheet("color: #10b981; font-weight: bold;")
                    else:
                        section['status_label'].setText("❌ Not configured")
                        section['status_label'].setStyleSheet("color: #ef4444;")

                QMessageBox.information(
                    self,
                    "Key Cleared",
                    f"API key for {provider_id.title()} has been removed."
                )

                logger.info(f"Cleared API key for {provider_id}")

            except Exception as e:
                logger.error(f"Failed to clear key for {provider_id}: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to clear API key:\n{str(e)}"
                )

    def open_setup_wizard(self):
        """Open the setup wizard"""
        from setup_wizard import SetupWizard

        wizard = SetupWizard(self)
        wizard.setup_complete.connect(self.on_wizard_complete)
        wizard.exec()

    def on_wizard_complete(self, default_provider: str, credentials: Dict[str, str]):
        """Handle wizard completion"""
        # Reload configuration
        for provider_id in ['openai', 'anthropic', 'gemini', 'ollama']:
            key_name = f'{provider_id.upper()}_API_KEY'
            if key_name in credentials:
                self.current_keys[provider_id] = credentials[key_name]
            else:
                self.current_keys[provider_id] = ''

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
                if provider_id == 'openai':
                    credentials['OPENAI_API_KEY'] = new_key
                elif provider_id == 'anthropic':
                    credentials['ANTHROPIC_API_KEY'] = new_key
                elif provider_id == 'gemini':
                    credentials['GEMINI_API_KEY'] = new_key
                elif provider_id == 'ollama':
                    credentials['OLLAMA_API_KEY'] = new_key

        return default_provider, credentials

    def save_provider_config(self) -> bool:
        """
        Save provider configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            default_provider, credentials = self.get_provider_config()

            # Track if restart is needed
            provider_changed = default_provider != self.config.ai_provider
            credentials_modified = any(self.modified_keys.values())

            # Update AI provider in config
            if provider_changed:
                self.config.ai_provider = default_provider
                logger.info(f"Updated default AI provider to: {default_provider}")

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

            # Persist base URLs for providers that support them
            ollama_section = self.provider_sections.get('ollama')
            if ollama_section and ollama_section.get('base_url_input'):
                host_value = ollama_section['base_url_input'].text().strip() or self.ollama_host
                self.config.ollama_host = host_value
                self.provider_base_urls['ollama'] = host_value

            # Save Ollama model selection
            if hasattr(self, 'ollama_model_combo'):
                ollama_model = self.ollama_model_combo.currentText().strip()
                if ollama_model:
                    self.config.ollama_model = ollama_model

            # Persist configuration to .env file
            try:
                from config import Config
                Config.save_to_env(
                    provider=self.config.ai_provider,
                    session_tokens=self.config.session_tokens,
                    overlay_hotkey=self.config.overlay_hotkey,
                    check_interval=self.config.check_interval,
                    overlay_x=self.config.overlay_x,
                    overlay_y=self.config.overlay_y,
                    overlay_width=self.config.overlay_width,
                    overlay_height=self.config.overlay_height,
                    overlay_minimized=self.config.overlay_minimized,
                    overlay_opacity=self.config.overlay_opacity
                )
                logger.info("Configuration persisted to .env file")
            except Exception as save_error:
                logger.warning(f"Failed to save to .env: {save_error}")

            # Emit signal
            self.provider_config_changed.emit(default_provider, credentials)

            # Show restart notification if provider or credentials changed
            if provider_changed or credentials_modified:
                QMessageBox.information(
                    self,
                    "Restart Required",
                    "Your settings have been saved successfully!\n\n"
                    "⚠️  Please restart the application for the changes to take effect.\n\n"
                    "The new AI provider configuration will be used after restarting."
                )

            return True

        except Exception as e:
            logger.error(f"Failed to save provider config: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save provider configuration:\n{str(e)}"
            )
            return False
