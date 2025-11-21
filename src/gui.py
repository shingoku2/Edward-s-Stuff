"""
Omnix GUI Module
================

PyQt6 interface styled with the Omnix QSS theme. Provides the main dashboard,
chat panel, settings panel, and in-game overlay window matching the reference
visual design.
"""

from __future__ import annotations

import logging
import math
import sys
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import QEvent, QPoint, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import Config
from credential_store import CredentialStore
from ui.design_system import OmnixDesignSystem, design_system
from keybind_manager import KeybindManager
from macro_manager import MacroManager
from theme_compat import ThemeManager
from settings_dialog import TabbedSettingsDialog

logger = logging.getLogger(__name__)


def _load_qss() -> str:
    """Load the legacy Omnix QSS stylesheet."""
    qss_path = Path(__file__).parent / "ui" / "omnix.qss"
    if not qss_path.exists():
        return ""
    return qss_path.read_text(encoding="utf-8")


class AIWorkerThread(QThread):
    """Background worker that calls the AI assistant without blocking the UI."""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, assistant, question: str, game_context: Optional[Dict] = None):
        super().__init__()
        self.assistant = assistant
        self.question = question
        self.game_context = game_context or {}

    def run(self) -> None:  # pragma: no cover - exercised via tests with monkeypatch
        try:
            if self.assistant is None:
                response = "Omnix is standing by. Configure an AI provider to begin."
            else:
                response = self.assistant.ask_question(self.question, game_context=self.game_context)
            self.finished.emit(response or "")
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("AI worker failed")
            self.error.emit(str(exc))


class NeonCard(QFrame):
    """Frameless card that maps to the QSS `NeonCard` selector."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("NeonCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


class NeonButton(QPushButton):
    """Custom button that exposes `variant` and `active` state for QSS styling."""

    def __init__(self, text: str, variant: Optional[str] = None, checkable: bool = False, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if variant:
            self.setProperty("variant", variant)
        self.setCheckable(checkable)
        self.toggled.connect(self._sync_state)
        self._sync_state(self.isChecked())

    def _sync_state(self, checked: bool) -> None:
        self.setProperty("active", "true" if checked else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class ChatWidget(QWidget):
    """Neon-styled chat surface with threaded AI responses."""

    def __init__(self, assistant, title: str = "Chat", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.assistant = assistant
        self.ai_worker: Optional[AIWorkerThread] = None

        self.setObjectName("ChatWidget")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        header = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("ChatTitle")
        subtitle = QLabel("How can I help?")
        subtitle.setObjectName("ChatSubtitle")
        header.addWidget(title_label)
        header.addWidget(subtitle)
        main_layout.addLayout(header)

        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setObjectName("ChatDivider")
        main_layout.addWidget(divider)

        self._build_message_list(main_layout)
        self._build_quick_responses(main_layout)
        self._build_input_area(main_layout)

        self._seed_intro()

    def _build_message_list(self, main_layout: QVBoxLayout) -> None:
        scroll = QScrollArea()
        scroll.setObjectName("ChatScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self.messages_layout = QVBoxLayout(container)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

    def _build_quick_responses(self, main_layout: QVBoxLayout) -> None:
        title = QLabel("Quick responses")
        title.setObjectName("SectionTitle")
        main_layout.addWidget(title)

        row = QHBoxLayout()
        for text in ["Focus mode", "Assist call outs", "Cooldown alerts"]:
            button = NeonButton(text, variant="toggle", checkable=True)
            button.clicked.connect(lambda _, t=text: self._send_message(t))
            row.addWidget(button)
        row.addStretch()
        main_layout.addLayout(row)

    def _build_input_area(self, main_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(8)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Omnix...")
        self.input_field.returnPressed.connect(self._on_submit)
        row.addWidget(self.input_field, 1)

        self.send_button = NeonButton("Send")
        self.send_button.clicked.connect(self._on_submit)
        row.addWidget(self.send_button)

        main_layout.addLayout(row)

    def _seed_intro(self) -> None:
        self.add_message("AI", "Hello!")
        self.add_message("AI", "Hi! How can I assist you?")
        self.add_message("AI", "Sure, analyzing the game now...", role="ai")

    def add_message(self, sender: str, message: str, role: str = "ai") -> None:
        bubble = QFrame()
        bubble.setProperty("role", "ai" if role.lower() in {"ai", "omnix"} else "user")
        bubble.setObjectName("ChatBubbleAI" if bubble.property("role") == "ai" else "ChatBubbleUser")

        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(10, 8, 10, 8)
        sender_label = QLabel(sender)
        sender_label.setObjectName("ChatSender")
        text_label = QLabel(message)
        text_label.setWordWrap(True)
        text_label.setObjectName("ChatText")
        layout.addWidget(sender_label)
        layout.addWidget(text_label)

        insert_index = max(self.messages_layout.count() - 1, 0)
        self.messages_layout.insertWidget(insert_index, bubble)

    def _on_submit(self) -> None:
        text = self.input_field.text().strip()
        if not text:
            return
        self._send_message(text)

    def _send_message(self, text: str) -> None:
        self.add_message("You", text, role="user")
        self.input_field.clear()
        self.send_button.setEnabled(False)

        self.ai_worker = AIWorkerThread(self.assistant, text)
        self.ai_worker.finished.connect(self._handle_response)
        self.ai_worker.error.connect(self._handle_error)
        self.ai_worker.start()

    def _handle_response(self, response: str) -> None:
        self.add_message("Omnix", response, role="ai")
        self.send_button.setEnabled(True)
        self.ai_worker = None

    def _handle_error(self, message: str) -> None:
        self.add_message("Error", message, role="ai")
        self.send_button.setEnabled(True)
        self.ai_worker = None


class HexStatusWidget(QWidget):
    """Custom painted hexagon status indicator for the central card."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(260, 260)
        self.game_label = "CS:GO"
        self.status_text = "Online"
        icon_path = (Path(__file__).parent / ".." / "OMNIX-LOGO-PLAIN.png").resolve()
        pixmap = QPixmap(str(icon_path)) if icon_path.exists() else QPixmap()
        self.icon = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) if not pixmap.isNull() else pixmap

    def paintEvent(self, event: QEvent) -> None:  # pragma: no cover - visual only
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)

        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 2 - 12
        pen = QPen(QColor("#13d5ff"))
        pen.setWidth(3)
        painter.setPen(pen)

        points = []
        for i in range(6):
            angle = 60 * i - 30
            radians = math.radians(angle)
            x = center.x() + radius * 0.9 * math.cos(radians)
            y = center.y() + radius * 0.9 * math.sin(radians)
            points.append(QPoint(int(x), int(y)))
        painter.drawPolygon(points)

        painter.setPen(QColor("#ff4e4e"))
        painter.setFont(QFont("Orbitron", 18, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, self.game_label)

        if not self.icon.isNull():
            icon_rect = self.rect().adjusted(40, 50, -40, -70)
            painter.drawPixmap(icon_rect, self.icon)

        painter.setPen(QColor("#63f5a4"))
        painter.setFont(QFont("Rajdhani", 12, QFont.Weight.DemiBold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, self.status_text)


class GameStatusPanel(NeonCard):
    """Central card showing game detection and statistics."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("GameStatusPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Game Detected")
        title.setObjectName("SectionTitle")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.hex_widget = HexStatusWidget()
        self.hex_widget.setObjectName("HexWidget")
        layout.addWidget(self.hex_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        stats = QGridLayout()
        stats.setSpacing(10)
        self.kd_label = self._build_stat(stats, 0, "K/D", "1.52")
        self.match_label = self._build_stat(stats, 1, "MATCH", "24")
        self.wins_label = self._build_stat(stats, 2, "WINS", "152")
        layout.addLayout(stats)

    def _build_stat(self, layout: QGridLayout, column: int, label_text: str, value: str) -> QLabel:
        container = QFrame()
        container.setObjectName("StatContainer")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(8, 8, 8, 8)
        lbl = QLabel(label_text)
        lbl.setObjectName("StatLabel")
        val = QLabel(value)
        val.setObjectName("StatValue")
        vbox.addWidget(lbl)
        vbox.addWidget(val)
        layout.addWidget(container, 0, column)
        return val


class SettingsPanel(NeonCard):
    """Right side panel with quick settings and provider selection."""

    settings_requested = pyqtSignal(int)  # Signal to open settings dialog at specific tab

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Quick Settings")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self.menu_buttons: Dict[str, NeonButton] = {}
        menu = QVBoxLayout()

        # Quick access buttons that open full settings dialog
        settings_items = [
            ("AI Providers", 0),  # Tab index 0
            ("Game Profiles", 1),  # Tab index 1
            ("Knowledge Packs", 2),  # Tab index 2
            ("Macros", 4),  # Tab index 4
        ]

        for name, tab_index in settings_items:
            button = NeonButton(name, variant="toggle")
            button.clicked.connect(lambda _, idx=tab_index: self.settings_requested.emit(idx))
            menu.addWidget(button)
            self.menu_buttons[name] = button

        layout.addLayout(menu)
        layout.addStretch()

        provider_label = QLabel("AI Provider")
        provider_label.setObjectName("SectionTitle")
        layout.addWidget(provider_label)

        provider_row = QHBoxLayout()
        self.provider_openai = NeonButton("OpenAI", variant="provider", checkable=True)
        self.provider_anthropic = NeonButton("Anthropic", variant="provider", checkable=True)
        self.provider_openai.clicked.connect(lambda: self._open_providers_settings())
        self.provider_anthropic.clicked.connect(lambda: self._open_providers_settings())
        provider_row.addWidget(self.provider_openai)
        provider_row.addWidget(self.provider_anthropic)
        layout.addLayout(provider_row)

        layout.addStretch()

    def _open_providers_settings(self) -> None:
        """Open full settings dialog at providers tab"""
        self.settings_requested.emit(0)  # Tab index 0 is AI Providers


class OverlayWindow(QWidget):
    """Frameless always-on-top overlay with translucent chat."""

    def __init__(self, assistant, config: Config, ds: OmnixDesignSystem):
        super().__init__()
        self.assistant = assistant
        self.config = config
        self.design_system = ds
        self.minimized = getattr(config, "overlay_minimized", False)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setGeometry(
            int(getattr(config, "overlay_x", 100)),
            int(getattr(config, "overlay_y", 100)),
            int(getattr(config, "overlay_width", 420)),
            int(getattr(config, "overlay_height", 360)),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.chat = ChatWidget(assistant, title="Overlay")
        layout.addWidget(self.chat)

        overlay_styles = ds.generate_overlay_stylesheet(getattr(config, "overlay_opacity", 0.8)) if ds else ""
        self.setStyleSheet(overlay_styles + "\n" + _load_qss())

        if self.minimized:
            self.toggle_minimize()

    def moveEvent(self, event: QEvent) -> None:
        """Save overlay position when moved"""
        super().moveEvent(event)
        self.config.overlay_x = self.x()
        self.config.overlay_y = self.y()
        # Don't save immediately to avoid excessive I/O during drag
        logger.debug(f"Overlay moved to ({self.x()}, {self.y()})")

    def resizeEvent(self, event: QEvent) -> None:
        """Save overlay size when resized"""
        super().resizeEvent(event)
        if not self.minimized:
            self.config.overlay_width = self.width()
            self.config.overlay_height = self.height()
            logger.debug(f"Overlay resized to ({self.width()}x{self.height()})")

    def closeEvent(self, event: QEvent) -> None:
        """Save config when overlay is closed"""
        super().closeEvent(event)
        self._save_overlay_config()

    def _save_overlay_config(self) -> None:
        """Persist overlay configuration to .env"""
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
                overlay_opacity=self.config.overlay_opacity
            )
            logger.info("Overlay configuration saved")
        except Exception as e:
            logger.error(f"Failed to save overlay config: {e}")

    def toggle_minimize(self) -> None:
        self.minimized = not self.minimized
        self.config.overlay_minimized = self.minimized
        if self.minimized:
            self._saved_height = self.height()
            self.chat.setVisible(False)
            self.setFixedHeight(80)
        else:
            self.chat.setVisible(True)
            self.setFixedHeight(getattr(self, "_saved_height", self.sizeHint().height()))


class MainWindow(QMainWindow):
    """Omnix main dashboard window."""

    def __init__(
        self,
        ai_assistant,
        config: Config,
        credential_store: CredentialStore,
        design_system: OmnixDesignSystem = design_system,
        game_detector=None
    ):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.config = config
        self.credential_store = credential_store
        self.design_system = design_system or OmnixDesignSystem()
        self.game_detector = game_detector
        self.current_game = None

        self.setWindowTitle("Omnix - All Knowing AI Companion")
        self.resize(1280, 760)

        base_styles = self.design_system.generate_complete_stylesheet()
        self.setStyleSheet(base_styles + "\n" + _load_qss())

        # Initialize managers for settings dialog
        self.keybind_manager = KeybindManager(config)
        self.macro_manager = MacroManager(config)
        self.theme_manager = ThemeManager()

        # Initialize settings dialog (but don't show it yet)
        self.settings_dialog = None

        self.overlay_window = OverlayWindow(ai_assistant, config, self.design_system)

        central = QWidget()
        central.setObjectName("MainContainer")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_main_grid())
        layout.addLayout(self._build_footer())

        # Start game detection if available
        if self.game_detector:
            self._start_game_detection()

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(6)
        title = QLabel("OMNIX")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("ALL KNOWING AI COMPANION")
        subtitle.setObjectName("BrandSubtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        header.addStretch()
        return header

    def _build_main_grid(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        self.chat_panel = NeonCard()
        chat_layout = QVBoxLayout(self.chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.addWidget(ChatWidget(self.ai_assistant))
        row.addWidget(self.chat_panel, 2)

        self.game_status_panel = GameStatusPanel()
        row.addWidget(self.game_status_panel, 2)

        self.settings_panel = SettingsPanel()
        self.settings_panel.settings_requested.connect(self._open_settings_at_tab)
        row.addWidget(self.settings_panel, 2)

        return row

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setSpacing(10)

        overlay_button = NeonButton("Overlay", variant="primary")
        overlay_button.setObjectName("OverlayButton")
        overlay_button.clicked.connect(self._toggle_overlay)
        footer.addWidget(overlay_button)

        settings_button = NeonButton("Settings")
        settings_button.setObjectName("FooterSettingsButton")
        settings_button.clicked.connect(self._open_settings)
        footer.addWidget(settings_button)

        footer.addStretch()
        return footer

    def _toggle_overlay(self) -> None:
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
        else:
            self.overlay_window.show()
            self.overlay_window.raise_()

    def _open_settings(self) -> None:
        """Open the comprehensive settings dialog"""
        self._open_settings_at_tab(0)  # Default to first tab

    def _open_settings_at_tab(self, tab_index: int) -> None:
        """Open settings dialog at specific tab"""
        if self.settings_dialog is None:
            self.settings_dialog = TabbedSettingsDialog(
                self,
                self.config,
                self.keybind_manager,
                self.macro_manager,
                self.theme_manager
            )
            # Connect settings dialog signals
            self.settings_dialog.settings_saved.connect(self._on_settings_saved)
            self.settings_dialog.provider_config_changed.connect(self._on_provider_changed)

        self.settings_dialog.set_current_tab(tab_index)
        self.settings_dialog.exec()

    def _on_settings_saved(self, settings: dict) -> None:
        """Handle settings saved from dialog"""
        logger.info("Settings saved from dialog")
        # Update UI to reflect new settings
        if 'default_provider' in settings:
            self._update_provider_display(settings['default_provider'])

    def _on_provider_changed(self, provider: str, credentials: dict) -> None:
        """Handle AI provider configuration change"""
        logger.info(f"Provider changed to: {provider}")
        self._update_provider_display(provider)
        # Reinitialize AI assistant if needed
        # This would require restarting or recreating the assistant

    def _update_provider_display(self, provider: str) -> None:
        """Update provider button states in settings panel"""
        self.settings_panel.provider_openai.setChecked(provider == "openai")
        self.settings_panel.provider_anthropic.setChecked(provider == "anthropic")

    def _start_game_detection(self) -> None:
        """Start periodic game detection"""
        from PyQt6.QtCore import QTimer
        self.game_check_timer = QTimer()
        self.game_check_timer.timeout.connect(self._check_for_game)
        self.game_check_timer.start(5000)  # Check every 5 seconds
        # Do initial check
        self._check_for_game()

    def _check_for_game(self) -> None:
        """Check if a game is running and update UI"""
        if not self.game_detector:
            return

        game = self.game_detector.detect_running_game()
        if game and game.get('name') != self.current_game:
            self.current_game = game.get('name')
            self._update_game_status(game)
            logger.info(f"Game detected: {self.current_game}")
        elif not game and self.current_game:
            self.current_game = None
            self._clear_game_status()
            logger.info("No game detected")

    def _update_game_status(self, game: dict) -> None:
        """Update the game status panel with detected game"""
        if hasattr(self.game_status_panel, 'hex_widget'):
            self.game_status_panel.hex_widget.game_label = game.get('name', 'Unknown')
            self.game_status_panel.hex_widget.status_text = "Detected"
            self.game_status_panel.hex_widget.update()

    def _clear_game_status(self) -> None:
        """Clear the game status display"""
        if hasattr(self.game_status_panel, 'hex_widget'):
            self.game_status_panel.hex_widget.game_label = "No Game"
            self.game_status_panel.hex_widget.status_text = "Waiting..."
            self.game_status_panel.hex_widget.update()

    def cleanup(self) -> None:
        if self.overlay_window:
            self.overlay_window.close()
        if hasattr(self, 'game_check_timer'):
            self.game_check_timer.stop()


def run_gui(
    ai_assistant,
    config: Config,
    credential_store: CredentialStore,
    ds: OmnixDesignSystem = design_system,
    game_detector=None
) -> None:
    """Launch the Omnix GUI."""

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(ai_assistant, config, credential_store, ds, game_detector)
    window.show()
    sys.exit(app.exec())


__all__ = [
    "AIWorkerThread",
    "ChatWidget",
    "OverlayWindow",
    "MainWindow",
    "run_gui",
]
