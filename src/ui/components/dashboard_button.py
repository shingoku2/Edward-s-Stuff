"""
Omnix Dashboard Button Component
==================================

Large grid button component for the main dashboard with icon and text label.
"""

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from typing import Optional
from ..tokens import COLORS, SPACING, RADIUS, TYPOGRAPHY
from ..icons import icons


class OmnixDashboardButton(QPushButton):
    """
    Dashboard grid button with large icon and text label.

    Features a frosted glass aesthetic with semi-transparent background
    and hover effects using accent colors.

    Usage:
        button = OmnixDashboardButton("chat", "Chat")
        button.clicked.connect(on_chat_clicked)
    """

    def __init__(
        self,
        icon_name: str,
        text: str,
        parent: Optional[object] = None,
    ):
        """
        Initialize dashboard button.

        Args:
            icon_name: Name of the icon from the icon system
            text: Text label for the button
            parent: Parent widget
        """
        super().__init__(parent)

        # Set cursor
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING.md)
        layout.setContentsMargins(SPACING.base, SPACING.lg, SPACING.base, SPACING.lg)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        icon_pixmap = icons.get_pixmap(icon_name, color=COLORS.accent_primary, size=48)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon_pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.icon_label)

        # Text label
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {COLORS.text_secondary};
                font-size: {TYPOGRAPHY.size_sm}pt;
                font-weight: {TYPOGRAPHY.weight_medium};
            }}
        """)
        layout.addWidget(self.text_label)

        self.setLayout(layout)

        # Apply styling
        self.setStyleSheet(f"""
            OmnixDashboardButton {{
                background-color: #2C2C4A99;
                border: 1px solid {COLORS.border_subtle};
                border-radius: {RADIUS.md}px;
                min-width: 120px;
                min-height: 120px;
            }}
            OmnixDashboardButton:hover {{
                background-color: #3A3A5ACC;
                border: 1px solid {COLORS.accent_primary};
            }}
            OmnixDashboardButton:pressed {{
                background-color: #46466EE6;
                border: 1px solid {COLORS.accent_primary_bright};
            }}
        """)
