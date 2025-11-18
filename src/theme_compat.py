"""
Theme Compatibility Layer
=========================

Provides backward compatibility wrapper for code still using the legacy ThemeManager.
This allows gradual migration without breaking existing functionality.

This wrapper makes OmnixThemeManager compatible with legacy ThemeManager API.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from ui.theme_manager import OmnixThemeManager, get_theme_manager

logger = logging.getLogger(__name__)


@dataclass
class LegacyTheme:
    """
    Legacy Theme dataclass for backward compatibility.
    Maps to OmnixDesignTokens under the hood.
    """
    # Theme mode (not used in new system, kept for compatibility)
    mode: str = "dark"

    # Colors (mapped to tokens)
    primary_color: str = "#00BFFF"
    secondary_color: str = "#39FF14"
    background_color: str = "#1A1A2E"
    surface_color: str = "#2C2C4A"
    text_color: str = "#FFFFFF"
    text_secondary_color: str = "#E0E0E0"

    # Status colors
    error_color: str = "#FF3B3B"
    success_color: str = "#39FF14"
    warning_color: str = "#FFB800"

    # Typography (mapped to tokens)
    font_family: str = "Roboto, Arial, sans-serif"
    font_size: int = 11

    # UI scale (not used in new system)
    ui_scale: str = "normal"

    # Layout (mapped to spacing tokens)
    layout_mode: str = "comfortable"
    border_radius: int = 8
    spacing: int = 16
    transparency: float = 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'LegacyTheme':
        """Create LegacyTheme from dictionary."""
        return LegacyTheme(**data)


@dataclass
class LegacyOverlayAppearance:
    """Legacy OverlayAppearance for backward compatibility."""
    position_preset: str = "top_right"
    custom_x: int = 100
    custom_y: int = 100
    width: int = 900
    height: int = 700
    opacity: float = 0.95
    scale: float = 1.0
    show_header: bool = True
    show_minimize_button: bool = True
    edge_snapping: bool = True
    snap_threshold: int = 20
    stay_on_top: bool = True
    minimize_to_tray: bool = False
    show_chat: bool = True
    show_game_info: bool = True
    show_tips_panel: bool = False
    show_stats_panel: bool = False

    def get_position_preset_coords(self, screen_width: int, screen_height: int) -> tuple:
        """
        Get coordinates for position preset.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            Tuple of (x, y) coordinates
        """
        margin = 20  # Margin from edges

        preset_map = {
            "top_left": (margin, margin),
            "top_right": (screen_width - self.width - margin, margin),
            "bottom_left": (margin, screen_height - self.height - margin),
            "bottom_right": (
                screen_width - self.width - margin,
                screen_height - self.height - margin
            ),
            "center": (
                (screen_width - self.width) // 2,
                (screen_height - self.height) // 2
            ),
            "custom": (self.custom_x, self.custom_y),
        }

        return preset_map.get(self.position_preset, (self.custom_x, self.custom_y))

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'LegacyOverlayAppearance':
        return LegacyOverlayAppearance(**data)


class ThemeManagerCompat:
    """
    Compatibility wrapper that makes OmnixThemeManager compatible with legacy code.

    This wrapper:
    - Provides the same API as legacy ThemeManager
    - Translates between legacy Theme objects and OmnixDesignTokens
    - Allows gradual migration without breaking existing code
    """

    def __init__(self):
        """Initialize compatibility wrapper."""
        self.omnix_manager = get_theme_manager()
        self.current_theme = self._tokens_to_legacy_theme()
        self.overlay_appearance = LegacyOverlayAppearance()

        logger.info("ThemeManagerCompat initialized with OmnixThemeManager backend")

    def _tokens_to_legacy_theme(self) -> LegacyTheme:
        """
        Convert current OmnixDesignTokens to legacy Theme format.

        Returns:
            LegacyTheme object
        """
        tokens = self.omnix_manager.tokens

        return LegacyTheme(
            mode="dark",  # Always dark in new system
            primary_color=tokens.colors.accent_primary,
            secondary_color=tokens.colors.accent_secondary,
            background_color=tokens.colors.bg_primary,
            surface_color=tokens.colors.bg_secondary,
            text_color=tokens.colors.text_primary,
            text_secondary_color=tokens.colors.text_secondary,
            error_color=tokens.colors.error,
            success_color=tokens.colors.success,
            warning_color=tokens.colors.warning,
            font_family=tokens.typography.font_primary,
            font_size=tokens.typography.size_base,
            ui_scale="normal",
            layout_mode="comfortable",
            border_radius=tokens.radius.base,
            spacing=tokens.spacing.base,
            transparency=1.0
        )

    def _legacy_theme_to_tokens(self, theme: LegacyTheme):
        """
        Update OmnixDesignTokens from legacy Theme.

        Args:
            theme: LegacyTheme object
        """
        # Update color tokens
        self.omnix_manager.update_color('accent_primary', theme.primary_color)
        self.omnix_manager.update_color('accent_secondary', theme.secondary_color)
        self.omnix_manager.update_color('bg_primary', theme.background_color)
        self.omnix_manager.update_color('bg_secondary', theme.surface_color)
        self.omnix_manager.update_color('text_primary', theme.text_color)
        self.omnix_manager.update_color('text_secondary', theme.text_secondary_color)
        self.omnix_manager.update_color('error', theme.error_color)
        self.omnix_manager.update_color('success', theme.success_color)
        self.omnix_manager.update_color('warning', theme.warning_color)

        # Update typography tokens
        self.omnix_manager.update_typography('font_primary', theme.font_family)
        self.omnix_manager.update_typography('size_base', theme.font_size)

        # Update layout tokens
        self.omnix_manager.update_radius('base', theme.border_radius)
        self.omnix_manager.update_spacing('base', theme.spacing)

    def set_theme(self, theme: LegacyTheme):
        """
        Set current theme (legacy API).

        Args:
            theme: LegacyTheme object
        """
        self.current_theme = theme
        self._legacy_theme_to_tokens(theme)
        logger.info("Theme updated via compatibility layer")

    def set_overlay_appearance(self, appearance: LegacyOverlayAppearance):
        """
        Set overlay appearance (legacy API).

        Args:
            appearance: LegacyOverlayAppearance object
        """
        self.overlay_appearance = appearance
        logger.info("Overlay appearance updated via compatibility layer")

    def generate_stylesheet(self, for_overlay: bool = False) -> str:
        """
        Generate PyQt6 stylesheet (legacy API).

        Args:
            for_overlay: If True, generate for overlay window

        Returns:
            QSS stylesheet string
        """
        if for_overlay:
            opacity = getattr(self.overlay_appearance, 'opacity', 0.95)
            return self.omnix_manager.get_overlay_stylesheet(opacity)
        else:
            return self.omnix_manager.get_stylesheet()

    def save_to_dict(self) -> dict:
        """
        Save theme and overlay appearance to dictionary (legacy API).

        Returns:
            Dictionary with theme and overlay_appearance keys
        """
        return {
            'theme': self.current_theme.to_dict(),
            'overlay_appearance': self.overlay_appearance.to_dict()
        }

    def load_from_dict(self, data: dict):
        """
        Load theme and overlay appearance from dictionary (legacy API).

        Args:
            data: Dictionary with theme and/or overlay_appearance keys
        """
        if 'theme' in data:
            self.current_theme = LegacyTheme.from_dict(data['theme'])
            self._legacy_theme_to_tokens(self.current_theme)

        if 'overlay_appearance' in data:
            self.overlay_appearance = LegacyOverlayAppearance.from_dict(data['overlay_appearance'])

        logger.info("Theme loaded from dictionary via compatibility layer")


# Default themes for compatibility
DEFAULT_DARK_THEME = LegacyTheme(
    mode="dark",
    primary_color="#00BFFF",
    secondary_color="#39FF14",
    background_color="#1A1A2E",
    surface_color="#2C2C4A",
    text_color="#FFFFFF",
    text_secondary_color="#E0E0E0"
)

DEFAULT_LIGHT_THEME = LegacyTheme(
    mode="light",
    primary_color="#00BFFF",
    secondary_color="#39FF14",
    background_color="#FFFFFF",
    surface_color="#F3F4F6",
    text_color="#1F2937",
    text_secondary_color="#6B7280"
)


# Alias for backward compatibility
ThemeManager = ThemeManagerCompat
