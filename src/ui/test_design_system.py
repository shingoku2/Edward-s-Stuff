"""
Omnix UI Design System - Test Suite
====================================

Quick test to verify all components import correctly and basic functionality works.

Run with:
    python -m pytest src/ui/test_design_system.py
    or
    python -m src.ui.test_design_system
"""

import sys


def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")

    # Core modules (use relative imports)
    from . import tokens
    from . import design_system
    from .tokens import COLORS, TYPOGRAPHY, SPACING, RADIUS, SHADOWS, ANIMATION, Z_INDEX
    from .design_system import OmnixDesignSystem
    from .icons import OmnixIcons, icons

    # Components
    from .components import (
        OmnixButton,
        OmnixIconButton,
        OmnixLineEdit,
        OmnixTextEdit,
        OmnixComboBox,
        OmnixCard,
        OmnixPanel,
        OmnixInfoCard,
        OmnixVBox,
        OmnixHBox,
        OmnixGrid,
        OmnixFormLayout,
        OmnixSidebar,
        OmnixSidebarButton,
        OmnixHeaderBar,
        OmnixDialog,
        OmnixConfirmDialog,
        OmnixMessageDialog,
        OmnixInputDialog,
    )

    # Overlay components
    from .components.overlay import (
        OmnixOverlayPanel,
        OmnixOverlayChatWidget,
        OmnixOverlayTip,
        OmnixOverlayStatus,
    )

    print("✓ All imports successful (basic UI modules)")


def test_tokens():
    """Test design tokens."""
    print("\nTesting design tokens...")

    from .tokens import tokens, COLORS

    # Test color palette
    assert COLORS.bg_primary == "#1A1A2E"
    assert COLORS.accent_primary == "#00BFFF"
    assert COLORS.text_primary == "#FFFFFF"

    # Test token access
    color_scheme = tokens.get_color_scheme()
    assert "bg_primary" in color_scheme
    assert "accent_primary" in color_scheme

    font_sizes = tokens.get_font_sizes()
    assert "base" in font_sizes
    assert font_sizes["base"] == 11

    print("✓ Design tokens working correctly")


def test_stylesheet_generation():
    """Test stylesheet generation."""
    print("\nTesting stylesheet generation...")

    from .design_system import design_system

    # Generate complete stylesheet
    stylesheet = design_system.generate_complete_stylesheet()
    assert isinstance(stylesheet, str)
    assert len(stylesheet) > 0
    assert "QWidget" in stylesheet
    assert "#1A1A2E" in stylesheet  # bg_primary
    assert "#00BFFF" in stylesheet  # accent_primary

    # Generate overlay stylesheet
    overlay_style = design_system.generate_overlay_stylesheet(opacity=0.75)
    assert isinstance(overlay_style, str)
    assert "rgba" in overlay_style

    print("✓ Stylesheet generation working correctly")


def test_icons():
    """Test icon system."""
    import os
    print("\nTesting icon system...")

    from .icons import icons

    # Get available icons
    available = icons.available_icons()
    assert len(available) > 0
    assert "omnix_logo" in available
    assert "chat" in available
    assert "settings" in available

    # Get an icon (this will only fully work in PyQt6 environment)
    # Skip icon creation in CI or headless environments due to Qt threading issues
    if os.environ.get("CI") or os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        print("⚠ Skipping icon creation in headless/CI environment")
        return

    try:
        from PyQt6.QtGui import QIcon
        icon = icons.get_icon("chat", size=32)
        assert isinstance(icon, QIcon)
        print("✓ Icon system working correctly (PyQt6 available)")
    except (ImportError, RuntimeError) as e:
        print(f"⚠ Icon system imports work (full test skipped: {e})")


def test_theme_compatibility():
    """Test legacy compatibility wrapper."""
    print("\nTesting theme compatibility...")

    from src.theme_compat import ThemeManagerCompat, LegacyTheme

    compat = ThemeManagerCompat()
    assert compat.current_theme is not None

    # Update tokens via legacy theme
    legacy_theme = LegacyTheme(
        primary_color="#123456",
        secondary_color="#ABCDEF",
        font_size=14,
        spacing=20,
        border_radius=10,
    )
    compat.set_theme(legacy_theme)

    tokens = compat.omnix_manager.tokens
    assert tokens.colors.accent_primary == "#123456"
    assert tokens.colors.accent_secondary == "#ABCDEF"
    assert tokens.typography.size_base == 14
    assert tokens.spacing.base == 20
    assert tokens.radius.base == 10

    # Persistence roundtrip
    saved = compat.save_to_dict()
    compat.load_from_dict(saved)
    assert compat.current_theme.primary_color == "#123456"

    # Stylesheet generation still available
    stylesheet = compat.generate_stylesheet()
    assert isinstance(stylesheet, str)

    print("✓ Theme compatibility working correctly")


def test_component_creation():
    """Test component instantiation (without PyQt6 display)."""
    print("\nTesting component creation...")

    try:
        from PyQt6.QtWidgets import QApplication
        from .components import OmnixButton, OmnixCard, OmnixPanel

        # Create minimal app
        app = QApplication.instance() or QApplication([])

        # Create components
        button = OmnixButton("Test Button")
        assert button is not None
        assert button.text() == "Test Button"

        card = OmnixCard(title="Test Card")
        assert card is not None

        panel = OmnixPanel()
        assert panel is not None

        print("✓ Component creation working correctly")

    except ImportError:
        print("⚠ Component creation test skipped (PyQt6 not available)")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Omnix UI Design System - Test Suite")
    print("=" * 60)

    try:
        test_imports()
        test_tokens()
        test_stylesheet_generation()
        test_icons()
        test_theme_compatibility()
        test_component_creation()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
