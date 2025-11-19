"""
Omnix Layout Components
========================

Layout helper components for organizing widgets.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from typing import Optional, List, Tuple
from ..tokens import COLORS, SPACING


class OmnixVBox(QWidget):
    """
    Vertical box layout container.

    A widget with a vertical layout following design system spacing.

    Usage:
        vbox = OmnixVBox(spacing=12)
        vbox.add_widget(widget1)
        vbox.add_widget(widget2)
        vbox.add_stretch()
    """

    def __init__(
        self,
        spacing: int = SPACING.md,
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize vertical box layout.

        Args:
            spacing: Spacing between widgets in pixels
            margins: Layout margins (left, top, right, bottom)
            parent: Parent widget
        """
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(spacing)
        self._layout.setContentsMargins(*margins)
        self.setLayout(self._layout)

    def add_widget(self, widget: QWidget, stretch: int = 0, alignment=None):
        """
        Add a widget to the layout.

        Args:
            widget: Widget to add
            stretch: Stretch factor
            alignment: Widget alignment (Qt.AlignmentFlag)
        """
        if alignment:
            self._layout.addWidget(widget, stretch, alignment)
        else:
            self._layout.addWidget(widget, stretch)

    def add_layout(self, layout):
        """
        Add another layout to this layout.

        Args:
            layout: Layout to add
        """
        self._layout.addLayout(layout)

    def add_stretch(self, stretch: int = 1):
        """
        Add stretchable space.

        Args:
            stretch: Stretch factor
        """
        self._layout.addStretch(stretch)

    def add_spacing(self, spacing: int):
        """
        Add fixed spacing.

        Args:
            spacing: Spacing in pixels
        """
        self._layout.addSpacing(spacing)

    def layout(self) -> QVBoxLayout:
        """Get the underlying layout."""
        return self._layout


class OmnixHBox(QWidget):
    """
    Horizontal box layout container.

    A widget with a horizontal layout following design system spacing.

    Usage:
        hbox = OmnixHBox(spacing=8)
        hbox.add_widget(widget1)
        hbox.add_widget(widget2)
        hbox.add_stretch()
    """

    def __init__(
        self,
        spacing: int = SPACING.md,
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize horizontal box layout.

        Args:
            spacing: Spacing between widgets in pixels
            margins: Layout margins (left, top, right, bottom)
            parent: Parent widget
        """
        super().__init__(parent)

        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(spacing)
        self._layout.setContentsMargins(*margins)
        self.setLayout(self._layout)

    def add_widget(self, widget: QWidget, stretch: int = 0, alignment=None):
        """
        Add a widget to the layout.

        Args:
            widget: Widget to add
            stretch: Stretch factor
            alignment: Widget alignment (Qt.AlignmentFlag)
        """
        if alignment:
            self._layout.addWidget(widget, stretch, alignment)
        else:
            self._layout.addWidget(widget, stretch)

    def add_layout(self, layout):
        """
        Add another layout to this layout.

        Args:
            layout: Layout to add
        """
        self._layout.addLayout(layout)

    def add_stretch(self, stretch: int = 1):
        """
        Add stretchable space.

        Args:
            stretch: Stretch factor
        """
        self._layout.addStretch(stretch)

    def add_spacing(self, spacing: int):
        """
        Add fixed spacing.

        Args:
            spacing: Spacing in pixels
        """
        self._layout.addSpacing(spacing)

    def layout(self) -> QHBoxLayout:
        """Get the underlying layout."""
        return self._layout


class OmnixGrid(QWidget):
    """
    Grid layout container.

    A widget with a grid layout for structured content.

    Usage:
        grid = OmnixGrid(spacing=12)
        grid.add_widget(widget1, 0, 0)
        grid.add_widget(widget2, 0, 1)
        grid.add_widget(widget3, 1, 0, 1, 2)  # Span 2 columns
    """

    def __init__(
        self,
        spacing: int = SPACING.md,
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize grid layout.

        Args:
            spacing: Spacing between widgets in pixels
            margins: Layout margins (left, top, right, bottom)
            parent: Parent widget
        """
        super().__init__(parent)

        self._layout = QGridLayout(self)
        self._layout.setSpacing(spacing)
        self._layout.setContentsMargins(*margins)
        self.setLayout(self._layout)

    def add_widget(
        self,
        widget: QWidget,
        row: int,
        col: int,
        row_span: int = 1,
        col_span: int = 1,
        alignment=None,
    ):
        """
        Add a widget to the grid.

        Args:
            widget: Widget to add
            row: Row position
            col: Column position
            row_span: Number of rows to span
            col_span: Number of columns to span
            alignment: Widget alignment (Qt.AlignmentFlag)
        """
        if alignment:
            self._layout.addWidget(widget, row, col, row_span, col_span, alignment)
        else:
            self._layout.addWidget(widget, row, col, row_span, col_span)

    def add_layout(self, layout, row: int, col: int, row_span: int = 1, col_span: int = 1):
        """
        Add a layout to the grid.

        Args:
            layout: Layout to add
            row: Row position
            col: Column position
            row_span: Number of rows to span
            col_span: Number of columns to span
        """
        self._layout.addLayout(layout, row, col, row_span, col_span)

    def set_row_stretch(self, row: int, stretch: int):
        """
        Set stretch factor for a row.

        Args:
            row: Row index
            stretch: Stretch factor
        """
        self._layout.setRowStretch(row, stretch)

    def set_column_stretch(self, col: int, stretch: int):
        """
        Set stretch factor for a column.

        Args:
            col: Column index
            stretch: Stretch factor
        """
        self._layout.setColumnStretch(col, stretch)

    def layout(self) -> QGridLayout:
        """Get the underlying layout."""
        return self._layout


class OmnixFormLayout(OmnixGrid):
    """
    Form layout for label-input pairs.

    A specialized grid layout optimized for forms with labels and inputs.

    Usage:
        form = OmnixFormLayout()
        form.add_row("Username:", username_input)
        form.add_row("Password:", password_input)
    """

    def __init__(
        self,
        spacing: int = SPACING.md,
        label_col_width: Optional[int] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize form layout.

        Args:
            spacing: Spacing between rows
            label_col_width: Fixed width for label column (optional)
            parent: Parent widget
        """
        super().__init__(spacing=spacing, parent=parent)

        self._current_row = 0
        self._label_col_width = label_col_width

        # Set column stretches (labels don't stretch, inputs do)
        self.set_column_stretch(0, 0)  # Labels
        self.set_column_stretch(1, 1)  # Inputs

    def add_row(self, label_text: str, widget: QWidget):
        """
        Add a label-widget pair as a row.

        Args:
            label_text: Label text
            widget: Input widget
        """
        from PyQt6.QtWidgets import QLabel

        # Create label
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: 11pt;
                font-weight: 500;
            }}
        """)

        if self._label_col_width:
            label.setFixedWidth(self._label_col_width)

        # Add to grid
        self.add_widget(label, self._current_row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.add_widget(widget, self._current_row, 1)

        self._current_row += 1

    def add_full_width_widget(self, widget: QWidget):
        """
        Add a widget that spans both columns.

        Args:
            widget: Widget to add
        """
        self.add_widget(widget, self._current_row, 0, 1, 2)
        self._current_row += 1
