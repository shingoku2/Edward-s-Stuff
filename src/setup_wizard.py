"""
First-Run Setup Wizard
Guides users through initial API key configuration
"""

import logging
import webbrowser
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QWidget, QTextEdit, QMessageBox,
    QFrame, QStackedWidget, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from credential_store import CredentialStore
from provider_tester import ProviderTester

logger = logging.getLogger(__name__)


class TestConnectionThread(QThread):
    """Background thread for testing API connections"""
    test_complete = pyqtSignal(bool, str)  # success, message

    def __init__(self, provider: str, api_key: str, base_url: Optional[str] = None, timeout: float = 15.0):
        super().__init__()
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    def run(self):
        """Run connection test in background"""
        try:
            if self.isInterruptionRequested():
                return

            if self.provider == "openai":
                success, message = ProviderTester.test_openai(self.api_key, self.base_url, timeout=self.timeout)
            elif self.provider == "anthropic":
                success, message = ProviderTester.test_anthropic(self.api_key, timeout=self.timeout)
            elif self.provider == "gemini":
                success, message = ProviderTester.test_gemini(self.api_key, timeout=self.timeout)
            else:
                success, message = False, f"Unknown provider: {self.provider}"

            self.test_complete.emit(success, message)
        except Exception as e:
            logger.error(f"Connection test thread error: {e}", exc_info=True)
            self.test_complete.emit(False, f"Test failed: {str(e)}")


class SetupWizard(QDialog):
    """First-run setup wizard for API key configuration"""

    # Signal emitted when setup is complete
    setup_complete = pyqtSignal(str, dict)  # provider, credentials_dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.credential_store = CredentialStore()
        self.test_thread = None
        self.connection_timeout = ProviderTester.DEFAULT_TIMEOUT

        # Track which providers are enabled and their keys
        self.provider_enabled = {
            'openai': False,
            'anthropic': False,
            'gemini': False
        }
        self.provider_keys = {
            'openai': '',
            'anthropic': '',
            'gemini': ''
        }
        self.provider_base_urls = {
            'openai': ''
        }
        self.provider_tested = {
            'openai': False,
            'anthropic': False,
            'gemini': False
        }

        self.default_provider = 'anthropic'  # Default to Anthropic (Claude)

        self.init_ui()

    def init_ui(self):
        """Initialize the wizard UI"""
        self.setWindowTitle("Gaming AI Assistant - Setup Wizard")
        self.setMinimumSize(700, 600)
        self.setModal(True)

        layout = QVBoxLayout()

        # Stacked widget for wizard pages
        self.pages = QStackedWidget()

        # Create wizard pages
        self.create_welcome_page()
        self.create_provider_selection_page()
        self.create_key_input_page()
        self.create_confirmation_page()

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

        # Apply dark theme
        self.apply_theme()

        # Start on welcome page
        self.update_navigation()

    def create_welcome_page(self):
        """Create the welcome/introduction page"""
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

        # Introduction text
        intro = QLabel(
            "<h3>How It Works</h3>"
            "<p>This assistant uses <b>your own API keys</b> to connect to AI providers like "
            "OpenAI (GPT), Anthropic (Claude), or Google (Gemini).</p>"
            "<br>"
            "<h3>Your Privacy Matters</h3>"
            "<p>✓ Your API keys stay <b>encrypted on your PC</b></p>"
            "<p>✓ Keys are <b>never sent to any server we control</b></p>"
            "<p>✓ You connect directly to your chosen AI provider</p>"
            "<br>"
            "<h3>Provider Differences</h3>"
            "<p><b>Anthropic Claude:</b> Great balance of speed and quality (Recommended)</p>"
            "<p><b>OpenAI GPT:</b> Popular and powerful, supports custom endpoints</p>"
            "<p><b>Google Gemini:</b> Fast and efficient Google AI</p>"
            "<br>"
            "<p>Don't worry - you can change providers later in Settings!</p>"
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("font-size: 11pt; line-height: 1.5;")
        layout.addWidget(intro)

        layout.addStretch()

        page.setLayout(layout)
        self.pages.addWidget(page)

    def create_provider_selection_page(self):
        """Create provider selection page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Select AI Providers")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addSpacing(20)

        # Instructions
        instructions = QLabel(
            "Choose which AI providers you want to set up. You can enable one or multiple providers."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11pt;")
        layout.addWidget(instructions)

        layout.addSpacing(20)

        # Provider checkboxes
        self.provider_checkboxes = {}

        # OpenAI
        openai_group = self.create_provider_checkbox(
            'openai',
            'OpenAI (GPT)',
            'Popular and powerful AI. Supports custom endpoints for local models.',
            'https://platform.openai.com/api-keys'
        )
        layout.addWidget(openai_group)

        # Anthropic
        anthropic_group = self.create_provider_checkbox(
            'anthropic',
            'Anthropic (Claude) - Recommended',
            'Excellent balance of speed, quality, and gaming knowledge.',
            'https://console.anthropic.com/settings/keys'
        )
        layout.addWidget(anthropic_group)

        # Gemini
        gemini_group = self.create_provider_checkbox(
            'gemini',
            'Google Gemini',
            'Fast and efficient Google AI with generous free tier.',
            'https://aistudio.google.com/app/apikey'
        )
        layout.addWidget(gemini_group)

        layout.addStretch()

        # Default selection
        self.provider_checkboxes['anthropic'].setChecked(True)

        page.setLayout(layout)
        self.pages.addWidget(page)

    def create_provider_checkbox(self, provider_id: str, name: str, description: str, url: str) -> QGroupBox:
        """Create a provider checkbox group"""
        group = QGroupBox()
        layout = QVBoxLayout()

        checkbox = QCheckBox(name)
        checkbox.setStyleSheet("font-size: 12pt; font-weight: bold;")
        checkbox.stateChanged.connect(lambda state, p=provider_id: self.on_provider_toggled(p, state))
        self.provider_checkboxes[provider_id] = checkbox
        layout.addWidget(checkbox)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 10pt; color: #9ca3af; margin-left: 25px;")
        layout.addWidget(desc_label)

        # Get API Key button
        button_layout = QHBoxLayout()
        button_layout.addSpacing(25)

        get_key_button = QPushButton(f"Get API Key →")
        get_key_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        get_key_button.clicked.connect(lambda checked, u=url: webbrowser.open(u))
        button_layout.addWidget(get_key_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def create_key_input_page(self):
        """Create API key input page with test buttons"""
        page = QWidget()
        self.key_input_layout = QVBoxLayout()

        # Title
        title = QLabel("Enter API Keys")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        self.key_input_layout.addWidget(title)

        self.key_input_layout.addSpacing(20)

        # Instructions
        instructions = QLabel(
            "Enter your API keys for the selected providers. Click 'Test Connection' to verify each key."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11pt;")
        self.key_input_layout.addWidget(instructions)

        self.key_input_layout.addSpacing(20)

        # Provider key input sections (will be populated dynamically)
        self.key_input_sections = {}

        self.key_input_layout.addStretch()

        page.setLayout(self.key_input_layout)
        self.pages.addWidget(page)

    def create_provider_key_section(self, provider_id: str) -> QWidget:
        """Create a key input section for a provider"""
        section = QWidget()
        layout = QVBoxLayout()

        # Provider name
        if provider_id == 'openai':
            name = "OpenAI (GPT)"
            placeholder = "sk-..."
            help_text = "Your OpenAI API key (starts with 'sk-')"
        elif provider_id == 'anthropic':
            name = "Anthropic (Claude)"
            placeholder = "sk-ant-..."
            help_text = "Your Anthropic API key (starts with 'sk-ant-')"
        elif provider_id == 'gemini':
            name = "Google Gemini"
            placeholder = "AIza..."
            help_text = "Your Gemini API key (starts with 'AIza')"
        else:
            name = provider_id.title()
            placeholder = ""
            help_text = ""

        name_label = QLabel(f"🔑 {name}")
        name_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
        layout.addWidget(name_label)

        help_label = QLabel(help_text)
        help_label.setStyleSheet("font-size: 9pt; color: #9ca3af;")
        layout.addWidget(help_label)

        # API Key input
        key_layout = QHBoxLayout()

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
                padding: 8px;
                font-size: 10pt;
                font-family: monospace;
            }
        """)
        key_layout.addWidget(key_input, stretch=3)

        # Show/hide toggle
        show_button = QPushButton("👁")
        show_button.setCheckable(True)
        show_button.setFixedWidth(40)
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
                padding: 5px;
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

        # OpenAI custom endpoint (optional)
        if provider_id == 'openai':
            base_url_label = QLabel("Custom Base URL (optional, for OpenAI-compatible endpoints):")
            base_url_label.setStyleSheet("font-size: 9pt; color: #9ca3af; margin-top: 5px;")
            layout.addWidget(base_url_label)

            base_url_input = QLineEdit()
            base_url_input.setPlaceholderText("https://api.openai.com/v1")
            base_url_input.textChanged.connect(lambda text, p=provider_id: self.on_base_url_changed(p, text))
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
            layout.addWidget(base_url_input)
            self.key_input_sections[f'{provider_id}_base_url'] = base_url_input

        # Test button and status
        test_layout = QHBoxLayout()

        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(lambda checked, p=provider_id: self.test_provider_connection(p))
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
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
        test_layout.addWidget(test_button)

        status_label = QLabel("")
        status_label.setWordWrap(True)
        status_label.setStyleSheet("font-size: 9pt;")
        test_layout.addWidget(status_label, stretch=1)

        layout.addLayout(test_layout)

        # Store references
        self.key_input_sections[provider_id] = {
            'key_input': key_input,
            'test_button': test_button,
            'status_label': status_label
        }

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3a3a3a;")
        layout.addWidget(separator)

        section.setLayout(layout)
        return section

    def create_confirmation_page(self):
        """Create final confirmation page"""
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

        # Summary
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 15px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.summary_text)

        layout.addSpacing(20)

        # Final instructions
        instructions = QLabel(
            "Click 'Finish & Start Assistant' to begin using the Gaming AI Assistant!\n\n"
            "You can change these settings later in the Settings dialog (⚙️ button)."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("font-size: 11pt;")
        layout.addWidget(instructions)

        page.setLayout(layout)
        self.pages.addWidget(page)

    def on_provider_toggled(self, provider_id: str, state: int):
        """Handle provider checkbox toggle"""
        self.provider_enabled[provider_id] = (state == Qt.CheckState.Checked.value)
        logger.info(f"Provider {provider_id} enabled: {self.provider_enabled[provider_id]}")

    def on_key_changed(self, provider_id: str, text: str):
        """Handle API key text change"""
        self.provider_keys[provider_id] = text.strip()
        # Reset tested status when key changes
        if provider_id in self.provider_tested:
            self.provider_tested[provider_id] = False
            if provider_id in self.key_input_sections:
                self.key_input_sections[provider_id]['status_label'].setText("")

    def on_base_url_changed(self, provider_id: str, text: str):
        """Handle base URL text change"""
        self.provider_base_urls[provider_id] = text.strip()

    def test_provider_connection(self, provider_id: str):
        """Test connection for a specific provider"""
        api_key = self.provider_keys.get(provider_id, '').strip()
        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter an API key first.")
            return

        self._stop_test_thread()

        # Get UI elements
        section = self.key_input_sections.get(provider_id)
        if not section:
            return

        test_button = section['test_button']
        status_label = section['status_label']

        # Disable button and show testing message
        test_button.setEnabled(False)
        status_label.setText("Testing connection...")
        status_label.setStyleSheet("font-size: 9pt; color: #fbbf24;")

        # Get base URL if applicable
        base_url = self.provider_base_urls.get(provider_id, '')

        # Start test thread
        self.test_thread = TestConnectionThread(
            provider_id,
            api_key,
            base_url,
            timeout=self.connection_timeout,
        )
        self.test_thread.test_complete.connect(
            lambda success, message, p=provider_id: self.on_test_complete(p, success, message)
        )
        self.test_thread.finished.connect(self._clear_test_thread)
        self.test_thread.start()

    def on_test_complete(self, provider_id: str, success: bool, message: str):
        """Handle test completion"""
        section = self.key_input_sections.get(provider_id)
        if not section:
            return

        test_button = section['test_button']
        status_label = section['status_label']

        # Re-enable button
        test_button.setEnabled(True)

        # Update status
        self.provider_tested[provider_id] = success
        if success:
            status_label.setText("✅ Connected")
            status_label.setStyleSheet("font-size: 9pt; color: #10b981; font-weight: bold;")
        else:
            status_label.setText("❌ Failed")
            status_label.setStyleSheet("font-size: 9pt; color: #ef4444; font-weight: bold;")

            # Show detailed error in message box
            QMessageBox.warning(self, "Connection Test Failed", message)

        self.update_navigation()

    def _clear_test_thread(self):
        """Clear references to the completed test thread"""
        self.test_thread = None

    def _stop_test_thread(self):
        """Request any running test thread to stop and wait briefly"""
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.requestInterruption()
            self.test_thread.wait(2000)
        self.test_thread = None

    def update_key_input_page(self):
        """Update the key input page based on selected providers"""
        # Clear existing sections
        for key in list(self.key_input_sections.keys()):
            if isinstance(self.key_input_sections[key], dict):
                widget = self.key_input_sections[key]['key_input'].parent()
                if widget:
                    widget.deleteLater()
                del self.key_input_sections[key]

        # Add sections for enabled providers
        for provider_id in ['openai', 'anthropic', 'gemini']:
            if self.provider_enabled[provider_id]:
                section = self.create_provider_key_section(provider_id)
                # Insert before the stretch
                self.key_input_layout.insertWidget(self.key_input_layout.count() - 1, section)

    def update_confirmation_page(self):
        """Update the confirmation page summary"""
        summary_html = "<h3>Configured Providers:</h3><ul>"

        configured_count = 0
        first_working_provider = None

        for provider_id in ['openai', 'anthropic', 'gemini']:
            if self.provider_enabled[provider_id] and self.provider_keys[provider_id]:
                configured_count += 1
                tested = self.provider_tested.get(provider_id, False)

                if provider_id == 'openai':
                    name = "OpenAI (GPT)"
                elif provider_id == 'anthropic':
                    name = "Anthropic (Claude)"
                elif provider_id == 'gemini':
                    name = "Google Gemini"
                else:
                    name = provider_id.title()

                status = "✅ Tested & Working" if tested else "⚠️ Not Tested"
                summary_html += f"<li><b>{name}</b>: {status}</li>"

                if tested and first_working_provider is None:
                    first_working_provider = provider_id

        summary_html += "</ul>"

        if configured_count == 0:
            summary_html += "<p style='color: #ef4444;'>No providers configured!</p>"
        else:
            # Set default provider to first working one, or first enabled one
            if first_working_provider:
                self.default_provider = first_working_provider
            else:
                for provider_id in ['anthropic', 'openai', 'gemini']:
                    if self.provider_enabled[provider_id] and self.provider_keys[provider_id]:
                        self.default_provider = provider_id
                        break

            if self.default_provider == 'openai':
                default_name = "OpenAI (GPT)"
            elif self.default_provider == 'anthropic':
                default_name = "Anthropic (Claude)"
            elif self.default_provider == 'gemini':
                default_name = "Google Gemini"
            else:
                default_name = self.default_provider.title()

            summary_html += f"<br><h3>Default Provider:</h3><p><b>{default_name}</b></p>"
            summary_html += "<p style='font-size: 9pt; color: #9ca3af;'>You can change this in Settings later.</p>"

        self.summary_text.setHtml(summary_html)

    def next_page(self):
        """Go to next page"""
        current_index = self.pages.currentIndex()

        # Special handling for provider selection -> key input transition
        if current_index == 1:  # Provider selection page
            self.update_key_input_page()

        # Special handling for key input -> confirmation transition
        if current_index == 2:  # Key input page
            self.update_confirmation_page()

        if current_index < self.pages.count() - 1:
            self.pages.setCurrentIndex(current_index + 1)
            self.update_navigation()

    def previous_page(self):
        """Go to previous page"""
        current_index = self.pages.currentIndex()
        if current_index > 0:
            self.pages.setCurrentIndex(current_index - 1)
            self.update_navigation()

    def update_navigation(self):
        """Update navigation button states"""
        current_index = self.pages.currentIndex()

        # Update back button
        self.back_button.setEnabled(current_index > 0)

        # Update next button
        if current_index == self.pages.count() - 1:
            # Last page - change to Finish button
            self.next_button.setText("Finish & Start Assistant")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self.finish_setup)
        else:
            self.next_button.setText("Next →")
            try:
                self.next_button.clicked.disconnect()
            except:
                pass
            self.next_button.clicked.connect(self.next_page)

        # Enable/disable next button based on page requirements
        can_proceed = True

        if current_index == 1:  # Provider selection
            # At least one provider must be selected
            can_proceed = any(self.provider_enabled.values())

        elif current_index == 2:  # Key input
            # All enabled providers must have keys entered (not necessarily tested)
            for provider_id, enabled in self.provider_enabled.items():
                if enabled and not self.provider_keys.get(provider_id, '').strip():
                    can_proceed = False
                    break

        self.next_button.setEnabled(can_proceed)

    def finish_setup(self):
        """Complete the setup wizard"""
        # Save credentials to secure storage
        credentials = {}
        for provider_id, key in self.provider_keys.items():
            if self.provider_enabled[provider_id] and key:
                if provider_id == 'openai':
                    credentials['OPENAI_API_KEY'] = key
                elif provider_id == 'anthropic':
                    credentials['ANTHROPIC_API_KEY'] = key
                elif provider_id == 'gemini':
                    credentials['GEMINI_API_KEY'] = key

        if credentials:
            try:
                self.credential_store.save_credentials(credentials)
                logger.info(f"Saved {len(credentials)} credentials to secure storage")

                # Emit completion signal with default provider and credentials
                self.setup_complete.emit(self.default_provider, credentials)

                # Show success message
                QMessageBox.information(
                    self,
                    "Setup Complete",
                    f"Your API keys have been saved securely!\n\n"
                    f"Default provider: {self.default_provider.title()}\n\n"
                    f"The assistant is ready to use. Press Ctrl+Shift+G to toggle the overlay."
                )

                self.accept()

            except Exception as e:
                logger.error(f"Failed to save credentials: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Setup Failed",
                    f"Failed to save your credentials:\n{str(e)}\n\n"
                    f"Please try again or check the log file for details."
                )
        else:
            QMessageBox.warning(
                self,
                "No Credentials",
                "No API keys were configured. Please go back and enter at least one API key."
            )

    def closeEvent(self, event):
        """Ensure background threads are cleaned up when the dialog closes"""
        self._stop_test_thread()
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
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3a3a3a;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: #14b8a6;
                border-color: #14b8a6;
            }
        """)
