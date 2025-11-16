"""
Omnix Theme Bridge
==================

Bridges the new Omnix UI Design System with the existing theme_manager.py
to ensure backward compatibility and smooth migration.

⚠️ TECHNICAL DEBT WARNING ⚠️
=============================
This bridge exists because Omnix currently has TWO theme systems:

1. **Legacy System** (src/theme_manager.py):
   - Uses Theme dataclass with basic color/font settings
   - Modified through Appearance Settings UI (src/appearance_tabs.py)
   - Saved to ~/.gaming_ai_assistant/theme.json

2. **New Design System** (src/ui/design_system.py, src/ui/tokens.py):
   - Modern token-based design system
   - Used by all new UI components in src/ui/components/
   - Generates comprehensive QSS stylesheets

CURRENT ISSUES:
- Users changing settings in Appearance tab may not see full effects on new components
- Two sources of truth for styling creates confusion
- Settings don't fully propagate between systems

RECOMMENDED REFACTORING:
1. Migrate src/appearance_tabs.py to directly modify src/ui/tokens.py
2. Deprecate legacy Theme system in favor of OmnixDesignTokens
3. Update all components to use the new design system exclusively
4. Remove this bridge once migration is complete

Until then, this bridge provides backward compatibility.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.theme_manager import Theme, ThemeMode, UIScale, LayoutMode
from .tokens import OmnixDesignTokens, COLORS, TYPOGRAPHY, SPACING
from .design_system import OmnixDesignSystem


class OmnixThemeBridge:
    """
    Bridge between old Theme system and new OmnixDesignSystem.

    Provides backward compatibility while enabling the new design system.
    """

    def __init__(self, legacy_theme: Theme = None):
        """
        Initialize theme bridge.

        Args:
            legacy_theme: Existing Theme object (optional)
        """
        self.legacy_theme = legacy_theme or Theme()
        self.design_system = OmnixDesignSystem()
        self.tokens = OmnixDesignTokens()

    def convert_legacy_to_omnix(self) -> Theme:
        """
        Convert legacy theme to use Omnix design system colors.

        Updates the legacy theme to use the new Omnix color palette
        while maintaining the same structure.

        Returns:
            Updated Theme object with Omnix colors
        """
        # Update colors to match Omnix design system
        self.legacy_theme.primary_color = COLORS.accent_primary
        self.legacy_theme.secondary_color = COLORS.accent_secondary
        self.legacy_theme.background_color = COLORS.bg_primary
        self.legacy_theme.surface_color = COLORS.bg_secondary
        self.legacy_theme.text_color = COLORS.text_primary
        self.legacy_theme.text_secondary_color = COLORS.text_secondary

        # Update status colors
        self.legacy_theme.error_color = COLORS.error
        self.legacy_theme.success_color = COLORS.success
        self.legacy_theme.warning_color = COLORS.warning

        # Update typography
        self.legacy_theme.font_family = TYPOGRAPHY.font_primary
        self.legacy_theme.font_size = TYPOGRAPHY.size_base

        # Update spacing and border radius
        self.legacy_theme.spacing = SPACING.md
        self.legacy_theme.border_radius = 8  # Matches RADIUS.md

        return self.legacy_theme

    def get_omnix_stylesheet(self) -> str:
        """
        Get the complete Omnix stylesheet.

        Returns:
            Complete QSS stylesheet string
        """
        return self.design_system.generate_complete_stylesheet()

    def get_overlay_stylesheet(self, opacity: float = None) -> str:
        """
        Get overlay-specific stylesheet.

        Args:
            opacity: Overlay opacity (uses legacy theme value if not provided)

        Returns:
            Overlay QSS stylesheet string
        """
        if opacity is None:
            # Try to get from legacy theme's overlay appearance if available
            opacity = 0.75  # Default

        return self.design_system.generate_overlay_stylesheet(opacity)

    def apply_to_application(self, app):
        """
        Apply Omnix design system to PyQt application.

        Args:
            app: QApplication instance
        """
        stylesheet = self.get_omnix_stylesheet()
        app.setStyleSheet(stylesheet)

    def update_legacy_theme_from_omnix(self, omnix_theme: OmnixDesignTokens):
        """
        Update legacy theme from Omnix design tokens.

        This allows customization of the Omnix design tokens to flow back
        to the legacy theme system.

        Args:
            omnix_theme: OmnixDesignTokens instance
        """
        self.tokens = omnix_theme

        # Update legacy theme colors
        self.legacy_theme.primary_color = omnix_theme.colors.accent_primary
        self.legacy_theme.secondary_color = omnix_theme.colors.accent_secondary
        self.legacy_theme.background_color = omnix_theme.colors.bg_primary
        self.legacy_theme.surface_color = omnix_theme.colors.bg_secondary
        self.legacy_theme.text_color = omnix_theme.colors.text_primary
        self.legacy_theme.text_secondary_color = omnix_theme.colors.text_secondary

        return self.legacy_theme

    @staticmethod
    def create_omnix_theme() -> Theme:
        """
        Create a new Theme instance with Omnix design system values.

        Returns:
            Theme configured with Omnix design system
        """
        theme = Theme()

        # Apply Omnix colors
        theme.primary_color = COLORS.accent_primary
        theme.secondary_color = COLORS.accent_secondary
        theme.background_color = COLORS.bg_primary
        theme.surface_color = COLORS.bg_secondary
        theme.text_color = COLORS.text_primary
        theme.text_secondary_color = COLORS.text_secondary

        # Status colors
        theme.error_color = COLORS.error
        theme.success_color = COLORS.success
        theme.warning_color = COLORS.warning

        # Typography
        theme.font_family = TYPOGRAPHY.font_primary
        theme.font_size = TYPOGRAPHY.size_base

        # Layout
        theme.spacing = SPACING.md
        theme.border_radius = 8

        # Dark mode by default
        theme.mode = ThemeMode.DARK.value

        return theme


def migrate_to_omnix_design_system():
    """
    Helper function to migrate existing Omnix installation to new design system.

    This function:
    1. Creates a bridge instance
    2. Converts the default theme to Omnix design system
    3. Returns both the bridge and updated theme

    Returns:
        Tuple of (OmnixThemeBridge, Theme)
    """
    bridge = OmnixThemeBridge()
    omnix_theme = bridge.convert_legacy_to_omnix()

    return bridge, omnix_theme


# Convenience function for quick stylesheet generation
def get_omnix_stylesheet() -> str:
    """
    Quick access to Omnix stylesheet.

    Returns:
        Complete Omnix QSS stylesheet
    """
    design_system = OmnixDesignSystem()
    return design_system.generate_complete_stylesheet()


def get_omnix_overlay_stylesheet(opacity: float = 0.75) -> str:
    """
    Quick access to Omnix overlay stylesheet.

    Args:
        opacity: Overlay background opacity (0.0 to 1.0)

    Returns:
        Omnix overlay QSS stylesheet
    """
    design_system = OmnixDesignSystem()
    return design_system.generate_overlay_stylesheet(opacity)
