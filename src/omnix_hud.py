"""
Sci-fi OMNIX HUD primitives (PyQt6 + QSS) - LEGACY COMPONENTS
==============================================================

DEPRECATED: This module contains legacy HUD components that have been
replaced by the unified component system in ui/components/.

Legacy components:
- HudPanel -> use ui.components.OmnixPanel
- NeonButton -> use ui.components.OmnixButton
- ChatBubble -> use ui.components.OmnixCard with chat styling

These legacy components will be removed in a future version.
Please migrate to the unified component system for better consistency.
"""

from typing import Optional

from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QSize
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
)

# Import unified components to provide compatibility wrappers
try:
    from .ui.components import OmnixButton, OmnixPanel, OmnixCard

    _UNIFIED_AVAILABLE = True
except ImportError:
    _UNIFIED_AVAILABLE = False


# Legacy compatibility wrappers
class HudPanel(QFrame):
    """LEGACY: Use ui.components.OmnixPanel instead"""

    def __init__(self, parent: Optional[QWidget] = None):
        if _UNIFIED_AVAILABLE:
            # Use unified component when available
            self._panel = OmnixPanel(parent)
            super(QFrame, self).__init__(parent)
            # Delegate all calls to the unified panel
        else:
            # Fallback to legacy implementation
            super().__init__(parent)
            self.setObjectName("hud-panel")
            self.setFrameShape(QFrame.Shape.NoFrame)
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )


class NeonButton(QPushButton):
    """LEGACY: Use ui.components.OmnixButton instead"""

    def __init__(
        self, text: str, parent: Optional[QWidget] = None, *, primary: bool = True
    ):
        if _UNIFIED_AVAILABLE:
            # Use unified component with appropriate style
            style = "primary" if primary else "secondary"
            self._button = OmnixButton(text, style, parent)
            super(QPushButton, self).__init__(text, parent)
            # Delegate to unified button
        else:
            # Fallback to legacy implementation
            super().__init__(text, parent)
            self.setObjectName("neon-button")
            self.setProperty("variant", "primary" if primary else "secondary")
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setMinimumHeight(32)
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)


class ChatBubble(QFrame):
    def __init__(
        self, sender: str, text: str, is_user: bool, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setObjectName("chat-bubble")
        self.setProperty("role", "user" if is_user else "assistant")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)

        header = QLabel(sender)
        header.setObjectName("chat-bubble-sender")

        body = QLabel(text)
        body.setObjectName("chat-bubble-text")
        body.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(body)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


class ChatPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chat-scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(8, 8, 8, 8)
        self.container_layout.setSpacing(8)
        self.container_layout.addStretch(1)

        self.scroll_area.setWidget(self.container)
        outer.addWidget(self.scroll_area)

    def add_message(self, sender: str, text: str, is_user: bool):
        # Remove trailing stretch, add bubble, re-add stretch
        stretch = None
        count = self.container_layout.count()
        if count > 0:
            last_item = self.container_layout.itemAt(count - 1)
            if isinstance(last_item, QSpacerItem):
                stretch = self.container_layout.takeAt(count - 1)

        bubble = ChatBubble(sender, text, is_user)
        self.container_layout.addWidget(bubble)

        if stretch is not None:
            self.container_layout.addItem(stretch)
        else:
            self.container_layout.addStretch(1)

        # Auto-scroll to bottom
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self.container_layout.addStretch(1)


class GameStatusWidget(QFrame):
    """
    Central circular 'GAME DETECTED' widget.

    Use set_game(game_name, online) to update.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("game-status-widget")
        self._game_name = ""
        self._online = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("GAME DETECTED")
        self.title_label.setObjectName("game-status-title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.canvas = _GameStatusCanvas()
        self.canvas.setFixedSize(220, 220)

        self.status_label = QLabel("NO GAME • OFFLINE")
        self.status_label.setObjectName("game-status-label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.canvas)
        layout.addWidget(self.status_label)

    def set_game(self, game_name: Optional[str], online: bool):
        self._game_name = game_name or ""
        self._online = bool(online)
        status = "ONLINE" if online else "OFFLINE"
        if self._game_name:
            self.status_label.setText(f"{self._game_name} • {status}")
        else:
            self.status_label.setText(f"NO GAME • {status}")
        self.canvas.set_online(online)


class _GameStatusCanvas(QWidget):
    """
    Internal painter surface for multi-ring neon circle.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._pulse = 0.0
        self._online = False

        self._anim = QPropertyAnimation(self, b"pulse")
        self._anim.setDuration(2000)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setLoopCount(-1)
        self._anim.start()

    def sizeHint(self) -> QSize:
        return QSize(220, 220)

    def get_pulse(self) -> float:
        return self._pulse

    def set_pulse(self, value: float):
        self._pulse = float(value)
        self.update()

    pulse = pyqtProperty(float, fget=get_pulse, fset=set_pulse)

    def set_online(self, online: bool):
        self._online = bool(online)
        self.update()

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        r = side / 2 - 4
        center = self.rect().center()

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), Qt.GlobalColor.transparent)

        # Outer pulse
        base_alpha = 90 + int(60 * self._pulse)
        pulse_color = QColor("#22d3ee") if self._online else QColor("#4b5563")
        pulse_color.setAlpha(base_alpha)
        p.setPen(QPen(pulse_color, 3))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(center, r, r)

        # Inner rings
        inner_colors = ["#22d3ee", "#a855f7", "#f97373"]
        for i, c in enumerate(inner_colors):
            rr = r - 10 * (i + 1)
            if rr <= 0:
                continue
            col = QColor(c)
            col.setAlpha(190 if self._online else 90)
            p.setPen(QPen(col, 2))
            p.drawEllipse(center, rr, rr)

        # Center disc
        disc = QColor("#ef4444" if self._online else "#6b7280")
        disc.setAlpha(230)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(disc)
        p.drawEllipse(center, 26, 26)

        p.end()


class StatBlock(QFrame):
    """
    Compact stat block: K/D, MATCH, WINS.
    Use set_stats(kd, matches, wins).
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("stat-block")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(24)

        self.kd_value = QLabel("--")
        self.match_value = QLabel("--")
        self.win_value = QLabel("--")

        for label, value in [
            ("K/D", self.kd_value),
            ("MATCH", self.match_value),
            ("WINS", self.win_value),
        ]:
            col = QVBoxLayout()
            title = QLabel(label)
            title.setObjectName("stat-label")
            value.setObjectName("stat-value")
            value.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            col.addWidget(title)
            col.addWidget(value)
            col.setSpacing(2)
            layout.addLayout(col)

    def set_stats(self, kd: str, matches: str, wins: str):
        self.kd_value.setText(kd)
        self.match_value.setText(matches)
        self.win_value.setText(wins)


OMNIX_GLOBAL_QSS = """
/* Base window */
QMainWindow {
    background-color: #050816;
}

/* Global text */
QWidget {
    color: #e5e7eb;
    font-family: "Segoe UI", "Roboto", "Inter", sans-serif;
}

/* Top bar */

#top-bar {
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background-color: rgba(10, 16, 32, 0.96);
    padding: 0px;
    margin-bottom: 6px;
    border-top: 2px solid qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #f97373,
        stop:0.5 #ec4899,
        stop:1 #22d3ee);
}

#top-bar-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #f9fafb;
}

#top-bar-user {
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #818cf8;
}

QToolButton#top-bar-dot {
    border-radius: 9px;
    border: 1px solid rgba(248, 113, 113, 0.9);
    background-color: rgba(30, 64, 175, 0.9);
}
QToolButton#top-bar-dot:hover {
    background-color: rgba(248, 113, 113, 0.95);
}

/* Branding (optional in body) */
#omnix-logo {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #22d3ee,
                                stop:1 #a855f7);
    qproperty-alignment: AlignLeft | AlignVCenter;
}
#omnix-logo-subtitle {
    font-size: 9px;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #64748b;
}

/* HUD panels */
QFrame#hud-panel {
    background-color: rgba(10, 16, 32, 0.97);
    border-radius: 18px;
    border: 1px solid rgba(34, 211, 238, 0.4);
}

/* Chat */
#chat-scroll {
    border: none;
    background: transparent;
}

#chat-bubble {
    border-radius: 14px;
    border: 1px solid rgba(34, 211, 238, 0.4);
    background-color: rgba(15, 23, 42, 0.98);
}
#chat-bubble[role="user"] {
    border-color: rgba(236, 72, 153, 0.9);
    background-color: rgba(24, 24, 37, 0.98);
}

#chat-bubble-sender {
    font-size: 9px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #94a3b8;
}
#chat-bubble-text {
    font-size: 12px;
    color: #e5e7eb;
}

/* Chat input */
QLineEdit#chat-input {
    background-color: rgba(8, 11, 25, 0.98);
    border-radius: 999px;
    border: 1px solid rgba(39, 39, 80, 0.9);
    padding: 6px 14px;
    font-size: 12px;
    color: #e5e7eb;
}
QLineEdit#chat-input::placeholder {
    color: #6b7280;
}

/* Neon buttons (OVERLAY, SEND, SETTINGS, provider buttons) */
#neon-button {
    border-radius: 999px;
    padding: 7px 26px;
    border: 1px solid rgba(56, 189, 248, 0.9);
    background-color: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 rgba(8, 47, 73, 0.95),
        stop:1 rgba(15, 23, 42, 1.0));
    color: #e5e7eb;
    font-weight: 600;
    letter-spacing: 0.26em;
    text-transform: uppercase;
}
#neon-button[variant="secondary"] {
    border-color: rgba(236, 72, 153, 0.9);
    background-color: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 rgba(76, 29, 149, 0.95),
        stop:1 rgba(24, 24, 37, 1.0));
}
#neon-button:hover {
    background-color: rgba(8, 47, 73, 1.0);
}
#neon-button:pressed {
    background-color: rgba(15, 23, 42, 1.0);
}

/* Game status widget */
#game-status-widget {
    border-radius: 24px;
    border: 1px solid rgba(56, 189, 248, 0.7);
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(11, 15, 35, 0.98),
        stop:1 rgba(6, 9, 23, 0.98));
}
#game-status-title {
    font-size: 11px;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: #e5e7eb;
}
#game-status-label {
    font-size: 11px;
    color: #22c55e;
}

/* Stat block */
#stat-block {
    border-radius: 18px;
    border: 1px solid rgba(248, 113, 113, 0.85);
    background-color: rgba(24, 17, 52, 0.98);
}
#stat-label {
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #fca5a5;
}
#stat-value {
    font-size: 16px;
    font-weight: 700;
    color: #fecaca;
}

/* Settings rows */
QFrame#settings-row {
    border-radius: 12px;
    border: 1px solid rgba(31, 41, 55, 0.9);
    background-color: rgba(15, 23, 42, 0.98);
}
QFrame#settings-row[active="true"] {
    border-color: #22d3ee;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.9);
}

/* ── Main panels ── */
QFrame#hud-panel {
    background-color: rgba(10, 16, 32, 0.97);
    border-radius: 14px;
    border: 1px solid rgba(34, 211, 238, 0.35);
}

QFrame#overlay-frame {
    background-color: rgba(5, 11, 20, 0.94);
    border-radius: 12px;
    border: 1px solid rgba(34, 211, 238, 0.5);
}

/* ── Labels ── */
QLabel#panel-title {
    font-size: 9px;
    letter-spacing: 0.30em;
    text-transform: uppercase;
    color: #22d3ee;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(34, 211, 238, 0.2);
}

QLabel#game-name-label {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #f0f9ff;
    padding: 12px 0;
}

QLabel#game-info-label {
    font-size: 11px;
    color: #94a3b8;
    padding: 4px 8px;
}

QLabel#stat-value {
    font-size: 12px;
    color: #22d3ee;
    letter-spacing: 0.1em;
}

QLabel#stat-label {
    font-size: 9px;
    letter-spacing: 0.2em;
    color: #64748b;
}

/* ── Chat ── */
QTextEdit#chat-display {
    background-color: rgba(8, 11, 25, 0.95);
    border-radius: 8px;
    border: 1px solid rgba(39, 39, 80, 0.8);
    color: #e5e7eb;
    font-size: 12px;
    padding: 8px;
}

QLineEdit#chat-input {
    background-color: rgba(8, 11, 25, 0.98);
    border-radius: 999px;
    border: 1px solid rgba(39, 39, 80, 0.9);
    padding: 8px 16px;
    font-size: 12px;
    color: #e5e7eb;
}
QLineEdit#chat-input:focus {
    border-color: rgba(34, 211, 238, 0.8);
}

/* ── Buttons ── */
QPushButton#neon-button-primary {
    background-color: rgba(34, 211, 238, 0.12);
    color: #22d3ee;
    border: 1px solid rgba(34, 211, 238, 0.7);
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 700;
}
QPushButton#neon-button-primary:hover {
    background-color: #22d3ee;
    color: #000;
}

QPushButton#neon-button-secondary {
    background-color: rgba(99, 102, 241, 0.12);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.5);
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 600;
}
QPushButton#neon-button-secondary:hover {
    background-color: #6366f1;
    color: #fff;
}

/* ── Combo ── */
QComboBox#omnix-combo {
    background-color: rgba(8, 11, 25, 0.95);
    border: 1px solid rgba(34, 211, 238, 0.4);
    border-radius: 6px;
    color: #e5e7eb;
    padding: 4px 8px;
    font-size: 11px;
}
QComboBox#omnix-combo:focus {
    border-color: #22d3ee;
}
"""
