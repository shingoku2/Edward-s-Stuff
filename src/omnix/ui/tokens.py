"""
Omnix UI Design Tokens
======================

Design tokens define the visual foundation of the Omnix UI design system.
Restrained dark desktop palette with a single cool accent and accessible contrast.
"""

from dataclasses import dataclass
from typing import Dict, Literal


@dataclass
class ColorPalette:
    """Color palette for the Omnix desktop interface."""

    # Primary Backgrounds - Deep Space / Void
    bg_primary: str = "#0B0F14"
    bg_primary_alt: str = "#111820"

    # Secondary Backgrounds - Glass/Holographic panels
    # Using hex with alpha channel for Qt compatibility (#RRGGBBAA)
    bg_secondary: str = "#17212BCC"
    bg_secondary_alt: str = "#1D2935F2"

    # Accent Colors - Neon / Laser
    accent_primary: str = "#5CC8BE"
    accent_primary_bright: str = "#A7E6DF"
    accent_primary_dark: str = "#2F8F87"

    accent_secondary: str = "#7CA7D8"
    accent_tertiary: str = "#9B8AC4"

    # Text Colors
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#B7C1CC"
    text_muted: str = "#7D8A98"
    text_disabled: str = "#56616D"

    # Status Colors - Neon variants
    success: str = "#66C28A"
    warning: str = "#E0B86B"
    error: str = "#E27676"
    info: str = "#7CA7D8"

    # Border Colors
    border_subtle: str = "#ffffff1a"  # rgba(255, 255, 255, 0.1)
    border_default: str = "#64788A66"
    border_accent: str = "#5CC8BE"

    # Overlay Colors
    overlay_dark: str = "#0B0F14e6"
    overlay_medium: str = "#0B0F14cc"
    overlay_light: str = "#0B0F1499"

    # Interactive States
    hover_overlay: str = "#00f0ff1a"  # rgba(0, 240, 255, 0.1) - Cyan tint
    active_overlay: str = "#00f0ff33"  # rgba(0, 240, 255, 0.2) - Stronger cyan tint
    focus_outline: str = "#A7E6DF"

    # Gradients
    gradient_primary: str = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5CC8BE, stop:1 #7CA7D8)"
    )
    gradient_surface: str = (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e2332e6, stop:1 #141928f2)"
    )
    gradient_dark: str = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #111820, stop:1 #0B0F14)"
    gradient_panel: str = (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e2332cc, stop:1 #14192899)"
    )


@dataclass
class Typography:
    """Typography system for Omnix UI."""

    # Font Families - Prefer modern/geometric fonts
    font_primary: str = "'Segoe UI', 'Roboto', 'Montserrat', sans-serif"
    font_monospace: str = "'JetBrains Mono', 'Fira Code', monospace"

    # Font Sizes (in pt)
    size_xs: int = 9
    size_sm: int = 10
    size_base: int = 11
    size_md: int = 12
    size_lg: int = 14
    size_xl: int = 18  # Increased for headings
    size_2xl: int = 24
    size_3xl: int = 32
    size_4xl: int = 48

    # Font Weights
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 800  # Extra bold for futuristic headers

    # Line Heights (relative to font size)
    line_height_tight: float = 1.2
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75

    # Letter Spacing (in em)
    letter_spacing_tight: str = "-0.02em"
    letter_spacing_normal: str = "0em"
    letter_spacing_wide: str = "0.05em"


@dataclass
class Spacing:
    """Spacing system for consistent layouts."""

    # Base spacing unit (in px)
    unit: int = 4

    # Spacing scale (multiples of base unit)
    xs: int = 4  # 1 unit
    sm: int = 8  # 2 units
    md: int = 16  # 4 units - More breathing room
    base: int = 20  # 5 units
    lg: int = 32  # 8 units
    xl: int = 48  # 12 units
    xl2: int = 64  # 16 units
    xl3: int = 96  # 24 units

    # Common padding values
    padding_button: str = "10px 24px"
    padding_input: str = "12px 16px"
    padding_card: str = "24px"
    padding_panel: str = "32px"

    # Common margin values
    margin_sm: str = "8px"
    margin_md: str = "16px"
    margin_lg: str = "32px"


@dataclass
class BorderRadius:
    """Border radius values for components."""

    # Going for a slightly more angular/technical look
    none: int = 0
    sm: int = 2
    base: int = 4
    md: int = 6
    lg: int = 12
    xl: int = 16
    full: int = 9999  # Pill shape


@dataclass
class Shadows:
    """Shadow and Glow effects."""

    # Neon Glows
    sm: str = "0 0 5px rgba(0, 240, 255, 0.2)"
    base: str = "0 0 10px rgba(0, 240, 255, 0.3)"
    md: str = "0 0 15px rgba(0, 240, 255, 0.4)"
    lg: str = "0 0 25px rgba(0, 240, 255, 0.5)"

    # Error Glow
    error_glow: str = "0 0 10px rgba(255, 42, 42, 0.5)"

    # Legacy glow effects (updated colors)
    glow_blue_sm: str = "0 0 5px rgba(0, 240, 255, 0.3)"
    glow_blue_md: str = "0 0 10px rgba(0, 240, 255, 0.4)"
    glow_blue_lg: str = "0 0 15px rgba(0, 240, 255, 0.5)"

    glow_green_sm: str = "0 0 5px rgba(0, 255, 157, 0.3)"
    glow_green_md: str = "0 0 10px rgba(0, 255, 157, 0.4)"

    # Inner shadow for depth
    inner: str = "inset 0 2px 4px rgba(0, 0, 0, 0.3)"


@dataclass
class Animation:
    """Animation timing and easing functions."""

    # Duration (in ms)
    duration_fast: int = 150
    duration_base: int = 300
    duration_slow: int = 500

    # Easing functions (CSS-style)
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    ease_linear: str = "linear"
    ease_smooth: str = "cubic-bezier(0.25, 0.1, 0.25, 1)"


@dataclass
class ZIndex:
    """Z-index layering system."""

    base: int = 0
    dropdown: int = 100
    sticky: int = 200
    overlay: int = 300
    modal: int = 400
    popover: int = 500
    tooltip: int = 600
    notification: int = 700


class OmnixDesignTokens:
    """
    Central design tokens for the Omnix UI design system.

    This class provides access to all design tokens including colors,
    typography, spacing, shadows, and animations.

    Usage:
        tokens = OmnixDesignTokens()
        primary_bg = tokens.colors.bg_primary
        accent = tokens.colors.accent_primary
    """

    def __init__(self):
        self.colors = ColorPalette()
        self.typography = Typography()
        self.spacing = Spacing()
        self.radius = BorderRadius()
        self.shadows = Shadows()
        self.animation = Animation()
        self.z_index = ZIndex()

    def get_color_scheme(self) -> Dict[str, str]:
        """
        Get the complete color scheme as a dictionary.
        Useful for theming and bulk operations.
        """
        return {
            "bg_primary": self.colors.bg_primary,
            "bg_primary_alt": self.colors.bg_primary_alt,
            "bg_secondary": self.colors.bg_secondary,
            "bg_secondary_alt": self.colors.bg_secondary_alt,
            "accent_primary": self.colors.accent_primary,
            "accent_primary_bright": self.colors.accent_primary_bright,
            "accent_primary_dark": self.colors.accent_primary_dark,
            "accent_secondary": self.colors.accent_secondary,
            "accent_tertiary": self.colors.accent_tertiary,
            "text_primary": self.colors.text_primary,
            "text_secondary": self.colors.text_secondary,
            "text_muted": self.colors.text_muted,
            "success": self.colors.success,
            "warning": self.colors.warning,
            "error": self.colors.error,
            "info": self.colors.info,
        }

    def get_spacing_scale(self) -> Dict[str, int]:
        """Get the spacing scale as a dictionary."""
        return {
            "xs": self.spacing.xs,
            "sm": self.spacing.sm,
            "md": self.spacing.md,
            "base": self.spacing.base,
            "lg": self.spacing.lg,
            "xl": self.spacing.xl,
            "xl2": self.spacing.xl2,
            "xl3": self.spacing.xl3,
        }

    def get_font_sizes(self) -> Dict[str, int]:
        """Get the font size scale as a dictionary."""
        return {
            "xs": self.typography.size_xs,
            "sm": self.typography.size_sm,
            "base": self.typography.size_base,
            "md": self.typography.size_md,
            "lg": self.typography.size_lg,
            "xl": self.typography.size_xl,
            "2xl": self.typography.size_2xl,
            "3xl": self.typography.size_3xl,
            "4xl": self.typography.size_4xl,
        }


# Singleton instance for easy access
tokens = OmnixDesignTokens()


# Export commonly used values for convenience
COLORS = tokens.colors
TYPOGRAPHY = tokens.typography
SPACING = tokens.spacing
RADIUS = tokens.radius
SHADOWS = tokens.shadows
ANIMATION = tokens.animation
Z_INDEX = tokens.z_index
