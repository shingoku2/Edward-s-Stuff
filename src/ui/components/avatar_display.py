"""
Omnix Avatar Display Component
================================

Visual display component showing the AI assistant avatar and game context.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPen
from typing import Optional
from ..tokens import COLORS, SPACING, RADIUS, TYPOGRAPHY


class AvatarCircle(QWidget):
    """
    Custom widget for drawing the animated avatar circle.
    This widget handles its own painting to avoid QPainter crashes.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.animation_frame = 0
        self.setFixedSize(200, 200)

    def paintEvent(self, event):
        """Custom paint event for the avatar circle."""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Calculate center
            center_x = self.width() // 2
            center_y = self.height() // 2
            radius = min(center_x, center_y) - 10

            # Safety check
            if radius <= 0:
                return

            # Draw outer glow ring (animated)
            glow_radius = radius + 5 + (3 * abs((self.animation_frame % 60) - 30) / 30)
            glow_gradient = QRadialGradient(center_x, center_y, glow_radius)
            glow_gradient.setColorAt(0, QColor(0, 191, 255, 100))
            glow_gradient.setColorAt(0.7, QColor(0, 191, 255, 50))
            glow_gradient.setColorAt(1, QColor(0, 191, 255, 0))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow_gradient)
            painter.drawEllipse(int(center_x - glow_radius), int(center_y - glow_radius),
                              int(glow_radius * 2), int(glow_radius * 2))

            # Draw main avatar circle with gradient
            gradient = QRadialGradient(center_x, center_y, radius)
            gradient.setColorAt(0, QColor(57, 255, 20, 200))  # Neon green center
            gradient.setColorAt(0.5, QColor(0, 191, 255, 150))  # Electric blue
            gradient.setColorAt(1, QColor(44, 44, 74, 200))  # Dark edge

            painter.setBrush(gradient)
            painter.setPen(QPen(QColor(0, 191, 255), 2))
            painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))

            # Draw inner symbol (hexagon logo)
            self._draw_hexagon(painter, center_x, center_y, radius * 0.5)

        except Exception as e:
            # Log the error but don't crash the app
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in AvatarCircle.paintEvent: {e}", exc_info=True)

        finally:
            # Always end the painter to prevent crashes
            painter.end()

    def _draw_hexagon(self, painter: QPainter, center_x: int, center_y: int, size: float):
        """Draw a hexagon symbol in the center of the avatar."""
        try:
            import math

            painter.setPen(QPen(QColor(255, 255, 255, 230), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            # Calculate hexagon points
            points = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                x = center_x + size * math.cos(angle)
                y = center_y + size * math.sin(angle)
                points.append((x, y))

            # Draw hexagon
            for i in range(6):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % 6]
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

            # Draw inner lines
            rotation_offset = (self.animation_frame % 120) * 3
            painter.setPen(QPen(QColor(0, 191, 255, 150), 2))
            for i in range(3):
                angle = math.radians(rotation_offset + 120 * i)
                x = center_x + size * 0.7 * math.cos(angle)
                y = center_y + size * 0.7 * math.sin(angle)
                painter.drawLine(center_x, center_y, int(x), int(y))

        except Exception as e:
            # Log the error but don't crash the app
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in AvatarCircle._draw_hexagon: {e}", exc_info=True)


class OmnixAvatarDisplay(QFrame):
    """
    Avatar display component showing AI assistant visualization and context.

    Features:
    - Animated circular avatar with gradient effects
    - Game context display
    - Status indicators
    - Smooth animations

    Usage:
        avatar = OmnixAvatarDisplay()
        avatar.set_game_context("Elden Ring")
        avatar.set_status("Active")
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize avatar display.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # State
        self.game_context = None
        self.status = "Ready"

        # Setup UI
        self._init_ui()

        # Setup animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(50)  # 20 FPS animation

    def _init_ui(self):
        """Initialize the UI components."""
        # Apply styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(44, 44, 74, 0.4);
                border: 1px solid {COLORS.border_subtle};
                border-radius: {RADIUS.lg}px;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING.xl, SPACING.xl, SPACING.xl, SPACING.xl)
        main_layout.setSpacing(SPACING.lg)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Avatar circle container - now using custom AvatarCircle widget
        self.avatar_container = AvatarCircle()
        main_layout.addWidget(self.avatar_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(SPACING.sm)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title label
        self.title_label = QLabel("Omnix AI Assistant")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.accent_primary};
                font-size: {TYPOGRAPHY.size_xl}pt;
                font-weight: {TYPOGRAPHY.weight_bold};
                background: transparent;
                border: none;
            }}
        """)
        info_layout.addWidget(self.title_label)

        # Status label
        self.status_label = QLabel(self.status)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.accent_secondary};
                font-size: {TYPOGRAPHY.size_base}pt;
                font-weight: {TYPOGRAPHY.weight_medium};
                background: transparent;
                border: none;
            }}
        """)
        info_layout.addWidget(self.status_label)

        # Game context label
        self.game_label = QLabel("")
        self.game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.text_secondary};
                font-size: {TYPOGRAPHY.size_sm}pt;
                font-weight: {TYPOGRAPHY.weight_normal};
                background: transparent;
                border: none;
            }}
        """)
        info_layout.addWidget(self.game_label)

        main_layout.addLayout(info_layout)

        self.setLayout(main_layout)

    def _animate(self):
        """Update animation frame."""
        self.avatar_container.animation_frame += 1
        self.avatar_container.update()

    def set_game_context(self, game_name: Optional[str]):
        """
        Set the current game context.

        Args:
            game_name: Name of the current game or None
        """
        self.game_context = game_name
        if game_name:
            self.game_label.setText(f"🎮 Playing: {game_name}")
            self.status_label.setText("Active")
        else:
            self.game_label.setText("No game detected")
            self.status_label.setText("Ready")

    def set_status(self, status: str):
        """
        Set the status text.

        Args:
            status: Status message to display
        """
        self.status = status
        self.status_label.setText(status)

    def set_thinking(self, thinking: bool):
        """
        Set thinking state (changes animation speed).

        Args:
            thinking: True if AI is processing
        """
        if thinking:
            self.animation_timer.setInterval(30)  # Faster animation
            self.status_label.setText("Thinking...")
        else:
            self.animation_timer.setInterval(50)  # Normal animation
            self.status_label.setText(self.status)
