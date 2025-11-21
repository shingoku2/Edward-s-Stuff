"""
NeonCard Widget
"""
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QSizePolicy, QWidget


class NeonCard(QFrame):
    """Base container with holographic border styling."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("NeonCard")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(36)
        glow.setColor(QColor(24, 195, 255, 70))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
