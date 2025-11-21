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
    """Right side panel with tabbed settings and provider selection."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.menu_buttons: Dict[str, NeonButton] = {}
        menu = QVBoxLayout()
        for name in ["Overlay Mode", "General", "Notifications", "Privacy"]:
            button = NeonButton(name, variant="toggle", checkable=True)
            button.clicked.connect(lambda _, n=name: self.set_active_menu(n))
            menu.addWidget(button)
            self.menu_buttons[name] = button
        self.menu_buttons["Overlay Mode"].setChecked(True)
        layout.addLayout(menu)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_overlay_page())
        self.stack.addWidget(self._build_general_page())
        self.stack.addWidget(self._build_notifications_page())
        self.stack.addWidget(self._build_privacy_page())
        layout.addWidget(self.stack, 1)

        provider_label = QLabel("AI Provider")
        provider_label.setObjectName("SectionTitle")
        layout.addWidget(provider_label)

        provider_row = QHBoxLayout()
        self.provider_synapse = NeonButton("Synapse", variant="provider", checkable=True)
        self.provider_hybridenix = NeonButton("Hybridenix", variant="provider", checkable=True)
        self.provider_synapse.setChecked(True)
        self.provider_synapse.clicked.connect(lambda: self._select_provider(self.provider_synapse))
        self.provider_hybridenix.clicked.connect(lambda: self._select_provider(self.provider_hybridenix))
        provider_row.addWidget(self.provider_synapse)
        provider_row.addWidget(self.provider_hybridenix)
        layout.addLayout(provider_row)

        layout.addStretch()

    def _select_provider(self, button: NeonButton) -> None:
        for btn in [self.provider_synapse, self.provider_hybridenix]:
            btn.setChecked(btn is button)

    def set_active_menu(self, name: str) -> None:
        for index, key in enumerate(["Overlay Mode", "General", "Notifications", "Privacy"]):
            self.stack.setCurrentIndex(index if key == name else self.stack.currentIndex())
            self.menu_buttons[key].setChecked(key == name)
        self.stack.setCurrentIndex(["Overlay Mode", "General", "Notifications", "Privacy"].index(name))

    def _build_overlay_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)
        for text in [
            "Window frame",
            "Window location",
            "Lock position",
        ]:
            vbox.addWidget(NeonButton(text, variant="toggle", checkable=True))
        vbox.addStretch()
        return page

    def _build_general_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)
        for text in ["Launch on startup", "Power efficient", "Enable tool tips"]:
            vbox.addWidget(NeonButton(text, variant="toggle", checkable=True))
        vbox.addStretch()
        return page

    def _build_notifications_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)
        for text in ["Desktop notifications", "Sound alert", "AI alerts"]:
            vbox.addWidget(NeonButton(text, variant="toggle", checkable=True))
        vbox.addStretch()
        return page

    def _build_privacy_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)
        for text in ["Streamer mode", "Online status"]:
            vbox.addWidget(NeonButton(text, variant="toggle", checkable=True))
        share = NeonButton("Share usage data", variant="toggle", checkable=True)
        share.setChecked(True)
        vbox.addWidget(share)
        vbox.addStretch()
        return page


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

    def toggle_minimize(self) -> None:
        self.minimized = not self.minimized
        if self.minimized:
            self._saved_height = self.height()
            self.chat.setVisible(False)
            self.setFixedHeight(80)
        else:
            self.chat.setVisible(True)
            self.setFixedHeight(getattr(self, "_saved_height", self.sizeHint().height()))


class MainWindow(QMainWindow):
    """Omnix main dashboard window."""

    def __init__(self, ai_assistant, config: Config, credential_store: CredentialStore, design_system: OmnixDesignSystem = design_system):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.config = config
        self.credential_store = credential_store
        self.design_system = design_system or OmnixDesignSystem()

        self.setWindowTitle("Omnix - All Knowing AI Companion")
        self.resize(1280, 760)

        base_styles = self.design_system.generate_complete_stylesheet()
        self.setStyleSheet(base_styles + "\n" + _load_qss())

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
        settings_button.clicked.connect(lambda: self.settings_panel.set_active_menu("General"))
        footer.addWidget(settings_button)

        footer.addStretch()
        return footer

    def _toggle_overlay(self) -> None:
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
        else:
            self.overlay_window.show()
            self.overlay_window.raise_()

    def cleanup(self) -> None:
        if self.overlay_window:
            self.overlay_window.close()


def run_gui(ai_assistant, config: Config, credential_store: CredentialStore, ds: OmnixDesignSystem = design_system) -> None:
    """Launch the Omnix GUI."""

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(ai_assistant, config, credential_store, ds)
    window.show()
    sys.exit(app.exec())


__all__ = [
    "AIWorkerThread",
    "ChatWidget",
    "OverlayWindow",
    "MainWindow",
    "run_gui",
]
