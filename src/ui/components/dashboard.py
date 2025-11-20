"""
Omnix Dashboard Component
=========================

Main dashboard overlay with status card and action grid.
Implements the futuristic gaming companion interface.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional
from ..tokens import COLORS, SPACING, RADIUS, TYPOGRAPHY
from ..icons import icons
from .dashboard_button import OmnixDashboardButton


class OmnixStatusCard(QFrame):
    """
    Status card showing AI assistant info and current activity.

    Displays:
    - Assistant name and branding
    - Active/Inactive status
    - Current game being played

    Usage:
        status = OmnixStatusCard()
        status.set_game("Elden Ring")
        status.set_active(True)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize status card.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Apply glassmorphism styling
        self.setStyleSheet(f"""
            OmnixStatusCard {{
                background-color: {COLORS.bg_secondary};
                border: 1px solid {COLORS.border_default};
                border-radius: {RADIUS.lg}px;
                padding: {SPACING.lg}px;
            }}
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
        layout.setSpacing(SPACING.md)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title: "Omnix AI Assistant"
        self.title_label = QLabel("Omnix AI Assistant")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.accent_primary};
                font-size: {TYPOGRAPHY.size_3xl}pt;
                font-weight: {TYPOGRAPHY.weight_bold};
                letter-spacing: 0.05em;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.title_label)

        # Status indicator container
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(SPACING.sm)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status dot
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.accent_secondary};
                font-size: {TYPOGRAPHY.size_xl}pt;
                background: transparent;
                border: none;
            }}
        """)
        status_layout.addWidget(self.status_dot)

        # Status text
        self.status_label = QLabel("Active")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.accent_secondary};
                font-size: {TYPOGRAPHY.size_lg}pt;
                font-weight: {TYPOGRAPHY.weight_semibold};
                background: transparent;
                border: none;
            }}
        """)
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_container)

        # Activity indicator container
        activity_container = QWidget()
        activity_layout = QHBoxLayout(activity_container)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.setSpacing(SPACING.sm)
        activity_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Game icon
        game_icon = icons.get_pixmap("game", color=COLORS.text_secondary, size=24)
        self.game_icon_label = QLabel()
        self.game_icon_label.setPixmap(game_icon)
        self.game_icon_label.setStyleSheet("background: transparent; border: none;")
        activity_layout.addWidget(self.game_icon_label)

        # Activity text
        self.activity_label = QLabel("Playing: No Game Detected")
        self.activity_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.text_secondary};
                font-size: {TYPOGRAPHY.size_md}pt;
                background: transparent;
                border: none;
            }}
        """)
        activity_layout.addWidget(self.activity_label)

        layout.addWidget(activity_container)

        self.setLayout(layout)

    def set_active(self, active: bool):
        """
        Set active status.

        Args:
            active: True if AI assistant is active
        """
        if active:
            self.status_label.setText("Active")
            self.status_dot.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS.accent_secondary};
                    font-size: {TYPOGRAPHY.size_xl}pt;
                    background: transparent;
                    border: none;
                }}
            """)
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS.accent_secondary};
                    font-size: {TYPOGRAPHY.size_lg}pt;
                    font-weight: {TYPOGRAPHY.weight_semibold};
                    background: transparent;
                    border: none;
                }}
            """)
        else:
            self.status_label.setText("Inactive")
            self.status_dot.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS.text_muted};
                    font-size: {TYPOGRAPHY.size_xl}pt;
                    background: transparent;
                    border: none;
                }}
            """)
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS.text_muted};
                    font-size: {TYPOGRAPHY.size_lg}pt;
                    font-weight: {TYPOGRAPHY.weight_semibold};
                    background: transparent;
                    border: none;
                }}
            """)

    def set_game(self, game_name: Optional[str]):
        """
        Set current game being played.

        Args:
            game_name: Name of the game, or None if no game detected
        """
        if game_name:
            self.activity_label.setText(f"Playing: {game_name}")
        else:
            self.activity_label.setText("Playing: No Game Detected")


class OmnixDashboard(QWidget):
    """
    Main Omnix dashboard overlay.

    Features a status card at the top and a grid of action buttons below.
    Implements the futuristic gaming companion interface with glassmorphism
    and neon accents.

    Signals:
        chat_clicked: User clicked Chat button
        provider_clicked: User clicked AI Provider button
        settings_clicked: User clicked Settings button
        profiles_clicked: User clicked Game Profiles button
        knowledge_clicked: User clicked Knowledge Pack button
        coaching_clicked: User clicked Session Coaching button

    Usage:
        dashboard = OmnixDashboard()
        dashboard.chat_clicked.connect(open_chat)
        dashboard.set_game("Elden Ring")
    """

    # Signals for button clicks
    chat_clicked = pyqtSignal()
    provider_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    profiles_clicked = pyqtSignal()
    knowledge_clicked = pyqtSignal()
    coaching_clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize Omnix dashboard.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set transparent background for overlay
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING.xl2, SPACING.xl2, SPACING.xl2, SPACING.xl2)
        main_layout.setSpacing(SPACING.xl)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status card (Hero section)
        self.status_card = OmnixStatusCard()
        main_layout.addWidget(self.status_card)

        # Action grid container
        grid_container = QWidget()
        grid_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS.bg_secondary};
                border: 1px solid {COLORS.border_default};
                border-radius: {RADIUS.lg}px;
            }}
        """)

        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
        grid_layout.setSpacing(SPACING.md)

        # Create dashboard buttons (3 columns x 2 rows)
        self.buttons = {
            'chat': OmnixDashboardButton("chat", "Chat"),
            'provider': OmnixDashboardButton("ai", "AI Provider"),
            'settings': OmnixDashboardButton("settings", "Settings"),
            'profiles': OmnixDashboardButton("game", "Game Profiles"),
            'knowledge': OmnixDashboardButton("knowledge", "Knowledge Pack"),
            'coaching': OmnixDashboardButton("session", "Session Coaching"),
        }

        # Connect signals
        self.buttons['chat'].clicked.connect(self.chat_clicked.emit)
        self.buttons['provider'].clicked.connect(self.provider_clicked.emit)
        self.buttons['settings'].clicked.connect(self.settings_clicked.emit)
        self.buttons['profiles'].clicked.connect(self.profiles_clicked.emit)
        self.buttons['knowledge'].clicked.connect(self.knowledge_clicked.emit)
        self.buttons['coaching'].clicked.connect(self.coaching_clicked.emit)

        # Add buttons to grid (3 columns x 2 rows)
        grid_layout.addWidget(self.buttons['chat'], 0, 0)
        grid_layout.addWidget(self.buttons['provider'], 0, 1)
        grid_layout.addWidget(self.buttons['settings'], 0, 2)
        grid_layout.addWidget(self.buttons['profiles'], 1, 0)
        grid_layout.addWidget(self.buttons['knowledge'], 1, 1)
        grid_layout.addWidget(self.buttons['coaching'], 1, 2)

        main_layout.addWidget(grid_container)

        self.setLayout(main_layout)

    def set_game(self, game_name: Optional[str]):
        """
        Set current game being played.

        Args:
            game_name: Name of the game, or None if no game detected
        """
        self.status_card.set_game(game_name)

    def set_active(self, active: bool):
        """
        Set AI assistant active status.

        Args:
            active: True if AI assistant is active
        """
        self.status_card.set_active(active)
