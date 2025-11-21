"""
Omnix Navigation Components
=============================

Navigation components including sidebar and tab navigation.
"""

from typing import Callable, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..tokens import COLORS, RADIUS, SPACING, TYPOGRAPHY


class OmnixSidebarButton(QPushButton):
    """
    Sidebar navigation button.

    A button designed for sidebar navigation with icon and text.

    Usage:
        button = OmnixSidebarButton(text="Chat", icon_text="💬")
        button.clicked.connect(on_chat_clicked)
    """

    def __init__(
        self,
        text: str,
        icon_text: str = "",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize sidebar button.

        Args:
            text: Button text
            icon_text: Icon text/emoji
            parent: Parent widget
        """
        super().__init__(parent)

        self.setCheckable(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 12, 8, 12)

        # Icon
        if icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {COLORS.text_secondary};
                    font-size: {TYPOGRAPHY.size_2xl}pt;
                }}
            """
            )
            layout.addWidget(icon_label)

        # Text
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_secondary};
                font-size: {TYPOGRAPHY.size_sm}pt;
                font-weight: {TYPOGRAPHY.weight_medium};
            }}
        """
        )
        layout.addWidget(text_label)

        self.setLayout(layout)

        # Apply styling
        self._update_style()

    def _update_style(self):
        """Update button style."""
        self.setStyleSheet(
            f"""
            OmnixSidebarButton {{
                background-color: transparent;
                border: none;
                border-radius: {RADIUS.md}px;
                min-width: 80px;
                min-height: 80px;
            }}
            OmnixSidebarButton:hover {{
                background-color: {COLORS.bg_secondary};
            }}
            OmnixSidebarButton:checked {{
                background-color: {COLORS.accent_primary};
            }}
            OmnixSidebarButton:checked QLabel {{
                color: {COLORS.text_primary};
            }}
        """
        )


class OmnixSidebar(QWidget):
    """
    Sidebar navigation component.

    A vertical sidebar with navigation buttons.

    Signals:
        tab_changed: Emitted when active tab changes (index: int)

    Usage:
        sidebar = OmnixSidebar()
        sidebar.add_button("Chat", "💬", on_chat_clicked)
        sidebar.add_button("Settings", "⚙️", on_settings_clicked)
    """

    tab_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize sidebar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Styling
        self.setStyleSheet(
            f"""
            OmnixSidebar {{
                background-color: {COLORS.bg_primary_alt};
                border-right: 1px solid {COLORS.border_subtle};
            }}
        """
        )

        # Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING.sm)
        layout.setContentsMargins(SPACING.sm, SPACING.md, SPACING.sm, SPACING.md)
        self.setLayout(layout)

        # Button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.idClicked.connect(self.tab_changed.emit)

        self.buttons: List[OmnixSidebarButton] = []

    def add_button(
        self,
        text: str,
        icon_text: str = "",
        callback: Optional[Callable] = None,
    ) -> OmnixSidebarButton:
        """
        Add a button to the sidebar.

        Args:
            text: Button text
            icon_text: Icon text/emoji
            callback: Click callback function

        Returns:
            Created button
        """
        button = OmnixSidebarButton(text, icon_text, self)

        # Add to button group
        button_id = len(self.buttons)
        self.button_group.addButton(button, button_id)
        self.buttons.append(button)

        # Connect callback
        if callback:
            button.clicked.connect(callback)

        # Add to layout
        self.layout().addWidget(button)

        # Select first button by default
        if button_id == 0:
            button.setChecked(True)

        return button

    def add_stretch(self):
        """Add stretch to push subsequent buttons to bottom."""
        self.layout().addStretch()

    def set_active_tab(self, index: int):
        """
        Set the active tab.

        Args:
            index: Tab index
        """
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(True)


class OmnixHeaderBar(QWidget):
    """
    Application header bar.

    A header bar with logo, title, and status indicator.

    Usage:
        header = OmnixHeaderBar(title="Omnix AI Assistant")
        header.set_status("Online", "success")
    """

    def __init__(
        self,
        title: str = "Omnix",
        logo_text: str = "⬡",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize header bar.

        Args:
            title: Application title
            logo_text: Logo text/emoji
            parent: Parent widget
        """
        super().__init__(parent)

        # Styling
        self.setStyleSheet(
            f"""
            OmnixHeaderBar {{
                background-color: {COLORS.bg_primary_alt};
                border-bottom: 1px solid {COLORS.border_subtle};
            }}
        """
        )

        # Fixed height
        self.setFixedHeight(60)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING.base, SPACING.md, SPACING.base, SPACING.md)
        layout.setSpacing(SPACING.base)
        self.setLayout(layout)

        # Logo
        logo_label = QLabel(logo_text)
        logo_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.accent_primary};
                font-size: {TYPOGRAPHY.size_3xl}pt;
            }}
        """
        )
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.size_xl}pt;
                font-weight: {TYPOGRAPHY.weight_bold};
            }}
        """
        )
        layout.addWidget(title_label)

        # Stretch
        layout.addStretch()

        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(10, 10)
        layout.addWidget(self.status_indicator)

        # Status text
        self.status_text = QLabel("Offline")
        self.status_text.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_muted};
                font-size: {TYPOGRAPHY.size_sm}pt;
            }}
        """
        )
        layout.addWidget(self.status_text)

        # Set default status
        self.set_status("Offline", "error")

    def set_status(self, text: str, status: str = "info"):
        """
        Set status indicator.

        Args:
            text: Status text
            status: Status type (success, warning, error, info)
        """
        self.status_text.setText(text)

        status_colors = {
            "success": COLORS.success,
            "warning": COLORS.warning,
            "error": COLORS.error,
            "info": COLORS.info,
        }

        color = status_colors.get(status, COLORS.info)

        self.status_indicator.setStyleSheet(
            f"""
            QLabel {{
                background-color: {color};
                border-radius: 5px;
            }}
        """
        )

        self.status_text.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                font-size: {TYPOGRAPHY.size_sm}pt;
                font-weight: {TYPOGRAPHY.weight_medium};
            }}
        """
        )
