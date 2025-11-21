"""
Omnix Card and Panel Components
=================================

Card and panel components for organizing content.
"""

from typing import Optional

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..tokens import COLORS, RADIUS, SPACING


class OmnixPanel(QFrame):
    """
    Omnix panel component.

    A container with background and border styling from the design system.

    Usage:
        panel = OmnixPanel()
        panel.layout().addWidget(some_widget)
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        padding: int = 16,
    ):
        """
        Initialize Omnix panel.

        Args:
            parent: Parent widget
            padding: Internal padding in pixels
        """
        super().__init__(parent)

        # Set frame style
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Apply custom styling
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.bg_secondary};
                border: 1px solid {COLORS.border_subtle};
                border-radius: {RADIUS.base}px;
                padding: {padding}px;
            }}
        """
        )

        # Create layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(SPACING.md)
        self.setLayout(self._layout)

    def layout(self) -> QVBoxLayout:
        """Get the panel's layout."""
        return self._layout


class OmnixCard(QFrame):
    """
    Omnix card component.

    A card with optional header, content area, and hover effects.

    Usage:
        card = OmnixCard(title="Card Title")
        card.add_content(some_widget)
        card.set_hoverable(True)
    """

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
        hoverable: bool = False,
    ):
        """
        Initialize Omnix card.

        Args:
            title: Card title
            parent: Parent widget
            hoverable: Enable hover effect
        """
        super().__init__(parent)

        self._hoverable = hoverable

        # Set frame style
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Apply custom styling
        self._apply_style()

        # Create main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self.setLayout(self._main_layout)

        # Create header if title provided
        if title:
            self._create_header(title)

        # Create content area
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(
            SPACING.base, SPACING.base, SPACING.base, SPACING.base
        )
        self._content_layout.setSpacing(SPACING.md)
        self._main_layout.addWidget(self._content_widget)

    def _create_header(self, title: str):
        """Create card header with title."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACING.base, SPACING.md, SPACING.base, SPACING.md)

        # Title label
        title_label = QLabel(title)
        title_label.setProperty("labelStyle", "subheading")
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.accent_primary};
                font-weight: 600;
                font-size: 14pt;
            }}
        """
        )

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.border_subtle};
                border: none;
                max-height: 1px;
            }}
        """
        )

        self._main_layout.addWidget(header)
        self._main_layout.addWidget(separator)

    def _apply_style(self):
        """Apply card styling."""
        base_style = f"""
            OmnixCard {{
                background-color: {COLORS.bg_secondary};
                border: 1px solid {COLORS.border_default};
                border-radius: {RADIUS.md}px;
            }}
        """

        if self._hoverable:
            hover_style = f"""
                OmnixCard:hover {{
                    border-color: {COLORS.accent_primary};
                    background-color: {COLORS.bg_secondary_alt};
                }}
            """
            self.setStyleSheet(base_style + hover_style)
        else:
            self.setStyleSheet(base_style)

    def add_content(self, widget: QWidget):
        """
        Add a widget to the card content area.

        Args:
            widget: Widget to add
        """
        self._content_layout.addWidget(widget)

    def add_stretch(self):
        """Add stretch to the content layout."""
        self._content_layout.addStretch()

    def set_hoverable(self, hoverable: bool):
        """
        Enable or disable hover effect.

        Args:
            hoverable: Enable hover effect
        """
        self._hoverable = hoverable
        self._apply_style()

    def content_layout(self) -> QVBoxLayout:
        """Get the card's content layout."""
        return self._content_layout


class OmnixInfoCard(OmnixCard):
    """
    Information card with icon and text.

    A specialized card for displaying information with optional icon.

    Usage:
        card = OmnixInfoCard(
            title="Session Stats",
            description="Total playtime and performance metrics"
        )
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        icon: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize info card.

        Args:
            title: Card title
            description: Description text
            icon: Icon text/emoji (if no icon system available)
            parent: Parent widget
        """
        super().__init__(parent=parent)

        # Content container
        content = QWidget()
        layout = QHBoxLayout(content)
        layout.setSpacing(SPACING.base)

        # Icon (if provided)
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {COLORS.accent_primary};
                    font-size: 24pt;
                }}
            """
            )
            layout.addWidget(icon_label)

        # Text content
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setSpacing(SPACING.sm)
        text_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: 14pt;
                font-weight: 600;
            }}
        """
        )
        text_layout.addWidget(title_label)

        # Description
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {COLORS.text_secondary};
                    font-size: 11pt;
                }}
            """
            )
            text_layout.addWidget(desc_label)

        layout.addWidget(text_widget)
        layout.addStretch()

        self.add_content(content)
