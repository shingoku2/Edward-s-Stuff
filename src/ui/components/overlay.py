"""
Omnix Overlay Components
=========================

Components specifically designed for the in-game overlay.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional
from ..tokens import COLORS, SPACING, RADIUS, TYPOGRAPHY
from .inputs import OmnixLineEdit
from .buttons import OmnixButton


class OmnixOverlayPanel(QFrame):
    """
    Semi-transparent overlay panel.

    A panel designed for the in-game overlay with transparency and minimal chrome.

    Usage:
        panel = OmnixOverlayPanel(opacity=0.75)
        panel.layout().addWidget(some_widget)
    """

    def __init__(
        self,
        opacity: float = 0.75,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize overlay panel.

        Args:
            opacity: Background opacity (0.0 to 1.0)
            parent: Parent widget
        """
        super().__init__(parent)

        self.opacity = opacity

        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Apply styling
        bg_alpha = format(int(opacity * 255), '02x')
        self.setStyleSheet(f"""
            OmnixOverlayPanel {{
                background-color: #0F0F1A{bg_alpha};
                border: 1px solid {COLORS.accent_primary};
                border-radius: {RADIUS.md}px;
            }}
        """)

        # Create layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACING.md, SPACING.md, SPACING.md, SPACING.md)
        self._layout.setSpacing(SPACING.sm)
        self.setLayout(self._layout)

    def layout(self) -> QVBoxLayout:
        """Get the panel's layout."""
        return self._layout


class OmnixOverlayChatWidget(QWidget):
    """
    Minimalist chat widget for overlay.

    A compact chat interface designed for in-game use.

    Signals:
        message_sent: Emitted when user sends a message (message: str)

    Usage:
        chat = OmnixOverlayChatWidget()
        chat.message_sent.connect(handle_message)
        chat.add_message("AI", "Hello! How can I help?")
    """

    message_sent = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize overlay chat widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING.sm)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: #2A2A4A80;
                color: {COLORS.text_primary};
                border: none;
                border-radius: {RADIUS.sm}px;
                padding: {SPACING.sm}px;
                font-size: {TYPOGRAPHY.size_sm}pt;
            }}
        """)
        layout.addWidget(self.chat_display, 1)

        # Input area
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(SPACING.sm)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Input field
        self.input_field = OmnixLineEdit(placeholder="Ask Omnix...")
        self.input_field.returnPressed.connect(self._send_message)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2A2A4AB2;
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.accent_primary};
                border-radius: {RADIUS.sm}px;
                padding: 8px;
                font-size: {TYPOGRAPHY.size_sm}pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS.accent_primary_bright};
            }}
        """)
        input_layout.addWidget(self.input_field, 1)

        # Send button
        self.send_button = OmnixButton("Send", style="primary")
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #00BFFF4D;
                color: {COLORS.text_primary};
                border: 1px solid {COLORS.accent_primary};
                border-radius: {RADIUS.sm}px;
                padding: 8px 16px;
                font-size: {TYPOGRAPHY.size_sm}pt;
                font-weight: {TYPOGRAPHY.weight_semibold};
            }}
            QPushButton:hover {{
                background-color: {COLORS.accent_primary};
            }}
        """)
        input_layout.addWidget(self.send_button)

        layout.addWidget(input_container)

    def _send_message(self):
        """Send message from input field."""
        message = self.input_field.text().strip()
        if message:
            self.add_message("You", message)
            self.message_sent.emit(message)
            self.input_field.clear()

    def add_message(self, sender: str, message: str):
        """
        Add a message to the chat display.

        Args:
            sender: Message sender name
            message: Message text
        """
        # Determine color based on sender
        if sender.lower() in ["ai", "omnix", "assistant"]:
            sender_color = COLORS.accent_primary
        else:
            sender_color = COLORS.text_secondary

        # Format message
        html = f"""
        <div style="margin: 4px 0;">
            <span style="color: {sender_color}; font-weight: 600;">{sender}:</span>
            <span style="color: {COLORS.text_primary};">{message}</span>
        </div>
        """

        self.chat_display.append(html)

        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class OmnixOverlayTip(QWidget):
    """
    Contextual tip popup for overlay.

    A small, semi-transparent popup that shows tips and fades out.

    Usage:
        tip = OmnixOverlayTip(
            message="Low HP detected! Consider healing.",
            duration=3000
        )
        tip.show_tip()
    """

    def __init__(
        self,
        message: str = "",
        duration: int = 3000,
        tip_type: str = "info",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize overlay tip.

        Args:
            message: Tip message
            duration: Display duration in milliseconds
            tip_type: Tip type (info, warning, danger)
            parent: Parent widget
        """
        super().__init__(parent)

        self.duration = duration

        # Set window flags for overlay
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Determine colors
        tip_colors = {
            "info": COLORS.accent_primary,
            "warning": COLORS.warning,
            "danger": COLORS.error,
        }
        border_color = tip_colors.get(tip_type, COLORS.accent_primary)

        # Styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2A2A4AE6;
                border: 1px solid {border_color};
                border-radius: {RADIUS.md}px;
            }}
            QLabel {{
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.size_sm}pt;
            }}
        """)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING.md, SPACING.sm, SPACING.md, SPACING.sm)
        layout.setSpacing(SPACING.sm)

        # Icon (optional)
        icons = {
            "info": "💡",
            "warning": "⚠️",
            "danger": "❗",
        }
        if tip_type in icons:
            icon_label = QLabel(icons[tip_type])
            layout.addWidget(icon_label)

        # Message
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Auto-hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_tip)

        # Initially hidden
        self.hide()

    def show_tip(self, message: Optional[str] = None):
        """
        Show the tip.

        Args:
            message: Optional new message to display
        """
        if message:
            self.message_label.setText(message)

        self.show()
        self.hide_timer.start(self.duration)

    def hide_tip(self):
        """Hide the tip."""
        self.hide()

    def set_message(self, message: str):
        """
        Update tip message.

        Args:
            message: New message
        """
        self.message_label.setText(message)


class OmnixOverlayStatus(QWidget):
    """
    Status indicator for overlay.

    Shows game state or macro status.

    Usage:
        status = OmnixOverlayStatus()
        status.set_status("Macro Active", "success")
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize overlay status.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2A2A4ACC;
                border: 1px solid {COLORS.accent_primary};
                border-radius: {RADIUS.sm}px;
            }}
        """)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING.sm, SPACING.xs, SPACING.sm, SPACING.xs)
        layout.setSpacing(SPACING.sm)

        # Indicator dot
        self.indicator = QLabel()
        self.indicator.setFixedSize(8, 8)
        layout.addWidget(self.indicator)

        # Status text
        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.size_xs}pt;
                font-weight: {TYPOGRAPHY.weight_medium};
            }}
        """)
        layout.addWidget(self.status_text)

        # Set default status
        self.set_status("Ready", "info")

    def set_status(self, text: str, status: str = "info"):
        """
        Set status.

        Args:
            text: Status text
            status: Status type (info, success, warning, danger)
        """
        self.status_text.setText(text)

        status_colors = {
            "info": COLORS.info,
            "success": COLORS.success,
            "warning": COLORS.warning,
            "danger": COLORS.error,
        }

        color = status_colors.get(status, COLORS.info)

        self.indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
