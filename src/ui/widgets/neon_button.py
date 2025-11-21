"""
NeonButton and NeonToggle Widgets
"""
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QWidget


class NeonButton(QPushButton):
    """Neon-styled button with hover glow animation."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, accent: str = "#0af5ff"):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("variant", "primary")

        # Keep a subtle, static glow instead of animated effect to avoid painter conflicts
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(24)
        effect.setColor(QColor(accent).lighter(120))
        effect.setOffset(0, 0)
        self.setGraphicsEffect(effect)


class NeonToggle(NeonButton):
    """Checkable toggle styled for neon chips."""

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setProperty("variant", "toggle")

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.setProperty("active", "true" if self.isChecked() else "false")
        self.style().unpolish(self)
        self.style().polish(self)
