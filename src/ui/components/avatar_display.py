"""
Omnix Avatar Display Component
================================

Hero banner display component shown above the dashboard buttons.
"""
from typing import Optional

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame, QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen

from ..tokens import COLORS, SPACING, RADIUS, TYPOGRAPHY


class _CircuitCanvas(QWidget):
    """Painted gradient canvas with lightweight circuit lines."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumHeight(320)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def paintEvent(self, event):  # noqa: N802 - Qt signature
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        gradient.setColorAt(0, QColor(COLORS.bg_primary))
        gradient.setColorAt(1, QColor(COLORS.bg_secondary))
        painter.fillRect(rect, gradient)

        grid_color = QColor(COLORS.accent_primary)
        grid_color.setAlphaF(0.18)
        grid_pen = QPen(grid_color)
        grid_pen.setWidthF(1.2)
        painter.setPen(grid_pen)

        step = max(40, rect.width() // 12)
        for x in range(rect.left(), rect.right(), step):
            painter.drawLine(x, rect.top(), x, rect.bottom())
        for y in range(rect.top(), rect.bottom(), step):
            painter.drawLine(rect.left(), y, rect.right(), y)

        circuit_color = QColor(COLORS.accent_secondary)
        circuit_color.setAlphaF(0.35)
        circuit_pen = QPen(circuit_color)
        circuit_pen.setWidthF(2.0)
        painter.setPen(circuit_pen)

        mid_y = rect.center().y()
        mid_x = rect.center().x()
        path = QPainterPath(QPointF(rect.left() + step, mid_y - step))
        path.lineTo(QPointF(mid_x, mid_y - step))
        path.lineTo(QPointF(mid_x, mid_y + step))
        path.lineTo(QPointF(rect.right() - step, mid_y + step))
        painter.drawPath(path)
        painter.drawEllipse(QPointF(rect.center()), step * 0.75, step * 0.4)


class OmnixAvatarDisplay(QFrame):
    """
    Visual hero banner for the main dashboard.

    Displays the sci-fi circuit artwork supplied by design along with
    contextual status and the detected game name.
    """

    def __init__(self, parent: Optional[QFrame] = None):
        super().__init__(parent)
        self.game_context: Optional[str] = None
        self.status: str = "Ready"
        self.thinking: bool = False
        self._init_ui()

    def _init_ui(self):
        """Initialize the banner layout and text overlays."""
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: #1418288C;
                border: 1px solid {COLORS.border_subtle};
                border-radius: {RADIUS.lg}px;
            }}
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
        main_layout.setSpacing(SPACING.base)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.canvas = _CircuitCanvas()
        self.canvas.setStyleSheet(
            f"""
            QWidget {{
                border-radius: {RADIUS.lg}px;
                border: 1px solid {COLORS.border_subtle};
            }}
            """
        )
        main_layout.addWidget(self.canvas)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: #0C1424B8;
                border: 1px solid {COLORS.border_subtle};
                border-radius: {RADIUS.base}px;
            }}
            """
        )

        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(SPACING.base, SPACING.sm, SPACING.base, SPACING.sm)
        info_layout.setSpacing(SPACING.xs)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("Omnix AI Assistant")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.accent_primary};
                font-size: {TYPOGRAPHY.size_2xl}pt;
                font-weight: {TYPOGRAPHY.weight_bold};
                letter-spacing: {TYPOGRAPHY.letter_spacing_wide};
                background: transparent;
                border: none;
            }}
            """
        )
        info_layout.addWidget(self.title_label)

        self.status_label = QLabel(self.status)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.accent_secondary};
                font-size: {TYPOGRAPHY.size_md}pt;
                font-weight: {TYPOGRAPHY.weight_semibold};
                background: transparent;
                border: none;
            }}
            """
        )
        info_layout.addWidget(self.status_label)

        self.game_label = QLabel("No game detected")
        self.game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_secondary};
                font-size: {TYPOGRAPHY.size_sm}pt;
                font-weight: {TYPOGRAPHY.weight_normal};
                background: transparent;
                border: none;
            }}
            """
        )
        info_layout.addWidget(self.game_label)

        main_layout.addWidget(info_frame)
        self.setLayout(main_layout)

    def set_game_context(self, game_name: Optional[str]):
        """Update the visible game context."""
        self.game_context = game_name
        if game_name:
            self.game_label.setText(f"🎮 Playing: {game_name}")
            if not self.thinking:
                self.status_label.setText("Active")
        else:
            self.game_label.setText("No game detected")
            if not self.thinking:
                self.status_label.setText("Ready")

    def set_status(self, status: str):
        """Set the status text."""
        self.status = status
        if not self.thinking:
            self.status_label.setText(status)

    def set_thinking(self, thinking: bool):
        """Toggle thinking state."""
        self.thinking = thinking
        if thinking:
            self.status_label.setText("Thinking...")
        else:
            self.status_label.setText(self.status)
