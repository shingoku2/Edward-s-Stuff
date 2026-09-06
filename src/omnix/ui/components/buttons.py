"""
Omnix Button Components
========================

Button components following the Omnix design system.
"""

from typing import Optional

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QPushButton


class OmnixButton(QPushButton):
    """
    Omnix styled button component.

    Supports multiple button styles:
    - primary (default): Electric blue background
    - secondary: Transparent with border
    - danger: Red background for destructive actions
    - success: Green background for positive actions
    - icon: Circular icon-only button

    Usage:
        button = OmnixButton("Click Me")
        button = OmnixButton("Delete", style="danger")
        button = OmnixButton("Save", style="success")
    """

    def __init__(
        self,
        text: str = "",
        style: str = "primary",
        parent: Optional[object] = None,
    ):
        """
        Initialize Omnix button.

        Args:
            text: Button text
            style: Button style (primary, secondary, danger, success, icon)
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set button style property (used in QSS)
        if style != "primary":
            self.setProperty("buttonStyle", style)

        # Set cursor
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Set minimum size
        if style != "icon":
            self.setMinimumWidth(80)
            self.setMinimumHeight(36)

    def set_style(self, style: str):
        """
        Change button style.

        Args:
            style: New button style
        """
        self.setProperty("buttonStyle", style if style != "primary" else None)
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class OmnixIconButton(QPushButton):
    """
    Omnix icon-only button component.

    A circular button designed for icons without text.

    Usage:
        button = OmnixIconButton(icon=close_icon)
        button = OmnixIconButton(text="X", size=32)
    """

    def __init__(
        self,
        text: str = "",
        icon=None,
        size: int = 32,
        parent: Optional[object] = None,
    ):
        """
        Initialize Omnix icon button.

        Args:
            text: Button text (if no icon provided)
            icon: QIcon for the button
            size: Button size in pixels
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set icon if provided
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(size - 8, size - 8))

        # Set button style property
        self.setProperty("buttonStyle", "icon")

        # Set fixed size
        self.setFixedSize(size, size)

        # Set cursor
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
