"""
GUI Module
Main application interface with overlay capabilities
"""

import logging
from pathlib import Path
from typing import Dict

from PyQt6.QtCore import (
    QObject,
    Qt,
    QThread,
    QTimer,
    QtMsgType,
    pyqtSignal,
    qInstallMessageHandler,
    QUrl,
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


from config import Config
from credential_store import CredentialStore, CredentialStoreError  # noqa: F401
from game_profile import get_profile_store
from game_watcher import get_game_watcher
from keybind_manager import DEFAULT_KEYBINDS, KeybindManager
from macro_manager import MacroActionType, MacroManager
from macro_runner import MacroRunner
from session_recap_dialog import SessionRecapDialog
from settings_dialog import TabbedSettingsDialog
from theme_compat import DEFAULT_DARK_THEME, ThemeManager

# Import design system components
from ui.components import OmnixIconButton, OmnixLineEdit
from ui.icons import icons  # noqa: F401
from ui.tokens import COLORS, RADIUS, SPACING, TYPOGRAPHY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def qt_message_handler(msg_type, context, message):
    """
    Custom Qt message handler to catch Qt warnings and errors.
    This helps catch C++ level Qt errors that might not be visible in Python exceptions.
    """
    if msg_type == QtMsgType.QtDebugMsg:
        logger.debug(f"Qt Debug: {message}")
    elif msg_type == QtMsgType.QtInfoMsg:
        logger.info(f"Qt Info: {message}")
    elif msg_type == QtMsgType.QtWarningMsg:
        logger.warning(f"Qt Warning: {message}")
        logger.warning(f"  File: {context.file if context.file else 'unknown'}")
        logger.warning(f"  Line: {context.line if context.line else 'unknown'}")
        logger.warning(f"  Function: {context.function if context.function else 'unknown'}")
    elif msg_type == QtMsgType.QtCriticalMsg:
        logger.critical(f"Qt Critical: {message}")
        logger.critical(f"  File: {context.file if context.file else 'unknown'}")
        logger.critical(f"  Line: {context.line if context.line else 'unknown'}")
        logger.critical(f"  Function: {context.function if context.function else 'unknown'}")
    elif msg_type == QtMsgType.QtFatalMsg:
        logger.critical(f"Qt Fatal: {message}")
        logger.critical(f"  File: {context.file if context.file else 'unknown'}")
        logger.critical(f"  Line: {context.line if context.line else 'unknown'}")
        logger.critical(f"  Function: {context.function if context.function else 'unknown'}")
        logger.critical("=" * 70)
        logger.critical("Qt FATAL ERROR - Application will crash!")
        logger.critical("=" * 70)


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


class SessionEventBridge(QObject):
    """Bridge authentication events from background threads to the GUI."""

    session_event = pyqtSignal(str, str, dict)

    def emit_event(self, provider: str, action: str, payload: Dict[str, str]):
        self.session_event.emit(provider, action, payload)



# Import custom widgets
from ui.widgets.bottom_bar import BottomBar
from ui.widgets.chat import ChatPanel
from ui.widgets.overlay_window import OverlayWindow
from ui.widgets.panels import AIProviderPanel, GameStatusPanel, SettingsPanel



class MainWindow(QMainWindow):
    """Main application window with game detection and AI chat interface"""

    def __init__(
        self,
        ai_assistant,
        config,
        credential_store,
        design_system,
    ):
        super().__init__()
        self.ai_assistant = ai_assistant  # Can be None if no API keys configured
        self.config = config
        self.credential_store = credential_store
        self.design_system = design_system

        self.current_game = None

        # Worker threads for button actions (prevents garbage collection crashes)
        self.tips_worker = None
        self.overview_worker = None

        # Track if this is first show (for auto-opening settings)
        self.first_show = True

        # Track dragging state for frameless window
        self.dragging = False
        self.drag_position = None

        # Initialize managers for advanced features
        self.init_managers()

        # Create overlay window (but don't show it yet)
        # Note: parent=None to prevent overlay from hiding when main window loses focus
        self.overlay_window = OverlayWindow(ai_assistant, config, design_system, parent=None)
        if hasattr(self.overlay_window, "chat_widget"):
            self.overlay_window.chat_widget.set_game_context_provider(self._get_chat_game_context)

        # Initialize game watcher for game detection and profile switching
        self.game_watcher = get_game_watcher(check_interval=config.check_interval)
        self.profile_store = get_profile_store()

        self.session_event_bridge = SessionEventBridge()
        self.session_event_bridge.session_event.connect(self.on_session_event)

        if self.ai_assistant:
            self.ai_assistant.register_session_refresh_handler(self.session_event_bridge.emit_event)

        self.init_ui()
        self.start_game_watcher()

        # Start global hotkey listener after UI is ready
        self.start_hotkey_listener()

    def init_managers(self):
        """Initialize keybind, macro, and theme managers"""
        logger.info("Initializing advanced feature managers...")

        # Initialize KeybindManager
        self.keybind_manager = KeybindManager()

        # Load keybinds from config
        if self.config.keybinds:
            try:
                self.keybind_manager.load_from_dict(self.config.keybinds)
            except Exception as e:
                logger.error(f"Failed to load keybinds from config: {e}")
        else:
            # Load defaults
            for default_keybind in DEFAULT_KEYBINDS:
                self.keybind_manager.register_keybind(default_keybind, lambda: None)

        # Initialize MacroManager
        self.macro_manager = MacroManager()

        # Load macros from config
        if self.config.macros:
            self.macro_manager.load_from_dict(self.config.macros)

        # Initialize MacroRunner (after MacroManager so we can pass it in)
        self.macro_runner = MacroRunner(
            enabled=self.config.macros_enabled, macro_manager=self.macro_manager
        )

        # Initialize ThemeManager
        self.theme_manager = ThemeManager()

        # Load theme from config
        if self.config.theme:
            self.theme_manager.load_from_dict(self.config.theme)
        else:
            # Use default dark theme
            self.theme_manager.set_theme(DEFAULT_DARK_THEME)

        logger.info("Advanced feature managers initialized")

    def start_hotkey_listener(self):
        """Start listening for global hotkeys"""
        try:
            # Register keybind callbacks
            self.register_keybind_callbacks()

            # Start the global listener
            self.keybind_manager.start_listening()
            logger.info("Global hotkey listener started")
        except Exception as e:
            logger.warning(f"Could not start global hotkey listener: {e}")

    def register_keybind_callbacks(self):
        """Register callbacks for all keybind actions"""
        # Overlay toggle
        toggle_keybind = self.keybind_manager.get_keybind("toggle_overlay")
        if toggle_keybind:
            self.keybind_manager.callbacks["toggle_overlay"] = self.toggle_overlay_visibility

        # Open settings
        settings_keybind = self.keybind_manager.get_keybind("open_settings")
        if settings_keybind:
            self.keybind_manager.callbacks["open_settings"] = self.open_advanced_settings

        # Clear chat
        clear_keybind = self.keybind_manager.get_keybind("clear_chat")
        if clear_keybind:
            self.keybind_manager.callbacks["clear_chat"] = lambda: (
                self.overlay_window.chat_widget.clear_chat()
                if hasattr(self, "overlay_window") and self.overlay_window
                else None
            )

        # Show tips
        tips_keybind = self.keybind_manager.get_keybind("show_tips")
        if tips_keybind:
            self.keybind_manager.callbacks["show_tips"] = self.get_tips

        # Show overview
        overview_keybind = self.keybind_manager.get_keybind("show_overview")
        if overview_keybind:
            self.keybind_manager.callbacks["show_overview"] = self.get_overview

        # Register macro action handlers
        self.macro_manager.register_action_handler(MacroActionType.SHOW_TIPS.value, self.get_tips)
        self.macro_manager.register_action_handler(
            MacroActionType.SHOW_OVERVIEW.value, self.get_overview
        )
        self.macro_manager.register_action_handler(
            MacroActionType.CLEAR_CHAT.value,
            lambda: (
                self.overlay_window.chat_widget.clear_chat()
                if hasattr(self, "overlay_window") and self.overlay_window
                else None
            ),
        )
        self.macro_manager.register_action_handler(
            MacroActionType.TOGGLE_OVERLAY.value, self.toggle_overlay_visibility
        )
        self.macro_manager.register_action_handler(
            MacroActionType.CLOSE_OVERLAY.value,
            lambda: self.overlay_window.hide() if hasattr(self, "overlay_window") else None,
        )
        self.macro_manager.register_action_handler(
            MacroActionType.OPEN_SETTINGS.value, self.open_advanced_settings
        )

        # Register macro keybinds - iterate over all macros and register their keybinds
        self._register_macro_keybinds()

        logger.info("Keybind callbacks registered")

    def _register_macro_keybinds(self):
        """Register keybind callbacks for all macros that have keybinds assigned"""
        try:
            # Get all macros from the macro manager
            all_macros = self.macro_manager.get_all_macros()

            for macro in all_macros:
                if not macro.enabled:
                    continue

                # Check if this macro has a keybind registered
                macro_keybind = self.keybind_manager.get_macro_keybind(macro.id)
                if macro_keybind and macro_keybind.enabled:
                    # Create a callback for this specific macro
                    # Use a lambda with default argument to capture the macro correctly
                    callback = lambda m=macro: self.macro_runner.execute_macro(m)

                    # Update the callback for this macro's keybind
                    action_key = f"macro_{macro.id}"
                    self.keybind_manager.callbacks[action_key] = callback

                    logger.debug(
                        f"Registered keybind callback for macro: {macro.name} (ID: {macro.id})"
                    )

            logger.info(
                f"Registered {len([m for m in all_macros if m.enabled])} macro keybind callbacks"
            )

        except Exception as e:
            logger.error(f"Error registering macro keybinds: {e}", exc_info=True)

    def toggle_overlay_visibility(self):
        """Toggle overlay visibility"""
        if hasattr(self, "overlay_window"):
            if self.overlay_window.isVisible():
                self.overlay_window.hide()
                logger.info("Overlay hidden via keybind")
            else:
                self.overlay_window.show()
                self.overlay_window.activateWindow()
                logger.info("Overlay shown via keybind")

    def on_session_event(self, provider: str, action: str, payload: Dict[str, str]):
        """Handle authentication session events from the AI assistant."""

        message = payload.get("message", "")

        if self.credential_store:
            self.credential_store.cache_tokens(provider, {})

        chat_widget = getattr(self, "chat_widget", None)

        if action == "fallback":
            if message and chat_widget:
                chat_widget.add_message("System", message, is_user=False)
        elif action == "reauth_required":
            QTimer.singleShot(
                0,
                lambda: QMessageBox.information(
                    self,
                    "Session Expired",
                    message or "Session expired. Please sign in again.",
                ),
            )
            QTimer.singleShot(250, self.open_advanced_settings)

    from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

# ... (rest of the imports)

class MainWindow(QMainWindow):
    # ... (rest of the class)

    def init_ui(self):
        """Initialize the main window UI to use a web view."""
        self.setWindowTitle("Omnix: All Knowing Gaming Companion")
        self.resize(1440, 900)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # Load the frontend UI
        # Assumes the frontend has been built and is in frontend/dist
        frontend_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
        if frontend_path.exists():
            self.web_view.setUrl(QUrl.fromLocalFile(str(frontend_path)))
        else:
            # Fallback to a simple message if the frontend hasn't been built
            self.web_view.setHtml("""
                <body style="background-color: #0A0C14; color: #E0E0E0; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
                    <div style="text-align: center; border: 1px solid #0af5ff; padding: 2rem; border-radius: 10px; box-shadow: 0 0 20px rgba(10, 245, 255, 0.2);">
                        <h1 style="color: #0af5ff;">Omnix UI Not Found</h1>
                        <p>The frontend application has not been built.</p>
                        <p>Please run <code>npm run build</code> in the <code>frontend</code> directory and restart the application.</p>
                    </div>
                </body>
            """)

        self.create_system_tray()
        logger.info("Main window initialized with web view.")


    def mousePressEvent(self, event):
        """Handle mouse press for dragging the frameless window"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on header for dragging
            if self.header.geometry().contains(event.pos()):
                self.dragging = True
                self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self.dragging
            and self.drag_position is not None
        ):
            self.move(event.globalPosition().toPoint() - self.drag_position)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_position = None
        super().mouseReleaseEvent(event)

    def show_about_dialog(self):
        """Show about dialog for Omnix"""
        QMessageBox.about(
            self,
            "About Omnix AI Assistant",
            "Omnix AI Assistant\n\n"
            "Your real-time gaming companion powered by AI.\n\n"
            "Detects games, provides tips, strategies, and answers questions.\n\n"
            "Version 1.0",
        )

    def open_settings_tab(self, tab_index: int):
        """Open advanced settings dialog at a specific tab"""
        logger.info(f"Opening settings dialog at tab {tab_index}")

        # Create the settings dialog
        dialog = TabbedSettingsDialog(
            parent=self,
            config=self.config,
            keybind_manager=self.keybind_manager,
            macro_manager=self.macro_manager,
            theme_manager=self.theme_manager,
        )

        # Connect signals
        dialog.keybinds_changed.connect(self.on_keybinds_updated)
        dialog.macros_changed.connect(self.on_macros_updated)
        dialog.theme_changed.connect(self.on_theme_updated)
        dialog.overlay_appearance_changed.connect(self.on_overlay_appearance_updated)
        dialog.provider_config_changed.connect(self.on_provider_config_updated)

        # Set the current tab to the requested one
        dialog.set_current_tab(tab_index)

        # Show the dialog
        dialog.exec()

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

    def start_game_watcher(self):
        """Start the game watcher background thread for profile switching"""
        try:
            # Connect game change signals to profile switching
            self.game_watcher.game_changed.connect(self.on_game_watcher_changed)
            self.game_watcher.game_closed.connect(self.on_game_watcher_closed)

            # Start the watcher
            self.game_watcher.start_watching()
            logger.info(f"Game watcher started with {self.game_watcher.check_interval}s interval")
        except Exception as e:
            logger.error(f"Failed to start game watcher: {e}")

    def on_game_watcher_changed(self, game_name: str, profile):
        """
        Handle game change from GameWatcher.
        Switches AI profile to match the detected game.

        Args:
            game_name: Display name of the detected game
            profile: GameProfile for this game
        """
        try:
            profile_label = getattr(profile, "id", "unknown") if profile else "unknown"
            logger.info(f"GameWatcher detected game change: {game_name} (profile: {profile_label})")

            profile_id = getattr(profile, "id", None)
            executable_name = getattr(profile, "executable_name", None)
            self.current_game = {
                "name": game_name,
                "profile_id": profile_id,
                "executable": executable_name,
            }

            if self.ai_assistant:
                # Ensure the assistant resets its system prompt/history before
                # applying the game-specific profile so responses align with
                # the newly detected title.
                self.ai_assistant.set_current_game(self.current_game)
                logger.debug("AI Assistant current game context updated")

            # Update central game status display
            if hasattr(self, "game_status_panel"):
                self.game_status_panel.hex_widget.game_label.setText(game_name.upper())
                self.game_status_panel.hex_widget.status_label.setText("ONLINE")

            # Update overlay title with current game
            if self.overlay_window:
                self.overlay_window.setWindowTitle(f"Gaming Copilot - {game_name}")
                self.overlay_window.chat_widget.add_message(
                    "System",
                    f"Detected {game_name}! Ask me any questions about the game.",
                    is_user=False,
                )

            # Switch AI assistant to this game's profile
            if self.ai_assistant and profile:
                self.ai_assistant.set_game_profile(profile)
                logger.info(f"AI Assistant switched to profile: {profile.id}")
            else:
                logger.warning("AI assistant not available for profile switching")

        except Exception as e:
            logger.error(f"Error handling game change: {e}", exc_info=True)

    def on_game_watcher_closed(self):
        """Handle game close/loss from GameWatcher"""
        try:
            logger.info("GameWatcher: game closed")

            # Clear central game status
            if hasattr(self, "game_status_panel"):
                self.game_status_panel.hex_widget.game_label.setText("OMNIX")
                self.game_status_panel.hex_widget.status_label.setText("IDLE")

            # Update overlay title
            if self.overlay_window:
                self.overlay_window.setWindowTitle("Gaming Copilot")

            # Clear AI assistant profile
            if self.ai_assistant:
                self.ai_assistant.clear_game_profile()
                logger.info("AI Assistant profile cleared")

            self.current_game = None
            if self.ai_assistant:
                self.ai_assistant.current_game = None

        except Exception as e:
            logger.error(f"Error handling game close: {e}")

    def _get_chat_game_context(self) -> Optional[str]:
        """Return lightweight textual context about the current game for chat prompts"""
        if not self.current_game:
            return None

        game_name = self.current_game.get("name")
        if not game_name:
            return None

        profile_id = self.current_game.get("profile_id")
        if profile_id:
            return f"Current game: {game_name} (profile: {profile_id})"

        return f"Current game: {game_name}"

    def get_tips(self):
        """Request and display tips for the currently detected game"""
        if not self.current_game:
            return

        # Check if AI assistant is configured
        if not self.ai_assistant:
            if hasattr(self, "overlay_window") and self.overlay_window:
                self.overlay_window.chat_widget.add_message(
                    "System",
                    "⚠️ AI assistant not configured. Please click the Settings button to add your API keys.",
                    is_user=False,
                )
            return

        if hasattr(self, "overlay_window") and self.overlay_window:
            self.overlay_window.chat_widget.add_message("System", "Getting tips...", is_user=False)
        logger.info("Getting tips for current game")

        # Use worker thread
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
            self.tips_worker = None  # Clear reference after completion

        # Store worker as instance variable to prevent garbage collection
        self.tips_worker = TipsWorker(get_tips_impl)
        if hasattr(self, "overlay_window") and self.overlay_window:
            self.tips_worker.result_ready.connect(
                lambda tips: self.overlay_window.chat_widget.add_message(
                    "AI Assistant", tips, is_user=False
                )
            )
        self.tips_worker.finished.connect(cleanup_tips_worker)
        self.tips_worker.start()

    def get_overview(self):
        """Request and display overview of the currently detected game"""
        if not self.current_game:
            return

        # Check if AI assistant is configured
        if not self.ai_assistant:
            if hasattr(self, "overlay_window") and self.overlay_window:
                self.overlay_window.chat_widget.add_message(
                    "System",
                    "⚠️ AI assistant not configured. Please click the Settings button to add your API keys.",
                    is_user=False,
                )
            return

        game_name = self.current_game.get("name")
        if hasattr(self, "overlay_window") and self.overlay_window:
            self.overlay_window.chat_widget.add_message(
                "System", f"Getting overview of {game_name}...", is_user=False
            )
        logger.info(f"Getting overview for {game_name}")

        # Use worker thread
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
                if hasattr(self, "overlay_window") and self.overlay_window:
                    self.overlay_window.chat_widget.add_message(
                        "AI Assistant", overview, is_user=False
                    )
            except Exception as e:
                logger.error(f"Error displaying overview: {e}", exc_info=True)

        def handle_overview_error(error):
            try:
                if hasattr(self, "overlay_window") and self.overlay_window:
                    self.overlay_window.chat_widget.add_message(
                        "System", f"Error: {error}", is_user=False
                    )
            except Exception as e:
                logger.error(f"Error displaying error message: {e}", exc_info=True)

        def cleanup_worker():
            try:
                self.overview_worker = None  # Clear reference after completion
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")

        # Store worker as instance variable to prevent garbage collection
        self.overview_worker = OverviewWorker(get_overview_impl)
        self.overview_worker.result_ready.connect(handle_overview_result)
        self.overview_worker.error_occurred.connect(handle_overview_error)
        self.overview_worker.finished.connect(cleanup_worker)
        self.overview_worker.start()

    def show_session_recap(self):
        """Show session recap dialog with AI-powered coaching insights"""
        # Check if AI assistant is configured
        if not self.ai_assistant:
            QMessageBox.warning(
                self,
                "AI Assistant Not Configured",
                "AI assistant not configured. Please configure your API keys in Settings first.",
            )
            return

        try:
            game_name = (
                self.current_game.get("name", "Unknown Game")
                if self.current_game
                else "Unknown Game"
            )
            game_profile_id = getattr(self.ai_assistant, "current_game_profile_id", None)

            # Create and show session recap dialog
            dialog = SessionRecapDialog(
                parent=self,
                game_profile_id=game_profile_id,
                game_name=game_name,
                config=self.config,
            )
            dialog.exec()

            logger.info(f"Session recap dialog shown for {game_name}")

        except Exception as e:
            logger.error(f"Error showing session recap: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error showing session recap: {str(e)}")

    def open_advanced_settings(self):
        """Open the advanced settings dialog with keybinds, macros, and themes"""
        logger.info("Opening advanced settings dialog")

        dialog = TabbedSettingsDialog(
            parent=self,
            config=self.config,
            keybind_manager=self.keybind_manager,
            macro_manager=self.macro_manager,
            theme_manager=self.theme_manager,
        )

        # Connect signals
        dialog.keybinds_changed.connect(self.on_keybinds_updated)
        dialog.macros_changed.connect(self.on_macros_updated)
        dialog.theme_changed.connect(self.on_theme_updated)
        dialog.overlay_appearance_changed.connect(self.on_overlay_appearance_updated)
        dialog.provider_config_changed.connect(self.on_provider_config_updated)

        dialog.exec()

    def on_keybinds_updated(self, keybinds_dict: dict):
        """Handle keybinds being updated"""
        logger.info("Keybinds updated, re-registering all keybinds and callbacks")

        try:
            self.keybind_manager.load_from_dict(keybinds_dict)
        except Exception as e:
            logger.error(f"Failed to reload keybinds from dict: {e}")

        # Re-register callbacks with actual functions
        self.register_keybind_callbacks()

    def on_macros_updated(self, macros_dict: dict):
        """Handle macros being updated"""
        logger.info("Macros updated")
        # Reload macros
        self.macro_manager.load_from_dict(macros_dict)
        # Re-register macro keybinds
        self._register_macro_keybinds()

    def on_theme_updated(self, theme_dict: dict):
        """Handle theme being updated"""
        logger.info("Theme updated, applying to UI")
        # Reload theme
        self.theme_manager.load_from_dict(theme_dict)
        # Apply theme
        self.apply_theme()

    def on_overlay_appearance_updated(self, appearance_dict: dict):
        """Handle overlay appearance being updated"""
        logger.info("Overlay appearance updated")
        # Reload overlay appearance
        self.theme_manager.load_from_dict(appearance_dict)
        # Apply to overlay
        if hasattr(self, "overlay_window"):
            self.apply_overlay_appearance()

    def on_provider_config_updated(self, default_provider: str, credentials: dict):
        """Handle provider configuration being updated"""
        logger.info(f"Provider config updated: {default_provider}")
        if self.ai_assistant:
            self.ai_assistant.provider = default_provider
        # Reload the AI router's provider instances with updated API keys
        if hasattr(self.ai_assistant, "router"):
            self.ai_assistant.router.reload_providers()
            logger.info("AI router providers reloaded with updated configuration")

    def apply_theme(self):
        """Apply current theme to the main window"""
        try:
            base_stylesheet = self.theme_manager.generate_stylesheet(for_overlay=False)
            custom_stylesheet = self._load_custom_stylesheet()
            self.setStyleSheet(base_stylesheet + "\n" + custom_stylesheet)
            logger.info("Theme applied to main window")
        except Exception as e:
            logger.error(f"Error applying theme: {e}")

    def _load_custom_stylesheet(self) -> str:
        custom_path = Path(__file__).parent / "ui" / "omnix.qss"
        if custom_path.exists():
            try:
                return custom_path.read_text(encoding="utf-8")
            except OSError as exc:
                logger.error(f"Failed to read custom stylesheet: {exc}")
        return ""

    def _apply_entry_animations(self, widgets: list[QWidget]):
        delay = 0
        for widget in widgets:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)

            animation = QPropertyAnimation(effect, b"opacity", widget)
            animation.setDuration(400)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutQuad)

            def start_anim(anim=animation):
                anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

            QTimer.singleShot(delay, start_anim)
            delay += 80

    def apply_overlay_appearance(self):
        """Apply current appearance settings to the overlay window"""
        try:
            if hasattr(self, "overlay_window"):
                # Apply theme stylesheet
                stylesheet = self.theme_manager.generate_stylesheet(for_overlay=True)
                self.overlay_window.setStyleSheet(stylesheet)

                # Apply position and size
                overlay_app = self.theme_manager.overlay_appearance
                screen = QApplication.primaryScreen().geometry()

                x, y = overlay_app.get_position_preset_coords(screen.width(), screen.height())
                self.overlay_window.move(x, y)
                self.overlay_window.resize(overlay_app.width, overlay_app.height)
                self.overlay_window.setWindowOpacity(overlay_app.opacity)

                logger.info("Overlay appearance applied")
        except Exception as e:
            logger.error(f"Error applying overlay appearance: {e}")

    def quit_application(self):
        """Quit the application cleanly"""
        logger.info("Quitting application")
        self.cleanup()
        QApplication.quit()

    def cleanup(self):
        """Cleanup resources before closing"""
        logger.info("Cleaning up resources")

        # The chat_widget is on the overlay_window, not MainWindow.
        # We also add checks to ensure overlay_window and chat_widget exist.
        chat_widget_to_clean = None
        if hasattr(self, "overlay_window") and hasattr(self.overlay_window, "chat_widget"):
            chat_widget_to_clean = self.overlay_window.chat_widget

        # Stop any active AI worker threads
        if (
            chat_widget_to_clean
            and hasattr(chat_widget_to_clean, "ai_worker")
            and chat_widget_to_clean.ai_worker
        ):
            if chat_widget_to_clean.ai_worker.isRunning():
                chat_widget_to_clean.ai_worker.wait(2000)
                if chat_widget_to_clean.ai_worker.isRunning():
                    logger.warning("AI worker did not stop gracefully, terminating")
                    chat_widget_to_clean.ai_worker.terminate()

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

                # Show welcome message in overlay chat if available
                if hasattr(self, "overlay_window") and self.overlay_window:
                    self.overlay_window.chat_widget.add_message(
                        "System",
                        "Welcome to Omnix AI Assistant! 🎮\n\n"
                        "To get started, please configure your API keys in the Settings dialog.\n\n"
                        "Click the Settings button to enter your OpenAI or Anthropic API key.",
                        is_user=False,
                    )

                # Schedule settings dialog to open after a short delay (so window is fully shown)
                QTimer.singleShot(500, self.open_advanced_settings)

    def closeEvent(self, event):
        """
        Handle window close event by minimizing to system tray instead of quitting

        Args:
            event: QCloseEvent to be handled
        """
        # Stop game watcher when minimizing to tray
        try:
            if hasattr(self, "game_watcher") and self.game_watcher:
                self.game_watcher.stop_watching()
                logger.info("Game watcher stopped")
        except Exception as e:
            logger.error(f"Error stopping game watcher: {e}")

        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Gaming AI Assistant",
            "Application minimized to tray. Press Ctrl+Shift+G to toggle overlay.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )
        logger.info("Window close event - minimized to tray")


def run_gui(ai_assistant, config, credential_store, design_system_instance):
    """
    Initialize and run the GUI application

    Args:
        ai_assistant: AI assistant service instance (can be None if no credentials)
        config: Configuration instance
        credential_store: Credential store instance
        design_system_instance: Design system instance for styling
    """
    try:
        # Install Qt message handler BEFORE creating QApplication
        qInstallMessageHandler(qt_message_handler)
        logger.info("Qt message handler installed")

        app = QApplication(sys.argv)
        app.setApplicationName("Gaming AI Assistant")

        # Apply design system stylesheet to the entire application
        stylesheet = design_system_instance.generate_complete_stylesheet()
        app.setStyleSheet(stylesheet)
        logger.info("Design system stylesheet applied to application")

        # Check if this is first run (no credentials configured)
        if not config.is_configured():
            logger.info("No API keys configured - showing setup wizard")

            from setup_wizard import SetupWizard

            # Show setup wizard
            wizard = SetupWizard()

            def on_wizard_complete(default_provider, credentials):
                """Handle wizard completion"""
                logger.info(
                    f"Setup wizard completed: provider={default_provider}, credentials={list(credentials.keys())}"
                )

                # Save provider to .env
                Config.save_to_env(provider=default_provider)

                # Reinitialize config to load new credentials
                nonlocal config, ai_assistant
                config = Config(require_keys=False)

                # Initialize AI assistant with new credentials
                from ai_assistant import AIAssistant

                ai_assistant = AIAssistant(
                    provider=config.ai_provider,
                    api_key=config.get_api_key(),
                    session_tokens=config.session_tokens.get(config.ai_provider),
                )

                logger.info("AI assistant reinitialized after setup")

            wizard.setup_complete.connect(on_wizard_complete)
            result = wizard.exec()

            if result != QDialog.DialogCode.Accepted:
                # User cancelled setup wizard
                logger.info("Setup wizard cancelled by user")
                QMessageBox.warning(
                    None,
                    "Setup Required",
                    "API key configuration is required to use the Gaming AI Assistant.\n\n"
                    "The application will now exit. Please run it again when you're ready to set up.",
                )
                return

        # Create and show main window
        try:
            logger.info("Creating MainWindow...")
            window = MainWindow(
                ai_assistant,
                config,
                credential_store,
                design_system_instance,
            )
            logger.info("MainWindow created successfully")

            logger.info("Showing MainWindow...")
            window.show()
            logger.info("MainWindow shown successfully")

            # Handle application quit
            app.aboutToQuit.connect(window.cleanup)

        except Exception as e:
            logger.error("=" * 70, exc_info=True)
            logger.error(f"FAILED TO CREATE/SHOW MAINWINDOW: {e}", exc_info=True)
            logger.error("=" * 70)
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
            raise

        logger.info("Starting Qt event loop...")
        try:
            exit_code = app.exec()
            logger.info(f"Qt event loop exited with code: {exit_code}")
            sys.exit(exit_code)
        except Exception as e:
            logger.error("=" * 70)
            logger.error(f"EXCEPTION IN QT EVENT LOOP: {e}", exc_info=True)
            logger.error("=" * 70)
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
            raise

    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"GUI INITIALIZATION ERROR: {e}", exc_info=True)
        logger.error("=" * 70)
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    # Module should be run from main.py with proper dependencies
    print("GUI module - run from main.py")
