"""
Theme Manager Module (DEPRECATED)
==================================

⚠️  DEPRECATION WARNING ⚠️
This module is deprecated and will be removed in a future version.

**Migration Path:**
- For new code: Use `ui.theme_manager.OmnixThemeManager`
- For legacy code: Use `theme_compat.ThemeManagerCompat`

**Why Deprecated:**
This legacy theme system has been replaced with a modern token-based design system
that provides better customization, real-time updates, and cleaner architecture.

**New System:**
- `src/ui/theme_manager.py` - Modern OmnixThemeManager
- `src/ui/tokens.py` - Design tokens
- `src/ui/design_system.py` - Stylesheet generator
- `src/theme_compat.py` - Compatibility layer for migration

See THEME_MIGRATION_PLAN.md for full migration details.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ThemeMode(Enum):
    """Theme modes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Follow system theme


class UIScale(Enum):
    """UI scale presets"""
    SMALL = "small"     # 0.85x
    NORMAL = "normal"   # 1.0x
    LARGE = "large"     # 1.15x
    XLARGE = "xlarge"   # 1.3x


class LayoutMode(Enum):
    """Layout density"""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"


class OverlayPosition(Enum):
    """Preset overlay positions"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    CUSTOM = "custom"


@dataclass
class Theme:
    """Theme configuration"""
    # Theme mode
    mode: str = ThemeMode.DARK.value

    # Colors (hex format)
    primary_color: str = "#14b8a6"      # Teal
    secondary_color: str = "#f59e0b"    # Amber
    background_color: str = "#1e1e1e"   # Dark gray
    surface_color: str = "#2d2d2d"      # Lighter gray
    text_color: str = "#ffffff"         # White
    text_secondary_color: str = "#9ca3af"  # Gray

    # Error and success colors
    error_color: str = "#ef4444"        # Red
    success_color: str = "#10b981"      # Green
    warning_color: str = "#f59e0b"      # Amber

    # Typography
    font_family: str = "Segoe UI, Arial, sans-serif"
    font_size: int = 10  # Base font size in points
    ui_scale: str = UIScale.NORMAL.value

    # Layout
    layout_mode: str = LayoutMode.COMFORTABLE.value
    border_radius: int = 8  # Border radius in pixels
    spacing: int = 10  # Base spacing in pixels
    transparency: float = 1.0  # Window transparency 0.0-1.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Theme':
        """Create Theme from dictionary"""
        return Theme(**data)

    def get_scale_multiplier(self) -> float:
        """Get scale multiplier for UI elements"""
        scale_map = {
            UIScale.SMALL.value: 0.85,
            UIScale.NORMAL.value: 1.0,
            UIScale.LARGE.value: 1.15,
            UIScale.XLARGE.value: 1.3,
        }
        return scale_map.get(self.ui_scale, 1.0)

    def get_scaled_size(self, base_size: int) -> int:
        """Get scaled size based on UI scale"""
        return int(base_size * self.get_scale_multiplier())

    def get_spacing(self) -> int:
        """Get spacing based on layout mode"""
        if self.layout_mode == LayoutMode.COMPACT.value:
            return max(6, self.spacing - 4)
        return self.spacing


@dataclass
class OverlayAppearance:
    """Overlay-specific appearance settings"""
    # Position
    position_preset: str = OverlayPosition.TOP_RIGHT.value
    custom_x: int = 100
    custom_y: int = 100
    width: int = 900
    height: int = 700

    # Appearance
    opacity: float = 0.95
    scale: float = 1.0  # Additional scale multiplier for overlay
    show_header: bool = True
    show_minimize_button: bool = True

    # Behavior
    edge_snapping: bool = True
    snap_threshold: int = 20  # Pixels from edge to trigger snap
    stay_on_top: bool = True
    minimize_to_tray: bool = False

    # Visible panels/widgets
    show_chat: bool = True
    show_game_info: bool = True
    show_tips_panel: bool = False  # Future panel
    show_stats_panel: bool = False  # Future panel

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'OverlayAppearance':
        """Create OverlayAppearance from dictionary"""
        return OverlayAppearance(**data)

    def get_position_preset_coords(self, screen_width: int, screen_height: int) -> tuple[int, int]:
        """
        Get coordinates for position preset

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            Tuple of (x, y) coordinates
        """
        margin = 20  # Margin from edges

        preset_map = {
            OverlayPosition.TOP_LEFT.value: (margin, margin),
            OverlayPosition.TOP_RIGHT.value: (screen_width - self.width - margin, margin),
            OverlayPosition.BOTTOM_LEFT.value: (margin, screen_height - self.height - margin),
            OverlayPosition.BOTTOM_RIGHT.value: (
                screen_width - self.width - margin,
                screen_height - self.height - margin
            ),
            OverlayPosition.CENTER.value: (
                (screen_width - self.width) // 2,
                (screen_height - self.height) // 2
            ),
            OverlayPosition.CUSTOM.value: (self.custom_x, self.custom_y),
        }

        return preset_map.get(self.position_preset, (self.custom_x, self.custom_y))

    def apply_edge_snapping(self, x: int, y: int, screen_width: int, screen_height: int) -> tuple[int, int]:
        """
        Apply edge snapping to coordinates

        Args:
            x: Current X coordinate
            y: Current Y coordinate
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            Tuple of (snapped_x, snapped_y)
        """
        if not self.edge_snapping:
            return x, y

        snapped_x = x
        snapped_y = y

        # Snap to left edge
        if x < self.snap_threshold:
            snapped_x = 0

        # Snap to right edge
        if x + self.width > screen_width - self.snap_threshold:
            snapped_x = screen_width - self.width

        # Snap to top edge
        if y < self.snap_threshold:
            snapped_y = 0

        # Snap to bottom edge
        if y + self.height > screen_height - self.snap_threshold:
            snapped_y = screen_height - self.height

        return snapped_x, snapped_y


class ThemeManager:
    """
    Manages application themes and appearance

    Features:
    - Light/dark mode switching
    - Custom color schemes
    - Font and size customization
    - UI scale and density
    - Overlay appearance
    - Generate PyQt6 stylesheets
    """

    def __init__(self):
        """Initialize theme manager"""
        self.current_theme = Theme()
        self.overlay_appearance = OverlayAppearance()

    def set_theme(self, theme: Theme):
        """Set current theme"""
        self.current_theme = theme
        logger.info(f"Theme updated: mode={theme.mode}, scale={theme.ui_scale}")

    def set_overlay_appearance(self, appearance: OverlayAppearance):
        """Set overlay appearance"""
        self.overlay_appearance = appearance
        logger.info(f"Overlay appearance updated: position={appearance.position_preset}")

    def generate_stylesheet(self, for_overlay: bool = False) -> str:
        """
        Generate PyQt6 stylesheet from current theme

        Args:
            for_overlay: If True, generate for overlay window

        Returns:
            QSS stylesheet string
        """
        theme = self.current_theme
        scale = theme.get_scale_multiplier()

        # Apply overlay scale if needed
        if for_overlay:
            scale *= self.overlay_appearance.scale

        # Base sizes
        font_size = int(theme.font_size * scale)
        spacing = int(theme.spacing * scale)
        border_radius = int(theme.border_radius * scale)

        # Colors
        if theme.mode == ThemeMode.LIGHT.value:
            bg = "#ffffff"
            surface = "#f3f4f6"
            text = "#1f2937"
            text_secondary = "#6b7280"
            border = "#d1d5db"
        else:  # Dark mode
            bg = theme.background_color
            surface = theme.surface_color
            text = theme.text_color
            text_secondary = theme.text_secondary_color
            border = "#404040"

        primary = theme.primary_color
        secondary = theme.secondary_color
        error = theme.error_color
        success = theme.success_color

        # Generate stylesheet
        stylesheet = f"""
/* Main Application Styling */
QWidget {{
    background-color: {bg};
    color: {text};
    font-family: {theme.font_family};
    font-size: {font_size}pt;
}}

/* Buttons */
QPushButton {{
    background-color: {primary};
    color: white;
    border: none;
    border-radius: {border_radius}px;
    padding: {spacing}px {spacing*2}px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {self._adjust_color(primary, 1.1)};
}}

QPushButton:pressed {{
    background-color: {self._adjust_color(primary, 0.9)};
}}

QPushButton:disabled {{
    background-color: {border};
    color: {text_secondary};
}}

QPushButton.secondary {{
    background-color: {secondary};
}}

QPushButton.secondary:hover {{
    background-color: {self._adjust_color(secondary, 1.1)};
}}

QPushButton.danger {{
    background-color: {error};
}}

QPushButton.danger:hover {{
    background-color: {self._adjust_color(error, 1.1)};
}}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {surface};
    color: {text};
    border: 2px solid {border};
    border-radius: {border_radius}px;
    padding: {spacing}px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {primary};
}}

/* Labels */
QLabel {{
    color: {text};
    background: transparent;
}}

QLabel.secondary {{
    color: {text_secondary};
}}

/* Frames */
QFrame {{
    background-color: {surface};
    border-radius: {border_radius}px;
}}

QFrame.header {{
    background-color: {primary};
    color: white;
    padding: {spacing}px;
}}

/* Tabs */
QTabWidget::pane {{
    border: 2px solid {border};
    border-radius: {border_radius}px;
    background: {bg};
}}

QTabBar::tab {{
    background: {surface};
    color: {text};
    border: 2px solid {border};
    border-bottom: none;
    border-top-left-radius: {border_radius}px;
    border-top-right-radius: {border_radius}px;
    padding: {spacing}px {spacing*2}px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: {primary};
    color: white;
}}

QTabBar::tab:hover {{
    background: {self._adjust_color(surface, 1.1)};
}}

/* Sliders */
QSlider::groove:horizontal {{
    border: 1px solid {border};
    height: 6px;
    background: {surface};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {primary};
    border: 2px solid {primary};
    width: {spacing*2}px;
    margin: -6px 0;
    border-radius: {spacing}px;
}}

QSlider::handle:horizontal:hover {{
    background: {self._adjust_color(primary, 1.1)};
}}

/* Combo Boxes */
QComboBox {{
    background-color: {surface};
    color: {text};
    border: 2px solid {border};
    border-radius: {border_radius}px;
    padding: {spacing}px;
}}

QComboBox:focus {{
    border-color: {primary};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {surface};
    color: {text};
    selection-background-color: {primary};
}}

/* Checkboxes */
QCheckBox {{
    color: {text};
    spacing: {spacing}px;
}}

QCheckBox::indicator {{
    width: {spacing*2}px;
    height: {spacing*2}px;
    border: 2px solid {border};
    border-radius: {border_radius//2}px;
    background: {surface};
}}

QCheckBox::indicator:checked {{
    background: {primary};
    border-color: {primary};
}}

/* Radio Buttons */
QRadioButton {{
    color: {text};
    spacing: {spacing}px;
}}

QRadioButton::indicator {{
    width: {spacing*2}px;
    height: {spacing*2}px;
    border: 2px solid {border};
    border-radius: {spacing}px;
    background: {surface};
}}

QRadioButton::indicator:checked {{
    background: {primary};
    border-color: {primary};
}}

/* Spin Boxes */
QSpinBox, QDoubleSpinBox {{
    background-color: {surface};
    color: {text};
    border: 2px solid {border};
    border-radius: {border_radius}px;
    padding: {spacing}px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {primary};
}}

/* Group Boxes */
QGroupBox {{
    border: 2px solid {border};
    border-radius: {border_radius}px;
    margin-top: {spacing*2}px;
    font-weight: bold;
    color: {text};
    padding: {spacing}px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: {primary};
}}

/* Scroll Bars */
QScrollBar:vertical {{
    background: {surface};
    width: {spacing*2}px;
    border-radius: {spacing}px;
}}

QScrollBar::handle:vertical {{
    background: {border};
    border-radius: {spacing}px;
}}

QScrollBar::handle:vertical:hover {{
    background: {text_secondary};
}}

QScrollBar:horizontal {{
    background: {surface};
    height: {spacing*2}px;
    border-radius: {spacing}px;
}}

QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: {spacing}px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {text_secondary};
}}

/* Tool Tips */
QToolTip {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    padding: {spacing//2}px;
}}

/* List Widgets */
QListWidget {{
    background-color: {surface};
    color: {text};
    border: 2px solid {border};
    border-radius: {border_radius}px;
}}

QListWidget::item {{
    padding: {spacing}px;
}}

QListWidget::item:selected {{
    background-color: {primary};
    color: white;
}}

QListWidget::item:hover {{
    background-color: {self._adjust_color(surface, 1.1)};
}}

/* Table Widgets */
QTableWidget {{
    background-color: {surface};
    color: {text};
    border: 2px solid {border};
    border-radius: {border_radius}px;
    gridline-color: {border};
}}

QTableWidget::item {{
    padding: {spacing}px;
}}

QTableWidget::item:selected {{
    background-color: {primary};
    color: white;
}}

QHeaderView::section {{
    background-color: {self._adjust_color(surface, 1.1)};
    color: {text};
    padding: {spacing}px;
    border: 1px solid {border};
    font-weight: bold;
}}
"""
        return stylesheet

    def _adjust_color(self, hex_color: str, factor: float) -> str:
        """
        Adjust color brightness

        Args:
            hex_color: Color in hex format (#RRGGBB)
            factor: Brightness factor (>1 = lighter, <1 = darker)

        Returns:
            Adjusted color in hex format
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')

            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Adjust
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))

            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def save_to_dict(self) -> dict:
        """Save theme and overlay appearance to dictionary"""
        return {
            'theme': self.current_theme.to_dict(),
            'overlay_appearance': self.overlay_appearance.to_dict()
        }

    def load_from_dict(self, data: dict):
        """Load theme and overlay appearance from dictionary"""
        if 'theme' in data:
            self.current_theme = Theme.from_dict(data['theme'])
        if 'overlay_appearance' in data:
            self.overlay_appearance = OverlayAppearance.from_dict(data['overlay_appearance'])


# Default themes
DEFAULT_DARK_THEME = Theme(
    mode=ThemeMode.DARK.value,
    primary_color="#14b8a6",
    secondary_color="#f59e0b",
    background_color="#1e1e1e",
    surface_color="#2d2d2d",
    text_color="#ffffff",
    text_secondary_color="#9ca3af"
)

DEFAULT_LIGHT_THEME = Theme(
    mode=ThemeMode.LIGHT.value,
    primary_color="#14b8a6",
    secondary_color="#f59e0b",
    background_color="#ffffff",
    surface_color="#f3f4f6",
    text_color="#1f2937",
    text_secondary_color="#6b7280"
)
