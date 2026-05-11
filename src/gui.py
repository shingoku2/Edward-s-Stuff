"""
Omnix GUI Module
================

PyQt6 interface styled with the Omnix QSS theme. Provides the main dashboard,
chat panel, settings panel, and in-game overlay window matching the reference
visual design.
"""

from __future__ import annotations

import logging
import sys
import json
from pathlib import Path
from typing import Dict, Optional
import psutil

from PyQt6.QtCore import QEvent, Qt, QThread, QTimer, pyqtSignal, QSize, QObject, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from src.config import Config
from src.credential_store import CredentialStore
from src.ui.design_system import OmnixDesignSystem, design_system
from src.keybind_manager import KeybindManager
from src.macro_manager import MacroManager
from src.ui.theme_manager import OmnixThemeManager
from src.settings_dialog import TabbedSettingsDialog

# New HUD primitives
from src.omnix_hud import (
    HudPanel,
    NeonButton,
    ChatPanel,
    GameStatusWidget,
    StatBlock,
    OMNIX_GLOBAL_QSS,
)

logger = logging.getLogger(__name__)


class JSBridge(QObject):
    """Bridge for communication between JS/React and Python."""

    messageReceived = pyqtSignal(str)
    settingsChanged = pyqtSignal(dict)
    systemStatsUpdated = pyqtSignal(str)

    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window

    @pyqtSlot(str)
    def sendMessage(self, content: str):
        """Called from React when user sends a message."""
        self.main_window.send_message_to_ai(content)

    @pyqtSlot(str, str)
    def updateSetting(self, key: str, value: str):
        """Called from React to update a config setting."""
        logger.info(f"Setting updated from JS: {key} = {value}")
        # Add logic to update config here

    @pyqtSlot()
    def toggleOverlay(self):
        """Called from React to toggle the overlay window."""
        self.main_window._toggle_overlay()

    @pyqtSlot(result=str)
    def getConfig(self):
        """Called from React to get current config."""
        cfg = self.main_window.config
        config_data = {
            "ai": {
                "provider": cfg.ai_provider,
                "model": cfg.ollama_model,
            },
            "ui": {
                "opacity": cfg.overlay_opacity,
                "theme": cfg.theme,
            }
        }
        return json.dumps(config_data)

    @pyqtSlot(str, result=bool)
    def saveSettings(self, settings_json: str):
        """Called from React to save settings."""
        try:
            data = json.loads(settings_json)
            updates = {}
            
            # Map UI settings
            if "ui" in data:
                if "opacity" in data["ui"]:
                    updates["overlay_opacity"] = float(data["ui"]["opacity"])
                
            # Map AI settings
            if "ai" in data:
                if "model" in data["ai"]:
                    updates["ollama_model"] = data["ai"]["model"]
            
            if updates:
                self.main_window.config.update(updates)
                self.main_window.config.save()
                self.settingsChanged.emit(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    @pyqtSlot(result=str)
    def getMacros(self):
        """Called from React to get all macros."""
        macros = self.main_window.macro_manager.get_all_macros()
        return json.dumps([m.to_dict() for m in macros])

    @pyqtSlot(str, result=bool)
    def saveMacro(self, macro_json: str):
        """Called from React to save (update or create) a macro."""
        try:
            data = json.loads(macro_json)
            from src.macro_manager import Macro
            
            # Reconstruct macro from JSON
            macro = Macro.from_dict(data)
            
            # Update manager
            self.main_window.macro_manager.macros[macro.id] = macro
            
            # Persist to disk
            all_macros = self.main_window.macro_manager.save_to_dict()
            self.main_window.config.save_macros(all_macros)
            return True
        except Exception as e:
            logger.error(f"Failed to save macro: {e}")
            return False

    @pyqtSlot()
    def startMacroRecording(self):
        """Start recording a macro."""
        # Use a default name, user can rename later
        self.main_window.macro_manager.start_recording("New Recording")

    @pyqtSlot()
    def stopMacroRecording(self):
        """Stop recording."""
        macro = self.main_window.macro_manager.stop_recording()
        if macro:
            all_macros = self.main_window.macro_manager.save_to_dict()
            self.main_window.config.save_macros(all_macros)
            # Signal could be emitted here to refresh UI


def _load_qss() -> str:
    """Load the legacy Omnix QSS stylesheet.

    DEPRECATED: This function loads hardcoded styles that should be replaced
    with design system tokens. This is kept for backward compatibility only.

    TODO: Migrate all styling to use OmnixDesignSystem tokens instead.
    """
    qss_path = Path(__file__).parent / "ui" / "omnix.qss"
    if not qss_path.exists():
        logger.warning("Legacy QSS stylesheet not found at %s", qss_path)
        return _generate_token_based_styles()

    try:
        legacy_qss = qss_path.read_text(encoding="utf-8")
        logger.warning(
            "Loading legacy QSS stylesheet - consider migrating to design system tokens"
        )
        # For now, return legacy styles but log migration warning
        return legacy_qss
    except Exception as e:
        logger.error("Failed to load legacy QSS stylesheet: %s", e)
        return _generate_token_based_styles()


def _generate_token_based_styles() -> str:
    """Generate QSS styles using design system tokens (future migration target)."""
    try:
        from .ui.design_system import design_system

        # Generate minimal styles using design tokens
        styles = f"""
        /* Omnix Design System Generated Styles */
        QWidget {{
            background-color: {design_system.colors.background.primary};
            color: {design_system.colors.text.primary};
            font-family: {design_system.typography.font_primary};
        }}
        
        QPushButton {{
            background-color: {design_system.colors.primary.default};
            color: {design_system.colors.primary.foreground};
            border: none;
            border-radius: {design_system.radius.md}px;
            padding: {design_system.spacing.sm}px {design_system.spacing.md}px;
        }}
        
        QPushButton:hover {{
            background-color: {design_system.colors.primary.hover};
        }}
        """
        return styles
    except ImportError:
        # Fallback if design system not available
        return "/* Design system not available - using minimal fallback styles */"


class AIWorkerThread(QThread):
    """Background worker that calls the AI assistant without blocking the UI."""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, assistant, question: str, game_context: Optional[Dict] = None):
        super().__init__()
        self.assistant = assistant
        self.question = question
        self.game_context = game_context or {}

    def run(self) -> None:
        try:
            if self.assistant is None:
                response = "Omnix is standing by. Configure an AI provider to begin."
            else:
                response = self.assistant.ask_question(
                    self.question, game_context=self.game_context
                )
            self.finished.emit(response or "")
        except Exception as exc:
            logger.exception("AI worker failed")
            self.error.emit(str(exc))


class OverlayWindow(QWidget):
    """Frameless always-on-top overlay with React-based HUD."""

    def __init__(self, assistant, config: Config, ds: OmnixDesignSystem):
        super().__init__()
        self.assistant = assistant
        self.config = config
        self.design_system = ds

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setGeometry(
            int(getattr(config, "overlay_x", 100)),
            int(getattr(config, "overlay_y", 100)),
            int(getattr(config, "overlay_width", 1200)),
            int(getattr(config, "overlay_height", 800)),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        layout.addWidget(self.web_view)

        # Load Frontend with overlay mode
        frontend_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
        if frontend_path.exists():
            url = frontend_path.absolute().as_uri() + "?mode=overlay"
            from PyQt6.QtCore import QUrl
            self.web_view.load(QUrl(url))
        else:
            from PyQt6.QtCore import QUrl
            self.web_view.load(QUrl("http://localhost:3001?mode=overlay"))

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_position_and_size)
        self._save_delay_ms = 500

    def closeEvent(self, event: QEvent) -> None:
        super().closeEvent(event)
        self._save_overlay_config()

    def _save_overlay_config(self) -> None:
        try:
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
                overlay_opacity=self.config.overlay_opacity,
            )
        except Exception as e:
            logger.error(f"Failed to save overlay config: {e}")

    def toggle_minimize(self) -> None:
        self.minimized = not self.minimized
        self.config.overlay_minimized = self.minimized
        if self.minimized:
            self._saved_height = self.height()
            self.chat.setVisible(False)
            self.setFixedHeight(40)
        else:
            self.chat.setVisible(True)
            self.setFixedHeight(getattr(self, "_saved_height", 400))

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self._save_timer.start(self._save_delay_ms)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._save_timer.start(self._save_delay_ms)

    def _save_position_and_size(self) -> None:
        try:
            self.config.overlay_x = self.x()
            self.config.overlay_y = self.y()
            self.config.overlay_width = self.width()
            self.config.overlay_height = self.height()
            self.config.save()
        except Exception as e:
            logger.warning(f"Failed to save overlay position: {e}")


class MainWindow(QMainWindow):
    """Omnix main dashboard window with new HUD layout."""

    def __init__(
        self,
        ai_assistant,
        config: Config,
        credential_store: CredentialStore,
        design_system: OmnixDesignSystem = design_system,
        game_detector=None,
    ):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.config = config
        self.credential_store = credential_store
        self.design_system = design_system or OmnixDesignSystem()
        self.game_detector = game_detector
        self.current_game = None
        self.ai_worker: Optional[AIWorkerThread] = None

        self.setWindowTitle("OMNIX // HUD")
        self.resize(1280, 800)

        # Apply Global QSS
        self.setStyleSheet(OMNIX_GLOBAL_QSS)

        self.keybind_manager = KeybindManager()
        self.macro_manager = MacroManager()
        self.theme_manager = OmnixThemeManager()
        self.settings_dialog = None

        self.overlay_window = OverlayWindow(ai_assistant, config, self.design_system)

        # Setup Web View
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # Setup Web Channel for JS-Python communication
        self.bridge = JSBridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Load Frontend
        frontend_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
        if frontend_path.exists():
            self.web_view.load(frontend_path.absolute().as_uri())
        else:
            # Fallback for development (vite dev server)
            from PyQt6.QtCore import QUrl
            self.web_view.load(QUrl("http://localhost:3001"))

        # Start services
        if self.game_detector:
            self._start_game_detection()
            
        self._start_system_stats()

    def _start_system_stats(self) -> None:
        """Start periodic system stats collection."""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_system_stats)
        self.stats_timer.start(1000)

    def _update_system_stats(self) -> None:
        """Collect and emit system stats."""
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            data = {"cpu": cpu, "ram": ram}
            self.bridge.systemStatsUpdated.emit(json.dumps(data))
        except Exception as e:
            logger.error(f"Error updating system stats: {e}")

    def send_message_to_ai(self, text: str) -> None:
        """Handle message sending initiated from React."""
        if self.ai_worker is not None:
            return  # Already processing

        self.ai_worker = AIWorkerThread(self.ai_assistant, text)
        self.ai_worker.finished.connect(self._handle_response)
        self.ai_worker.error.connect(self._handle_error)
        self.ai_worker.start()

    def _handle_response(self, response: str) -> None:
        """Send AI response back to React."""
        self.bridge.messageReceived.emit(response)
        self.ai_worker = None

    def _handle_error(self, message: str) -> None:
        """Send error message back to React."""
        self.bridge.messageReceived.emit(f"Error: {message}")
        self.ai_worker = None

    def _build_header(self) -> QHBoxLayout:
        # Recreating header to match logic flow
        layout = QHBoxLayout()

        frame = QFrame()
        frame.setObjectName("top-bar")
        frame.setFixedHeight(50)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        h_layout = QHBoxLayout(frame)
        h_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("OMNIX")
        logo.setObjectName("omnix-logo")
        h_layout.addWidget(logo)

        sub = QLabel(" // SYSTEM READY")
        sub.setObjectName("omnix-logo-subtitle")
        sub.setContentsMargins(10, 6, 0, 0)
        h_layout.addWidget(sub)

        h_layout.addStretch()

        user = QLabel("PILOT ID: ADMIN")
        user.setObjectName("top-bar-user")
        h_layout.addWidget(user)

        layout.addWidget(frame)
        return layout

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setSpacing(20)

        # Large Overlay Button
        overlay_btn = NeonButton("TOGGLE OVERLAY", primary=True)
        overlay_btn.setMinimumHeight(48)
        overlay_btn.clicked.connect(self._toggle_overlay)
        footer.addWidget(overlay_btn, 1)

        # Large Settings Button
        settings_btn = NeonButton("SYSTEM SETTINGS", primary=False)
        settings_btn.setMinimumHeight(48)
        settings_btn.clicked.connect(self._open_settings)
        footer.addWidget(settings_btn, 1)

        return footer

    def _toggle_overlay(self) -> None:
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
        else:
            self.overlay_window.show()
            self.overlay_window.raise_()

    def _open_settings(self) -> None:
        self._open_settings_at_tab(0)

    def _open_settings_at_tab(self, tab_index: int) -> None:
        if self.settings_dialog is None:
            self.settings_dialog = TabbedSettingsDialog(
                self,
                self.config,
                self.keybind_manager,
                self.macro_manager,
                self.theme_manager,
            )
            self.settings_dialog.settings_saved.connect(self._on_settings_saved)
        self.settings_dialog.set_current_tab(tab_index)
        self.settings_dialog.exec()

    def _on_settings_saved(self, settings: dict) -> None:
        pass

    def _start_game_detection(self) -> None:
        self.game_check_timer = QTimer()
        self.game_check_timer.timeout.connect(self._check_for_game)
        self.game_check_timer.start(5000)
        self._check_for_game()

    def _check_for_game(self) -> None:
        if not self.game_detector:
            return
        game = self.game_detector.detect_running_game()

        if game and game.get("name") != self.current_game:
            self.current_game = game.get("name")
            self._update_game_status(game)
        elif not game and self.current_game:
            self.current_game = None
            self._update_game_status(None)

    def _update_game_status(self, game: Optional[Dict]) -> None:
        online = bool(game)
        name = game.get("name") if game else None
        pid = str(game.get("pid", "--")) if game else "--"

        # Update Center Widget
        self.game_status.set_game(name, online)

        # Update Stats (Mock stats for now, could come from DB)
        if online:
            self.stat_block.set_stats(kd="1.2", matches="42", wins="54%")
        else:
            self.stat_block.set_stats(kd="--", matches="--", wins="--")

        # Notify AI
        if self.ai_assistant:
            self.ai_assistant.set_current_game(game)

    def cleanup(self) -> None:
        if self.overlay_window:
            self.overlay_window.close()
        if hasattr(self, "game_check_timer"):
            self.game_check_timer.stop()
        if hasattr(self, "stats_timer"):
            self.stats_timer.stop()


def run_gui(
    ai_assistant,
    config: Config,
    credential_store: CredentialStore,
    ds: OmnixDesignSystem = design_system,
    game_detector=None,
) -> None:
    """Launch the Omnix GUI."""
    app = QApplication.instance() or QApplication(sys.argv)

    # Set dark palette as fallback
    app.setStyle("Fusion")

    window = MainWindow(ai_assistant, config, credential_store, ds, game_detector)
    window.show()
    sys.exit(app.exec())


__all__ = [
    "AIWorkerThread",
    "OverlayWindow",
    "MainWindow",
    "run_gui",
]
