"""
Omnix Modal Dialog Components
===============================

Modal dialog components for user interactions.
"""

from typing import Callable, Optional

from PyQt6.QtCore import Qt  # noqa: F401
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..tokens import COLORS, RADIUS, SPACING, TYPOGRAPHY
from .buttons import OmnixButton


class OmnixDialog(QDialog):
    """
    Base Omnix dialog component.

    A styled dialog window with consistent design system styling.

    Usage:
        dialog = OmnixDialog(title="Confirm Action", parent=parent)
        dialog.add_content(some_widget)
        dialog.add_button("OK", dialog.accept)
        dialog.exec()
    """

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
        width: int = 500,
        height: Optional[int] = None,
    ):
        """
        Initialize dialog.

        Args:
            title: Dialog title
            parent: Parent widget
            width: Dialog width
            height: Dialog height (optional, auto-size if not set)
        """
        super().__init__(parent)

        # Set window properties
        self.setWindowTitle(title)
        self.setModal(True)

        if height:
            self.setFixedSize(width, height)
        else:
            self.setMinimumWidth(width)

        # Apply styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {COLORS.bg_primary};
                border: 1px solid {COLORS.accent_primary};
                border-radius: {RADIUS.lg}px;
            }}
        """
        )

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Header
        if title:
            self._create_header(title)
            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {COLORS.border_subtle};
                    max-height: 1px;
                }}
            """
            )
            main_layout.addWidget(separator)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
        self.content_layout.setSpacing(SPACING.base)
        main_layout.addWidget(self.content_widget, 1)

        # Footer (buttons area)
        self.footer_widget = QWidget()
        self.footer_layout = QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(SPACING.lg, SPACING.md, SPACING.lg, SPACING.lg)
        self.footer_layout.setSpacing(SPACING.md)
        self.footer_layout.addStretch()
        main_layout.addWidget(self.footer_widget)

    def _create_header(self, title: str):
        """Create dialog header."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACING.lg, SPACING.base, SPACING.lg, SPACING.base)

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
        header_layout.addWidget(title_label)

        self.layout().addWidget(header)

    def add_content(self, widget: QWidget):
        """
        Add widget to content area.

        Args:
            widget: Widget to add
        """
        self.content_layout.addWidget(widget)

    def add_button(
        self,
        text: str,
        callback: Optional[Callable] = None,
        style: str = "primary",
    ) -> OmnixButton:
        """
        Add button to footer.

        Args:
            text: Button text
            callback: Click callback
            style: Button style (primary, secondary, danger, success)

        Returns:
            Created button
        """
        button = OmnixButton(text, style=style)
        if callback:
            button.clicked.connect(callback)
        self.footer_layout.addWidget(button)
        return button

    def add_default_buttons(
        self, ok_callback: Optional[Callable] = None, cancel_callback: Optional[Callable] = None
    ):
        """
        Add standard OK/Cancel buttons.

        Args:
            ok_callback: OK button callback (defaults to accept)
            cancel_callback: Cancel button callback (defaults to reject)
        """
        self.add_button("Cancel", cancel_callback or self.reject, style="secondary")
        self.add_button("OK", ok_callback or self.accept, style="primary")


class OmnixConfirmDialog(OmnixDialog):
    """
    Confirmation dialog.

    A dialog for Yes/No confirmations.

    Usage:
        dialog = OmnixConfirmDialog(
            title="Delete Profile",
            message="Are you sure you want to delete this profile?",
            confirm_text="Delete",
            parent=parent
        )
        if dialog.exec():
            # User confirmed
    """

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        is_dangerous: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Confirmation message
            confirm_text: Confirm button text
            cancel_text: Cancel button text
            is_dangerous: Use danger styling for confirm button
            parent: Parent widget
        """
        super().__init__(title=title, parent=parent, width=450)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.size_md}pt;
            }}
        """
        )
        self.add_content(message_label)

        # Buttons
        self.add_button(cancel_text, self.reject, style="secondary")
        self.add_button(confirm_text, self.accept, style="danger" if is_dangerous else "primary")


class OmnixMessageDialog(OmnixDialog):
    """
    Message dialog.

    A simple dialog to display a message with an OK button.

    Usage:
        dialog = OmnixMessageDialog(
            title="Success",
            message="Profile saved successfully!",
            message_type="success"
        )
        dialog.exec()
    """

    def __init__(
        self,
        title: str,
        message: str,
        message_type: str = "info",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize message dialog.

        Args:
            title: Dialog title
            message: Message to display
            message_type: Message type (info, success, warning, error)
            parent: Parent widget
        """
        super().__init__(title=title, parent=parent, width=400)

        # Icon map
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠️",
            "error": "✗",
        }

        colors = {
            "info": COLORS.info,
            "success": COLORS.success,
            "warning": COLORS.warning,
            "error": COLORS.error,
        }

        # Container
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(SPACING.base)

        # Icon
        icon_label = QLabel(icons.get(message_type, "ℹ️"))
        icon_label.setStyleSheet(
            f"""
            QLabel {{
                color: {colors.get(message_type, COLORS.info)};
                font-size: {TYPOGRAPHY.size_3xl}pt;
            }}
        """
        )
        layout.addWidget(icon_label)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.size_md}pt;
            }}
        """
        )
        layout.addWidget(message_label, 1)

        self.add_content(container)

        # OK button
        self.add_button("OK", self.accept, style="primary")


class OmnixInputDialog(OmnixDialog):
    """
    Input dialog.

    A dialog with a text input field.

    Usage:
        dialog = OmnixInputDialog(
            title="Enter Name",
            label="Profile Name:",
            placeholder="My Profile"
        )
        if dialog.exec():
            name = dialog.get_value()
    """

    def __init__(
        self,
        title: str,
        label: str,
        placeholder: str = "",
        default_value: str = "",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize input dialog.

        Args:
            title: Dialog title
            label: Input label
            placeholder: Input placeholder
            default_value: Default input value
            parent: Parent widget
        """
        super().__init__(title=title, parent=parent, width=450)

        from .inputs import OmnixLineEdit

        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.size_md}pt;
                font-weight: {TYPOGRAPHY.weight_medium};
            }}
        """
        )
        self.add_content(label_widget)

        # Input
        self.input_field = OmnixLineEdit(
            text=default_value, placeholder=placeholder, clearable=True
        )
        self.add_content(self.input_field)

        # Buttons
        self.add_default_buttons()

        # Focus on input
        self.input_field.setFocus()

    def get_value(self) -> str:
        """
        Get the input value.

        Returns:
            Input text
        """
        return self.input_field.text()
