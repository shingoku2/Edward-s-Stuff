"""
OverlayWindow Widget
"""
import logging

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from config import Config
from ui.components import OmnixIconButton
from ui.tokens import COLORS, RADIUS, SPACING, TYPOGRAPHY
from .chat import ChatWidget

logger = logging.getLogger(__name__)


class OverlayWindow(QWidget):
    """Frameless in-game overlay window with drag/resize/minimize functionality"""

    def __init__(self, ai_assistant, config, design_system, parent=None):
        super().__init__(parent)
        self.ai_assistant = ai_assistant
        self.config = config
        self.design_system = design_system

        # Track dragging state
        self.dragging = False
        self.drag_position = None

        # Track resize state
        self.resizing = False
        self.resize_direction = None

        # Track minimized state
        self.is_minimized = config.overlay_minimized
        self.normal_height = config.overlay_height

        # Debounce timer for saving window state
        # This prevents excessive disk I/O during window move/resize
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._do_save_window_state)
        self.save_timer.setInterval(500)  # Wait 500ms after user stops moving/resizing

        self.init_ui()

    def init_ui(self):
        """Initialize overlay UI with frameless design"""
        self.setWindowTitle("Gaming AI Assistant - Overlay")

        # Make window frameless and always on top
        # Use Window type (not Tool) to prevent hiding when focus changes
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        # Set window position and size from config
        self.setGeometry(
            self.config.overlay_x,
            self.config.overlay_y,
            self.config.overlay_width,
            self.config.overlay_height,
        )

        # Enable mouse tracking for resize grips
        self.setMouseTracking(True)

        # Apply design system overlay stylesheet with transparency
        self.setStyleSheet(
            self.design_system.generate_overlay_stylesheet(self.config.overlay_opacity)
        )

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with title and minimize button
        self.header = self.create_header()
        main_layout.addWidget(self.header)

        # Chat widget
        self.chat_widget = ChatWidget(self.ai_assistant)
        main_layout.addWidget(self.chat_widget)

        self.setLayout(main_layout)

        logger.info("Overlay window initialized")

    def create_header(self) -> QWidget:
        """Create custom header with title and window controls using OmnixHeaderBar"""
        header_container = QFrame()
        header_container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.bg_primary_alt};
                border-top-left-radius: {RADIUS.md}px;
                border-top-right-radius: {RADIUS.md}px;
                border-bottom: 1px solid {COLORS.border_subtle};
            }}
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(SPACING.base, SPACING.sm, SPACING.base, SPACING.sm)
        layout.setSpacing(SPACING.base)

        # Title section with icon
        title_layout = QVBoxLayout()
        title_label = QLabel("🎮 Gaming AI Assistant")
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.accent_primary};
                font-size: {TYPOGRAPHY.size_lg}pt;
                font-weight: {TYPOGRAPHY.weight_bold};
                background: transparent;
                border: none;
            }}
        """
        )
        title_layout.addWidget(title_label)

        subtitle = QLabel("In-Game Overlay")
        subtitle.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.text_muted};
                font-size: {TYPOGRAPHY.size_xs}pt;
                background: transparent;
                border: none;
            }}
        """
        )
        title_layout.addWidget(subtitle)

        layout.addLayout(title_layout)
        layout.addStretch()

        # Window control buttons using OmnixIconButton
        controls_layout = QHBoxLayout()

        # Minimize button
        self.minimize_button = OmnixIconButton(text="−", size=32)
        self.minimize_button.setToolTip("Minimize/Restore")
        self.minimize_button.clicked.connect(self.toggle_minimize)
        controls_layout.addWidget(self.minimize_button)

        # Close button with danger styling
        close_button = OmnixIconButton(text="×", size=32)
        close_button.setToolTip("Hide Overlay (Press hotkey to show again)")
        close_button.clicked.connect(self.hide)
        close_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.error};
            }}
            QPushButton:hover {{
                background-color: #FF5555;
            }}
            QPushButton:pressed {{
                background-color: #991b1b;
            }}
        """
        )
        controls_layout.addWidget(close_button)

        layout.addLayout(controls_layout)

        header_container.setLayout(layout)
        return header_container

    def mousePressEvent(self, event):
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking in header for dragging
            if self.header.geometry().contains(event.pos()):
                # Start dragging from header
                self.dragging = True
                self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
            else:
                # Check if clicking near edges for resize
                pos = event.pos()
                rect = self.rect()
                edge_margin = 10

                # Determine resize direction
                on_left = pos.x() < edge_margin
                on_right = pos.x() > rect.width() - edge_margin
                on_top = pos.y() < edge_margin
                on_bottom = pos.y() > rect.height() - edge_margin

                if on_left or on_right or on_top or on_bottom:
                    self.resizing = True
                    self.resize_direction = {
                        "left": on_left,
                        "right": on_right,
                        "top": on_top,
                        "bottom": on_bottom,
                    }
                    self.drag_position = event.globalPosition().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging and resizing"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.dragging and self.drag_position is not None:
                # Move window
                self.move(event.globalPosition().toPoint() - self.drag_position)

            elif self.resizing and self.resize_direction is not None:
                # Resize window
                delta = event.globalPosition().toPoint() - self.drag_position
                self.drag_position = event.globalPosition().toPoint()

                geometry = self.geometry()

                if self.resize_direction["left"]:
                    geometry.setLeft(geometry.left() + delta.x())
                if self.resize_direction["right"]:
                    geometry.setRight(geometry.right() + delta.x())
                if self.resize_direction["top"]:
                    geometry.setTop(geometry.top() + delta.y())
                if self.resize_direction["bottom"]:
                    geometry.setBottom(geometry.bottom() + delta.y())

                # Enforce minimum size
                if geometry.width() >= 400 and geometry.height() >= 300:
                    self.setGeometry(geometry)

        else:
            # Update cursor based on position
            pos = event.pos()
            rect = self.rect()
            edge_margin = 10

            on_left = pos.x() < edge_margin
            on_right = pos.x() > rect.width() - edge_margin
            on_top = pos.y() < edge_margin
            on_bottom = pos.y() > rect.height() - edge_margin

            if (on_left and on_top) or (on_right and on_bottom):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif (on_right and on_top) or (on_left and on_bottom):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif on_left or on_right:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif on_top or on_bottom:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release and save window position/size"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging or self.resizing:
                # Save window position and size to config
                self.save_window_state()

            self.dragging = False
            self.resizing = False
            self.resize_direction = None
            self.drag_position = None

        super().mouseReleaseEvent(event)

    def save_window_state(self):
        """
        Debounced save - schedules a save after user stops moving/resizing.
        This prevents excessive disk I/O during window manipulation.
        """
        # Restart the timer - if user is still moving/resizing, this delays the save
        self.save_timer.start()

    def _do_save_window_state(self):
        """Internal method: Actually save current window position and size to .env file"""
        geometry = self.geometry()
        Config.save_to_env(
            provider=self.config.ai_provider,
            session_tokens=self.config.session_tokens,
            overlay_hotkey=self.config.overlay_hotkey,
            check_interval=self.config.check_interval,
            overlay_x=geometry.x(),
            overlay_y=.y(),
            overlay_width=geometry.width(),
            overlay_height=geometry.height(),
            overlay_minimized=self.is_minimized,
            overlay_opacity=self.config.overlay_opacity,
        )
        logger.info(
            f"Saved overlay state: pos=({geometry.x()}, {geometry.y()}), size=({geometry.width()}x{geometry.height()})"
        )

    def toggle_minimize(self):
        """Toggle window minimized state"""
        if self.is_minimized:
            # Restore
            self.resize(self.width(), self.normal_height)
            self.is_minimized = False
        else:
            # Minimize
            self.normal_height = self.height()
            self.resize(self.width(), 50)  # Minimize to title bar height
            self.is_minimized = True

        # Save immediately for explicit minimize/restore actions
        self._do_save_window_state()

    def closeEvent(self, event):
        """Handle close event by hiding instead of destroying"""
        # Stop debounce timer and save immediately on close
        self.save_timer.stop()
        self._do_save_window_state()
        self.hide()
        event.ignore()
