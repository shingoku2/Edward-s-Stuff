"""
Omnix Input Components
=======================

Input field components following the Omnix design system.
"""

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QCompleter, QLineEdit, QTextEdit


class OmnixLineEdit(QLineEdit):
    """
    Omnix styled single-line input field.

    Features:
    - Consistent styling with design system
    - Placeholder text support
    - Clear button option
    - Input validation

    Usage:
        input_field = OmnixLineEdit(placeholder="Enter your name")
        input_field = OmnixLineEdit(placeholder="Password", echo_mode="password")
    """

    def __init__(
        self,
        text: str = "",
        placeholder: str = "",
        echo_mode: str = "normal",
        clearable: bool = False,
        parent: Optional[object] = None,
    ):
        """
        Initialize Omnix line edit.

        Args:
            text: Initial text
            placeholder: Placeholder text
            echo_mode: Echo mode (normal, password, no_echo)
            clearable: Show clear button
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set placeholder
        if placeholder:
            self.setPlaceholderText(placeholder)

        # Set echo mode
        if echo_mode == "password":
            self.setEchoMode(QLineEdit.EchoMode.Password)
        elif echo_mode == "no_echo":
            self.setEchoMode(QLineEdit.EchoMode.NoEcho)

        # Enable clear button
        if clearable:
            self.setClearButtonEnabled(True)


class OmnixTextEdit(QTextEdit):
    """
    Omnix styled multi-line text edit.

    Features:
    - Consistent styling with design system
    - Placeholder text support
    - Markdown support option
    - Read-only mode

    Usage:
        text_edit = OmnixTextEdit(placeholder="Enter description")
        text_edit = OmnixTextEdit(read_only=True)
    """

    def __init__(
        self,
        text: str = "",
        placeholder: str = "",
        read_only: bool = False,
        parent: Optional[object] = None,
    ):
        """
        Initialize Omnix text edit.

        Args:
            text: Initial text
            placeholder: Placeholder text
            read_only: Make read-only
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set placeholder
        if placeholder:
            self.setPlaceholderText(placeholder)

        # Set read-only
        if read_only:
            self.setReadOnly(True)


class OmnixComboBox(QComboBox):
    """
    Omnix styled dropdown/combo box.

    Features:
    - Consistent styling with design system
    - Auto-completion support
    - Editable option

    Usage:
        combo = OmnixComboBox(items=["Option 1", "Option 2", "Option 3"])
        combo = OmnixComboBox(items=data, editable=True)
    """

    def __init__(
        self,
        items: Optional[List[str]] = None,
        editable: bool = False,
        placeholder: str = "",
        parent: Optional[object] = None,
    ):
        """
        Initialize Omnix combo box.

        Args:
            items: List of items to populate
            editable: Allow custom text input
            placeholder: Placeholder text (when editable)
            parent: Parent widget
        """
        super().__init__(parent)

        # Add items
        if items:
            self.addItems(items)

        # Set editable
        if editable:
            self.setEditable(True)
            if placeholder:
                self.setPlaceholderText(placeholder)

            # Enable auto-completion
            completer = QCompleter(items or [], self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.setCompleter(completer)

    def add_item(self, item: str, user_data=None):
        """
        Add a single item to the combo box.

        Args:
            item: Item text
            user_data: Optional user data associated with item
        """
        if user_data is not None:
            self.addItem(item, user_data)
        else:
            self.addItem(item)

    def add_items(self, items: List[str]):
        """
        Add multiple items to the combo box.

        Args:
            items: List of item texts
        """
        self.addItems(items)

    def clear_items(self):
        """Clear all items from the combo box."""
        self.clear()

    def get_current_value(self) -> str:
        """
        Get the currently selected value.

        Returns:
            Current text value
        """
        return self.currentText()

    def set_current_value(self, value: str):
        """
        Set the current value.

        Args:
            value: Value to select
        """
        index = self.findText(value)
        if index >= 0:
            self.setCurrentIndex(index)
