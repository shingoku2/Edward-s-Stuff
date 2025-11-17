"""
Settings Dialog Module
Comprehensive tabbed settings dialog for the Gaming AI Assistant
"""

import logging
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt

from settings_tabs import KeybindingsTab, MacrosTab
from appearance_tabs import AppAppearanceTab, OverlayAppearanceTab
from providers_tab import ProvidersTab
from game_profiles_tab import GameProfilesTab
from knowledge_packs_tab import KnowledgePacksTab
from keybind_manager import KeybindManager
from macro_manager import MacroManager
from theme_compat import ThemeManager

logger = logging.getLogger(__name__)


class TabbedSettingsDialog(QDialog):
    """
    Comprehensive settings dialog with tabs for:
    - General (AI provider, API keys, sessions)
    - Keybindings
    - Macros
    - App Appearance
    - Overlay Appearance
    """

    # Signals
    settings_saved = pyqtSignal(dict)  # Emits all settings as dict
    keybinds_changed = pyqtSignal(dict)
    macros_changed = pyqtSignal(dict)
    theme_changed = pyqtSignal(dict)
    overlay_appearance_changed = pyqtSignal(dict)
    provider_config_changed = pyqtSignal(str, dict)  # default_provider, credentials
    game_profiles_changed = pyqtSignal()  # Emitted when game profiles are modified

    def __init__(
        self,
        parent,
        config,
        keybind_manager: KeybindManager,
        macro_manager: MacroManager,
        theme_manager: ThemeManager,
        # Keep reference to original SettingsDialog for General tab
        original_settings_widget=None
    ):
        super().__init__(parent)
        self.config = config
        self.keybind_manager = keybind_manager
        self.macro_manager = macro_manager
        self.theme_manager = theme_manager
        self.original_settings_widget = original_settings_widget

        self.init_ui()

    def init_ui(self):
        """Initialize the tabbed settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        layout = QVBoxLayout()

        # Title
        title = QLabel("⚙️ Application Settings")
        title.setStyleSheet("""
            QLabel {
                color: #14b8a6;
                font-size: 18pt;
                font-weight: bold;
                padding: 15px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Add tabs
        self.add_tabs()

        layout.addWidget(self.tab_widget)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save All Settings")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #14b8a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0f9688;
            }
            QPushButton:pressed {
                background-color: #0d7a6f;
            }
        """)
        self.save_button.clicked.connect(self.save_all_settings)
        button_layout.addWidget(self.save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Apply theme styling
        self.apply_dialog_theme()

    def add_tabs(self):
        """Add all tabs to the tab widget"""
        # AI Providers tab (most important, so it goes first)
        self.providers_tab = ProvidersTab(self.config)
        self.providers_tab.provider_config_changed.connect(self.on_provider_config_changed)
        self.tab_widget.addTab(self.providers_tab, "🔑 AI Providers")

        # Game Profiles tab
        self.game_profiles_tab = GameProfilesTab()
        self.game_profiles_tab.profile_changed.connect(self.on_game_profiles_changed)
        self.tab_widget.addTab(self.game_profiles_tab, "🎮 Game Profiles")

        # Knowledge Packs tab
        self.knowledge_packs_tab = KnowledgePacksTab(self)
        self.knowledge_packs_tab.packs_changed.connect(self.on_packs_changed)
        self.tab_widget.addTab(self.knowledge_packs_tab, "📚 Knowledge Packs")

        # Keybindings tab
        self.keybindings_tab = KeybindingsTab(self.keybind_manager, self.macro_manager)
        self.keybindings_tab.keybinds_changed.connect(self.on_keybinds_changed)
        self.tab_widget.addTab(self.keybindings_tab, "⌨️ Keybindings")

        # Macros tab
        self.macros_tab = MacrosTab(self.macro_manager)
        self.macros_tab.macros_changed.connect(self.on_macros_changed)
        self.tab_widget.addTab(self.macros_tab, "⚡ Macros")

        # App Appearance tab
        self.app_appearance_tab = AppAppearanceTab(self.theme_manager)
        self.app_appearance_tab.theme_changed.connect(self.on_theme_changed)
        self.tab_widget.addTab(self.app_appearance_tab, "🎨 App Appearance")

        # Overlay Appearance tab
        self.overlay_appearance_tab = OverlayAppearanceTab(self.theme_manager)
        self.overlay_appearance_tab.overlay_appearance_changed.connect(self.on_overlay_appearance_changed)
        self.tab_widget.addTab(self.overlay_appearance_tab, "🪟 Overlay Appearance")

    def on_keybinds_changed(self, keybinds_dict: dict):
        """Handle keybinds changed"""
        logger.info(f"Keybinds changed: {len(keybinds_dict)} keybinds")
        self.keybinds_changed.emit(keybinds_dict)

    def on_macros_changed(self, macros_dict: dict):
        """Handle macros changed"""
        logger.info(f"Macros changed: {len(macros_dict)} macros")
        self.macros_changed.emit(macros_dict)

    def on_theme_changed(self, theme_dict: dict):
        """Handle theme changed"""
        logger.info("Theme changed")
        self.theme_changed.emit(theme_dict)

    def on_overlay_appearance_changed(self, appearance_dict: dict):
        """Handle overlay appearance changed"""
        logger.info("Overlay appearance changed")
        self.overlay_appearance_changed.emit(appearance_dict)

    def on_provider_config_changed(self, default_provider: str, credentials: dict):
        """Handle provider configuration changed"""
        logger.info(f"Provider config changed: {default_provider}, {len(credentials)} credentials")
        self.provider_config_changed.emit(default_provider, credentials)

    def on_game_profiles_changed(self):
        """Handle game profiles changed"""
        logger.info("Game profiles changed")
        self.game_profiles_changed.emit()

    def on_packs_changed(self):
        """Handle knowledge packs being updated"""
        logger.info("Knowledge packs changed")

    def save_all_settings(self):
        """Save all settings from all tabs"""
        try:
            # Get all settings
            keybinds = self.keybindings_tab.get_keybinds()
            macros = self.macros_tab.get_macros()
            theme = self.app_appearance_tab.get_theme()
            overlay_appearance = self.overlay_appearance_tab.get_overlay_appearance()

            # Save provider configuration
            provider_saved = self.providers_tab.save_provider_config()
            if not provider_saved:
                # If provider config save failed, don't proceed
                return

            # Get provider config
            default_provider, credentials = self.providers_tab.get_provider_config()

            # Save to config
            self.config.save_keybinds(keybinds)
            self.config.save_macros(macros)
            self.config.save_theme(theme)

            # Save provider to .env
            if default_provider:
                from config import Config
                Config.save_to_env(
                    provider=default_provider,
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
                # Update the config object in memory so changes take effect immediately
                self.config.ai_provider = default_provider

            # Emit signals
            self.keybinds_changed.emit(keybinds)
            self.macros_changed.emit(macros)
            self.theme_changed.emit(theme)
            self.overlay_appearance_changed.emit(overlay_appearance)
            self.provider_config_changed.emit(default_provider, credentials)

            # Emit comprehensive settings saved signal
            all_settings = {
                'keybinds': keybinds,
                'macros': macros,
                'theme': theme,
                'overlay_appearance': overlay_appearance,
                'default_provider': default_provider,
                'credentials': credentials
            }
            self.settings_saved.emit(all_settings)

            logger.info("All settings saved successfully")

            QMessageBox.information(
                self,
                "Settings Saved",
                "All settings have been saved successfully!\n\n"
                "Some changes may require restarting the application to take full effect."
            )

            self.accept()

        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save settings:\n{str(e)}"
            )

    def apply_dialog_theme(self):
        """Apply theme styling to the dialog"""
        # Get current theme from theme manager
        theme = self.theme_manager.current_theme

        # Apply dark theme by default
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_color};
            }}
            QLabel {{
                color: {theme.text_color};
            }}
            QTabWidget::pane {{
                border: 2px solid {theme.surface_color};
                border-radius: 5px;
                background: {theme.background_color};
            }}
            QTabBar::tab {{
                background: {theme.surface_color};
                color: {theme.text_color};
                border: 2px solid {theme.surface_color};
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 10px 20px;
                margin-right: 2px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {theme.primary_color};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {theme.primary_color};
                opacity: 0.8;
            }}
        """)
