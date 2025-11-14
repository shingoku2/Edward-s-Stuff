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
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QShortcut, QIcon, QPixmap, QPainter, QColor
from typing import Optional, Dict
import os
import webbrowser

from credential_store import CredentialStore, CredentialStoreError
from config import Config
from login_dialog import LoginDialog
from keybind_manager import KeybindManager, Keybind, DEFAULT_KEYBINDS
from macro_manager import MacroManager, MacroActionType
from macro_runner import MacroRunner
from theme_manager import ThemeManager, DEFAULT_DARK_THEME
from settings_dialog import TabbedSettingsDialog
from session_recap_dialog import SessionRecapDialog
from game_watcher import get_game_watcher
from game_profile import get_profile_store

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


class SessionEventBridge(QObject):
    """Bridge authentication events from background threads to the GUI."""

    session_event = pyqtSignal(str, str, dict)

    def emit_event(self, provider: str, action: str, payload: Dict[str, str]):
        self.session_event.emit(provider, action, payload)


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

                # Check if this is a new game by comparing name and process (ignore timestamp)
                is_new_game = False
                if game and self.current_game:
                    # Compare only name and process, not the entire dict (which includes timestamp)
                    is_new_game = (
                        game.get('name') != self.current_game.get('name') or
                        game.get('process') != self.current_game.get('process')
                    )
                elif game and not self.current_game:
                    # First game detection
                    is_new_game = True

                if is_new_game:
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


class OverlayWindow(QWidget):
    """Frameless in-game overlay window with drag/resize/minimize functionality"""

    def __init__(self, ai_assistant, config, parent=None):
        super().__init__(parent)
        self.ai_assistant = ai_assistant
        self.config = config

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

    def init_ui(self):
        """Initialize overlay UI with frameless design"""
        self.setWindowTitle("Gaming AI Assistant - Overlay")

        # Make window frameless and always on top
        # Use Window type (not Tool) to prevent hiding when focus changes
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        # Set window position and size from config
        self.setGeometry(
            self.config.overlay_x,
            self.config.overlay_y,
            self.config.overlay_width,
            self.config.overlay_height
        )

        # Enable mouse tracking for resize grips
        self.setMouseTracking(True)

        # Apply dark theme with transparency
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(30, 30, 30, {int(self.config.overlay_opacity * 255)});
                color: #ffffff;
                border: 2px solid #14b8a6;
                border-radius: 8px;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with title and minimize button
        header = self.create_header()
        main_layout.addWidget(header)

        # Chat widget
        self.chat_widget = ChatWidget(self.ai_assistant)
        main_layout.addWidget(self.chat_widget)

        self.setLayout(main_layout)

        logger.info("Overlay window initialized")

    def create_header(self) -> QWidget:
        """Create custom header with title and window controls"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #3a3a3a;
                padding: 8px;
            }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)

        # Title
        title_layout = QVBoxLayout()
        title_label = QLabel("🎮 Gaming AI Assistant")
        title_label.setStyleSheet("""
            QLabel {
                color: #14b8a6;
                font-size: 14pt;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title_label)

        subtitle = QLabel("In-Game Overlay")
        subtitle.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 9pt;
                background: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(subtitle)

        main_layout.addLayout(title_layout)
        main_layout.addStretch()

        # Window control buttons
        controls_layout = QHBoxLayout()

        # Minimize button
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

        # Close button (hides overlay, doesn't quit app)
        close_button = QPushButton("×")
        close_button.setToolTip("Hide Overlay (Press hotkey to show again)")
        close_button.clicked.connect(self.hide)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 18pt;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """)
        controls_layout.addWidget(close_button)

        main_layout.addLayout(controls_layout)

        header.setLayout(main_layout)
        return header

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
        from src.config import Config
        geometry = self.geometry()
        Config.save_to_env(
            provider=self.config.ai_provider,
            overlay_hotkey=self.config.overlay_hotkey,
            check_interval=self.config.check_interval,
            overlay_x=geometry.x(),
            overlay_y=geometry.y(),
            overlay_width=geometry.width(),
            overlay_height=geometry.height(),
            overlay_minimized=self.is_minimized,
            overlay_opacity=self.config.overlay_opacity
        )
        logger.info(f"Saved overlay state: pos=({geometry.x()}, {geometry.y()}), size=({geometry.width()}x{geometry.height()})")

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
        """Handle close event by hiding instead of destroying"""
        self.save_window_state()
        self.hide()
        event.ignore()


class MainWindow(QMainWindow):
    """Main application window with game detection and AI chat interface"""

    def __init__(
        self,
        game_detector,
        ai_assistant,
        info_scraper,
        config,
        credential_store,
    ):
        super().__init__()
        self.game_detector = game_detector
        self.ai_assistant = ai_assistant  # Can be None if no API keys configured
        self.info_scraper = info_scraper
        self.config = config
        self.credential_store = credential_store

        self.current_game = None
        self.detection_thread = None

        # Worker threads for button actions (prevents garbage collection crashes)
        self.tips_worker = None
        self.overview_worker = None

        # Track if this is first show (for auto-opening settings)
        self.first_show = True

        # Initialize managers for advanced features
        self.init_managers()

        # Create overlay window (but don't show it yet)
        # Note: parent=None to prevent overlay from hiding when main window loses focus
        self.overlay_window = OverlayWindow(ai_assistant, config, parent=None)

        # Initialize game watcher for game detection and profile switching
        self.game_watcher = get_game_watcher(check_interval=config.check_interval)
        self.profile_store = get_profile_store()

        self.session_event_bridge = SessionEventBridge()
        self.session_event_bridge.session_event.connect(self.on_session_event)

        if self.ai_assistant:
            self.ai_assistant.register_session_refresh_handler(
                self.session_event_bridge.emit_event
            )

        self.init_ui()
        self.start_game_detection()
        self.start_game_watcher()

        # Start global hotkey listener after UI is ready
        self.start_hotkey_listener()

    def init_managers(self):
        """Initialize keybind, macro, and theme managers"""
        logger.info("Initializing advanced feature managers...")

        # Initialize KeybindManager
        self.keybind_manager = KeybindManager()

        # Load keybinds from config and register them (creates HotKey objects)
        if self.config.keybinds:
            for action, keybind_data in self.config.keybinds.items():
                try:
                    keybind = Keybind.from_dict(keybind_data)
                    # Register with dummy callback - real callbacks set later in register_keybind_callbacks()
                    self.keybind_manager.register_keybind(keybind, lambda: None, override=True)
                except Exception as e:
                    logger.error(f"Failed to load keybind {action}: {e}")
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
            enabled=self.config.macros_enabled,
            macro_manager=self.macro_manager
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
            self.keybind_manager.callbacks["clear_chat"] = lambda: self.chat_widget.clear_chat() if hasattr(self, 'chat_widget') else None

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
        self.macro_manager.register_action_handler(MacroActionType.SHOW_OVERVIEW.value, self.get_overview)
        self.macro_manager.register_action_handler(MacroActionType.CLEAR_CHAT.value,
            lambda: self.chat_widget.clear_chat() if hasattr(self, 'chat_widget') else None)
        self.macro_manager.register_action_handler(MacroActionType.TOGGLE_OVERLAY.value, self.toggle_overlay_visibility)
        self.macro_manager.register_action_handler(MacroActionType.CLOSE_OVERLAY.value,
            lambda: self.overlay_window.hide() if hasattr(self, 'overlay_window') else None)
        self.macro_manager.register_action_handler(MacroActionType.OPEN_SETTINGS.value, self.open_advanced_settings)

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

                    logger.debug(f"Registered keybind callback for macro: {macro.name} (ID: {macro.id})")

            logger.info(f"Registered {len([m for m in all_macros if m.enabled])} macro keybind callbacks")

        except Exception as e:
            logger.error(f"Error registering macro keybinds: {e}", exc_info=True)

    def toggle_overlay_visibility(self):
        """Toggle overlay visibility"""
        if hasattr(self, 'overlay_window'):
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
            QTimer.singleShot(0, lambda: QMessageBox.information(
                self,
                "Session Expired",
                message or "Session expired. Please sign in again.",
            ))
            QTimer.singleShot(250, self.open_advanced_settings)

    def init_ui(self):
        """Initialize the main window UI components and styling"""
        self.setWindowTitle("Gaming AI Assistant")

        # Set default window size (normal app window, not overlay)
        self.resize(900, 700)

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

        self.recap_button = QPushButton("📊 Session Recap")
        self.recap_button.clicked.connect(self.show_session_recap)
        self.recap_button.setEnabled(False)

        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.open_advanced_settings)

        self.advanced_settings_button = QPushButton("🎛️ Advanced Settings")
        self.advanced_settings_button.clicked.connect(self.open_advanced_settings)

        # Apply styling to action buttons
        for button in [self.tips_button, self.overview_button, self.recap_button]:
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
        for button in [self.settings_button, self.advanced_settings_button]:
            button.setStyleSheet("""
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
        actions_layout.addWidget(self.advanced_settings_button)

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
        """Toggle overlay window visibility between shown and hidden states"""
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
            logger.info("Overlay hidden")
        else:
            self.overlay_window.show()
            self.overlay_window.activateWindow()
            logger.info("Overlay shown")

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
        self.recap_button.setEnabled(True)

        # Update AI assistant context with current game
        if self.ai_assistant:
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
        self.recap_button.setEnabled(False)

        logger.info("Game lost event handled")

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
            logger.info(f"GameWatcher detected game change: {game_name} (profile: {profile.id})")

            # Update overlay title with current game
            if self.overlay_window:
                self.overlay_window.setWindowTitle(f"Gaming Copilot - {game_name}")

            # Switch AI assistant to this game's profile
            if self.ai_assistant:
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

            # Update overlay title
            if self.overlay_window:
                self.overlay_window.setWindowTitle("Gaming Copilot")

            # Clear AI assistant profile
            if self.ai_assistant:
                self.ai_assistant.clear_game_profile()
                logger.info("AI Assistant profile cleared")

        except Exception as e:
            logger.error(f"Error handling game close: {e}")

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

    def show_session_recap(self):
        """Show session recap dialog with AI-powered coaching insights"""
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

        try:
            game_name = self.current_game.get('name', 'Unknown Game')
            game_profile_id = getattr(self.ai_assistant, 'current_game_profile_id', None)

            # Create and show session recap dialog
            dialog = SessionRecapDialog(
                parent=self,
                game_profile_id=game_profile_id,
                game_name=game_name,
                config=self.config
            )
            dialog.exec()

            logger.info(f"Session recap dialog shown for {game_name}")

        except Exception as e:
            logger.error(f"Error showing session recap: {e}", exc_info=True)
            self.chat_widget.add_message(
                "System",
                f"Error showing session recap: {str(e)}",
                is_user=False
            )

    def open_advanced_settings(self):
        """Open the advanced settings dialog with keybinds, macros, and themes"""
        logger.info("Opening advanced settings dialog")

        dialog = TabbedSettingsDialog(
            parent=self,
            config=self.config,
            keybind_manager=self.keybind_manager,
            macro_manager=self.macro_manager,
            theme_manager=self.theme_manager
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

        # Clear existing keybinds and hotkeys
        for action in list(self.keybind_manager.keybinds.keys()):
            self.keybind_manager.unregister_keybind(action)

        # Re-register all keybinds (creates HotKey objects)
        for action, keybind_data in keybinds_dict.items():
            try:
                keybind = Keybind.from_dict(keybind_data)
                self.keybind_manager.register_keybind(keybind, lambda: None, override=True)
            except Exception as e:
                logger.error(f"Failed to reload keybind {action}: {e}")

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
        if hasattr(self, 'overlay_window'):
            self.apply_overlay_appearance()

    def on_provider_config_updated(self, default_provider: str, credentials: dict):
        """Handle provider configuration being updated"""
        logger.info(f"Provider config updated: {default_provider}")
        # Reload the AI router's provider instances with updated API keys
        if hasattr(self.ai_assistant, 'router'):
            self.ai_assistant.router.reload_providers()
            logger.info("AI router providers reloaded with updated configuration")

    def apply_theme(self):
        """Apply current theme to the main window"""
        try:
            stylesheet = self.theme_manager.generate_stylesheet(for_overlay=False)
            self.setStyleSheet(stylesheet)
            logger.info("Theme applied to main window")
        except Exception as e:
            logger.error(f"Error applying theme: {e}")

    def apply_overlay_appearance(self):
        """Apply current appearance settings to the overlay window"""
        try:
            if hasattr(self, 'overlay_window'):
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
                QTimer.singleShot(500, self.open_advanced_settings)

    def closeEvent(self, event):
        """
        Handle window close event by minimizing to system tray instead of quitting

        Args:
            event: QCloseEvent to be handled
        """
        # Stop game watcher when minimizing to tray
        try:
            if hasattr(self, 'game_watcher') and self.game_watcher:
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
            2000
        )
        logger.info("Window close event - minimized to tray")


def run_gui(game_detector, ai_assistant, info_scraper, config, credential_store):
    """
    Initialize and run the GUI application

    Args:
        game_detector: Game detection service instance
        ai_assistant: AI assistant service instance (can be None if no credentials)
        info_scraper: Information scraper service instance
        config: Configuration instance
        credential_store: Credential store instance
    """
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Gaming AI Assistant")

        # Check if this is first run (no credentials configured)
        if not config.is_configured():
            logger.info("No API keys configured - showing setup wizard")

            from setup_wizard import SetupWizard

            # Show setup wizard
            wizard = SetupWizard()

            def on_wizard_complete(default_provider, credentials):
                """Handle wizard completion"""
                logger.info(f"Setup wizard completed: provider={default_provider}, credentials={list(credentials.keys())}")

                # Save provider to .env
                Config.save_to_env(
                    provider=default_provider
                )

                # Reinitialize config to load new credentials
                nonlocal config, ai_assistant
                config = Config(require_keys=False)

                # Initialize AI assistant with new credentials
                from ai_assistant import AIAssistant
                ai_assistant = AIAssistant(
                    provider=config.ai_provider,
                    api_key=config.get_api_key(),
                    session_tokens=config.session_tokens.get(config.ai_provider)
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
                    "The application will now exit. Please run it again when you're ready to set up."
                )
                return

        # Create and show main window
        window = MainWindow(
            game_detector,
            ai_assistant,
            info_scraper,
            config,
            credential_store,
        )
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
