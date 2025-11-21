"""
Omnix Icon System
==================

Icon system for the Omnix UI design system.
Provides access to SVG-based icons and icon utilities.
"""

from typing import Optional

try:
    from PyQt6.QtCore import QSize, Qt
    from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
    from PyQt6.QtSvg import QSvgRenderer

    _PYQT_AVAILABLE = True
    _PYQT_IMPORT_ERROR = None
except ImportError as exc:  # pragma: no cover - exercised in headless CI
    QIcon = QPixmap = QPainter = QColor = None  # type: ignore[assignment]
    Qt = QSize = None  # type: ignore[assignment]
    QSvgRenderer = None  # type: ignore[assignment]
    _PYQT_AVAILABLE = False
    _PYQT_IMPORT_ERROR = exc

try:
    from .tokens import COLORS
except ImportError:  # Support importing module as top-level `icons`
    from tokens import COLORS


class OmnixIcons:
    """
    Omnix icon collection.

    Provides access to all Omnix UI icons as QIcon objects.
    Icons are rendered from SVG data for scalability.
    """

    # SVG icon data (simplified geometric line-art style)
    _SVG_ICONS = {
        "omnix_logo": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Hexagonal O with circuit pattern -->
                <path d="M 50,10 L 80,25 L 80,60 L 50,75 L 20,60 L 20,25 Z"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <path d="M 50,25 L 65,35 L 65,50 L 50,60 L 35,50 L 35,35 Z"
                      fill="none" stroke="{color}" stroke-width="2"/>
                <circle cx="50" cy="42.5" r="2" fill="{color}"/>
                <line x1="50" y1="25" x2="50" y2="35" stroke="{color}" stroke-width="1.5"/>
                <line x1="50" y1="50" x2="50" y2="60" stroke="{color}" stroke-width="1.5"/>
            </svg>
        """,
        "chat": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Speech bubble -->
                <rect x="15" y="20" width="70" height="50" rx="8"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <path d="M 35,70 L 30,85 L 45,70 Z" fill="{color}"/>
                <line x1="30" y1="40" x2="70" y2="40" stroke="{color}" stroke-width="2.5"/>
                <line x1="30" y1="55" x2="60" y2="55" stroke="{color}" stroke-width="2.5"/>
            </svg>
        """,
        "settings": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Gear -->
                <circle cx="50" cy="50" r="15" fill="none" stroke="{color}" stroke-width="3"/>
                <circle cx="50" cy="50" r="8" fill="{color}"/>
                <rect x="48" y="15" width="4" height="12" fill="{color}"/>
                <rect x="48" y="73" width="4" height="12" fill="{color}"/>
                <rect x="15" y="48" width="12" height="4" fill="{color}"/>
                <rect x="73" y="48" width="12" height="4" fill="{color}"/>
                <rect x="25" y="25" width="4" height="10" fill="{color}"
                      transform="rotate(45 27 30)"/>
                <rect x="71" y="25" width="4" height="10" fill="{color}"
                      transform="rotate(-45 73 30)"/>
                <rect x="25" y="71" width="4" height="10" fill="{color}"
                      transform="rotate(-45 27 76)"/>
                <rect x="71" y="71" width="4" height="10" fill="{color}"
                      transform="rotate(45 73 76)"/>
            </svg>
        """,
        "knowledge": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Book with circuit overlay -->
                <rect x="20" y="25" width="60" height="55" rx="4"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <line x1="50" y1="25" x2="50" y2="80" stroke="{color}" stroke-width="2"/>
                <line x1="30" y1="40" x2="45" y2="40" stroke="{color}" stroke-width="2"/>
                <line x1="30" y1="50" x2="45" y2="50" stroke="{color}" stroke-width="2"/>
                <line x1="30" y1="60" x2="45" y2="60" stroke="{color}" stroke-width="2"/>
                <circle cx="65" cy="45" r="3" fill="{color}"/>
                <circle cx="65" cy="55" r="3" fill="{color}"/>
                <line x1="65" y1="48" x2="65" y2="52" stroke="{color}" stroke-width="2"/>
            </svg>
        """,
        "game": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Game controller -->
                <path d="M 30,40 Q 20,40 20,50 L 20,60 Q 20,70 30,70 L 45,70 L 55,70 L 70,70 Q 80,70 80,60 L 80,50 Q 80,40 70,40 Z"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <!-- D-pad -->
                <line x1="32" y1="55" x2="42" y2="55" stroke="{color}" stroke-width="2.5"/>
                <line x1="37" y1="50" x2="37" y2="60" stroke="{color}" stroke-width="2.5"/>
                <!-- Buttons -->
                <circle cx="65" cy="52" r="3" fill="{color}"/>
                <circle cx="72" cy="58" r="3" fill="{color}"/>
            </svg>
        """,
        "macro": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Keyboard with arrow -->
                <rect x="20" y="40" width="60" height="30" rx="4"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <rect x="28" y="48" width="8" height="6" fill="{color}"/>
                <rect x="40" y="48" width="8" height="6" fill="{color}"/>
                <rect x="52" y="48" width="8" height="6" fill="{color}"/>
                <rect x="64" y="48" width="8" height="6" fill="{color}"/>
                <rect x="28" y="58" width="44" height="6" fill="{color}"/>
                <path d="M 65,25 L 75,15 L 85,25" fill="none" stroke="{color}" stroke-width="2.5"/>
                <line x1="75" y1="15" x2="75" y2="35" stroke="{color}" stroke-width="2.5"/>
            </svg>
        """,
        "ai": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- AI head profile with brain/data flow -->
                <path d="M 30,30 Q 40,20 50,20 Q 60,20 70,30 L 70,60 Q 65,70 50,70 Q 35,70 30,60 Z"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <circle cx="55" cy="40" r="3" fill="{color}"/>
                <path d="M 40,35 Q 45,30 50,35" fill="none" stroke="{color}" stroke-width="2"/>
                <line x1="45" y1="50" x2="45" y2="55" stroke="{color}" stroke-width="2"/>
                <line x1="55" y1="50" x2="55" y2="55" stroke="{color}" stroke-width="2"/>
                <circle cx="48" cy="52" r="1.5" fill="{color}"/>
                <circle cx="52" cy="52" r="1.5" fill="{color}"/>
            </svg>
        """,
        "session": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Stopwatch with graph -->
                <circle cx="50" cy="50" r="25" fill="none" stroke="{color}" stroke-width="3"/>
                <line x1="50" y1="50" x2="50" y2="35" stroke="{color}" stroke-width="2.5"/>
                <line x1="50" y1="50" x2="62" y2="55" stroke="{color}" stroke-width="2.5"/>
                <rect x="45" y="20" width="10" height="5" rx="2" fill="{color}"/>
                <path d="M 30,75 L 35,70 L 40,72 L 45,68 L 50,70 L 55,65 L 60,68 L 65,70 L 70,75"
                      fill="none" stroke="{color}" stroke-width="2"/>
            </svg>
        """,
        "secure": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Shield with lock -->
                <path d="M 50,15 L 70,25 L 70,50 Q 70,70 50,85 Q 30,70 30,50 L 30,25 Z"
                      fill="none" stroke="{color}" stroke-width="3"/>
                <rect x="43" y="48" width="14" height="15" rx="2"
                      fill="none" stroke="{color}" stroke-width="2"/>
                <path d="M 45,48 L 45,43 Q 45,38 50,38 Q 55,38 55,43 L 55,48"
                      fill="none" stroke="{color}" stroke-width="2"/>
                <circle cx="50" cy="56" r="2" fill="{color}"/>
            </svg>
        """,
        "add": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="30" fill="none" stroke="{color}" stroke-width="3"/>
                <line x1="35" y1="50" x2="65" y2="50" stroke="{color}" stroke-width="3"/>
                <line x1="50" y1="35" x2="50" y2="65" stroke="{color}" stroke-width="3"/>
            </svg>
        """,
        "close": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <line x1="30" y1="30" x2="70" y2="70" stroke="{color}" stroke-width="4"/>
                <line x1="70" y1="30" x2="30" y2="70" stroke="{color}" stroke-width="4"/>
            </svg>
        """,
        "minimize": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <line x1="30" y1="50" x2="70" y2="50" stroke="{color}" stroke-width="4"/>
            </svg>
        """,
        "maximize": """
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <rect x="30" y="30" width="40" height="40"
                      fill="none" stroke="{color}" stroke-width="4"/>
            </svg>
        """,
    }

    @staticmethod
    def get_icon(name: str, color: Optional[str] = None, size: int = 32) -> QIcon:
        """
        Get an icon by name.

        Args:
            name: Icon name
            color: Icon color (hex or color name), defaults to accent primary
            size: Icon size in pixels

        Returns:
            QIcon object
        """
        if not _PYQT_AVAILABLE:
            raise RuntimeError(
                "PyQt6 is required to render icons. Install PyQt6 or run the app "
                "in an environment with GUI support."
            ) from _PYQT_IMPORT_ERROR

        if color is None:
            color = COLORS.accent_primary

        svg_template = OmnixIcons._SVG_ICONS.get(name, OmnixIcons._SVG_ICONS["omnix_logo"])
        svg_data = svg_template.format(color=color).encode("utf-8")

        # Create QPixmap from SVG
        renderer = QSvgRenderer(svg_data)
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def get_pixmap(name: str, color: Optional[str] = None, size: int = 32) -> QPixmap:
        """
        Get an icon as a QPixmap.

        Args:
            name: Icon name
            color: Icon color (hex or color name), defaults to accent primary
            size: Icon size in pixels

        Returns:
            QPixmap object
        """
        icon = OmnixIcons.get_icon(name, color, size)
        return icon.pixmap(QSize(size, size))

    @staticmethod
    def available_icons() -> list:
        """
        Get list of available icon names.

        Returns:
            List of icon names
        """
        return list(OmnixIcons._SVG_ICONS.keys())


# Convenience aliases
icons = OmnixIcons()
