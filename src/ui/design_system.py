"""
Omnix Design System
===================

Central design system manager that generates QSS stylesheets and provides
component styling utilities based on the Omnix design tokens.
"""

from typing import Dict, Optional

try:
    from .tokens import tokens, COLORS, TYPOGRAPHY, SPACING, RADIUS, SHADOWS
except ImportError:  # Allow importing as top-level `design_system`
    from tokens import tokens, COLORS, TYPOGRAPHY, SPACING, RADIUS, SHADOWS


class OmnixDesignSystem:
    """
    Central design system for Omnix UI.

    Generates QSS stylesheets for PyQt6 components based on design tokens.
    Ensures consistency across all UI elements.
    """

    def __init__(self, custom_tokens=None):
        """
        Initialize design system.

        Args:
            custom_tokens: Optional OmnixDesignTokens instance to use instead of global tokens
        """
        self.tokens = custom_tokens if custom_tokens is not None else tokens

    def generate_base_stylesheet(self) -> str:
        """
        Generate the base stylesheet for the entire application.

        This includes global styles for common Qt widgets.
        """
        return f"""
/* ========================================
   OMNIX UI DESIGN SYSTEM - FUTURISTIC BASE STYLES
   ======================================== */

/* Global Application Styling */
QWidget {{
    background-color: {self.tokens.colors.bg_primary};
    color: {self.tokens.colors.text_primary};
    font-family: {self.tokens.typography.font_primary};
    font-size: {self.tokens.typography.size_base}pt;
    selection-background-color: {self.tokens.colors.accent_primary};
    selection-color: #000000;
    outline: none;
}}

/* Main Window */
QMainWindow {{
    background-color: {self.tokens.colors.bg_primary};
}}

/* Panels and Containers - Glass Effect */
QFrame {{
    background-color: {self.tokens.colors.bg_secondary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.md}px;
}}

/* Scrollbars - Slim & Minimal */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {self.tokens.colors.border_default};
    min-height: 30px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: {self.tokens.colors.accent_primary};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {self.tokens.colors.border_default};
    min-width: 30px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {self.tokens.colors.accent_primary};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* Menu Bar */
QMenuBar {{
    background-color: {self.tokens.colors.bg_primary_alt};
    color: {self.tokens.colors.text_primary};
    border-bottom: 1px solid {self.tokens.colors.border_default};
    padding: 4px 8px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    border-radius: {self.tokens.radius.sm}px;
}}

QMenuBar::item:selected {{
    background-color: {self.tokens.colors.accent_primary};
    color: #000000;
}}

QMenuBar::item:pressed {{
    background-color: {self.tokens.colors.accent_primary_dark};
}}

/* Menu Dropdown */
QMenu {{
    background-color: {self.tokens.colors.bg_primary_alt};
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.accent_primary};
    border-radius: {self.tokens.radius.md}px;
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 20px;
    border-radius: {self.tokens.radius.sm}px;
}}

QMenu::item:selected {{
    background-color: {self.tokens.colors.accent_primary};
    color: #000000;
}}

QMenu::separator {{
    height: 1px;
    background-color: {self.tokens.colors.border_default};
    margin: 4px 8px;
}}

/* Status Bar */
QStatusBar {{
    background-color: {self.tokens.colors.bg_primary_alt};
    color: {self.tokens.colors.text_secondary};
    border-top: 1px solid {self.tokens.colors.border_default};
    font-size: {self.tokens.typography.size_sm}pt;
}}

/* Tool Tips */
QToolTip {{
    background-color: {self.tokens.colors.bg_secondary_alt};
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.accent_primary};
    border-radius: {self.tokens.radius.base}px;
    padding: 8px 12px;
    font-size: {self.tokens.typography.size_sm}pt;
}}
"""

    def generate_button_stylesheet(self) -> str:
        """Generate stylesheet for button components."""
        return f"""
/* ========================================
   BUTTONS - NEON & GRADIENT STYLES
   ======================================== */

/* Primary Button */
QPushButton {{
    background-color: #2600F0FF;
    color: {self.tokens.colors.accent_primary};
    border: 1px solid {self.tokens.colors.accent_primary};
    border-radius: {self.tokens.radius.base}px;
    padding: {self.tokens.spacing.padding_button};
    font-weight: {self.tokens.typography.weight_bold};
    font-size: {self.tokens.typography.size_md}pt;
    text-transform: uppercase;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {self.tokens.colors.accent_primary};
    color: #000000;
    border: 1px solid {self.tokens.colors.accent_primary_bright};
}}

QPushButton:pressed {{
    background-color: {self.tokens.colors.accent_primary_dark};
    border-color: {self.tokens.colors.accent_primary_dark};
    color: white;
}}

QPushButton:disabled {{
    background-color: #0DFFFFFF;
    border: 1px solid {self.tokens.colors.text_disabled};
    color: {self.tokens.colors.text_disabled};
}}

/* Secondary Button (Ghost) */
QPushButton[buttonStyle="secondary"] {{
    background-color: transparent;
    border: 1px solid {self.tokens.colors.text_muted};
    color: {self.tokens.colors.text_secondary};
}}

QPushButton[buttonStyle="secondary"]:hover {{
    border-color: {self.tokens.colors.text_primary};
    color: {self.tokens.colors.text_primary};
    background-color: #0DFFFFFF;
}}

/* Danger Button */
QPushButton[buttonStyle="danger"] {{
    color: {self.tokens.colors.error};
    border-color: {self.tokens.colors.error};
    background-color: #1AFF2A2A;
}}

QPushButton[buttonStyle="danger"]:hover {{
    background-color: {self.tokens.colors.error};
    color: white;
}}

/* Success Button */
QPushButton[buttonStyle="success"] {{
    background-color: #2600FF9D;
    color: {self.tokens.colors.success};
    border: 1px solid {self.tokens.colors.success};
}}

QPushButton[buttonStyle="success"]:hover {{
    background-color: {self.tokens.colors.success};
    color: #000000;
}}

/* Icon Button */
QPushButton[buttonStyle="icon"] {{
    background-color: transparent;
    border: none;
    border-radius: {self.tokens.radius.full}px;
    padding: {self.tokens.spacing.sm}px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
}}

QPushButton[buttonStyle="icon"]:hover {{
    background-color: #1AFFFFFF;
}}

/* Tool Button */
QToolButton {{
    background-color: transparent;
    color: {self.tokens.colors.text_primary};
    border: none;
    border-radius: {self.tokens.radius.sm}px;
    padding: 8px;
}}

QToolButton:hover {{
    background-color: #1AFFFFFF;
}}

QToolButton:pressed {{
    background-color: {self.tokens.colors.accent_primary};
    color: #000000;
}}

QToolButton:checked {{
    background-color: {self.tokens.colors.accent_primary};
    color: #000000;
}}
"""

    def generate_input_stylesheet(self) -> str:
        """Generate stylesheet for input components."""
        return f"""
/* ========================================
   INPUT FIELDS - HIGH CONTRAST TECH
   ======================================== */

/* Line Edit */
QLineEdit {{
    background-color: #4D000000;
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.base}px;
    padding: {self.tokens.spacing.padding_input};
    font-size: {self.tokens.typography.size_md}pt;
    selection-background-color: {self.tokens.colors.accent_primary};
    selection-color: black;
}}

QLineEdit:hover {{
    border-color: {self.tokens.colors.accent_primary};
}}

QLineEdit:focus {{
    border: 1px solid {self.tokens.colors.accent_primary_bright};
    background-color: #0D00F0FF;
}}

QLineEdit:disabled {{
    background-color: #33000000;
    color: {self.tokens.colors.text_disabled};
    border-color: {self.tokens.colors.border_subtle};
}}

/* Text Edit */
QTextEdit, QPlainTextEdit {{
    background-color: #4D000000;
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.base}px;
    padding: {self.tokens.spacing.md}px;
    font-size: {self.tokens.typography.size_md}pt;
    selection-background-color: {self.tokens.colors.accent_primary};
    selection-color: black;
}}

QTextEdit:hover, QPlainTextEdit:hover {{
    border-color: {self.tokens.colors.accent_primary};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {self.tokens.colors.accent_primary_bright};
    background-color: #0D00F0FF;
}}

/* Combo Box (Dropdown) */
QComboBox {{
    background-color: #4D000000;
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.base}px;
    padding: 8px 12px;
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {self.tokens.colors.accent_primary};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border: 2px solid {self.tokens.colors.accent_primary};
    border-top: none;
    border-right: none;
    width: 6px;
    height: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {self.tokens.colors.bg_primary_alt};
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.md}px;
    selection-background-color: {self.tokens.colors.accent_primary};
    selection-color: black;
    padding: 4px;
}}

/* Spin Box */
QSpinBox, QDoubleSpinBox {{
    background-color: #4D000000;
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.base}px;
    padding: 8px 12px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {self.tokens.colors.accent_primary_bright};
    background-color: #0D00F0FF;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background-color: #66000000;
    border: none;
    border-radius: {self.tokens.radius.sm}px;
    width: 20px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {self.tokens.colors.accent_primary};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: #66000000;
    border: none;
    border-radius: {self.tokens.radius.sm}px;
    width: 20px;
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {self.tokens.colors.accent_primary};
}}
"""

    def generate_checkbox_radio_stylesheet(self) -> str:
        """Generate stylesheet for checkboxes and radio buttons."""
        return f"""
/* ========================================
   CHECKBOXES & RADIO BUTTONS
   ======================================== */

/* Checkbox */
QCheckBox {{
    color: {self.tokens.colors.text_primary};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.sm}px;
    background-color: {self.tokens.colors.bg_secondary};
}}

QCheckBox::indicator:hover {{
    border-color: {self.tokens.colors.accent_primary};
}}

QCheckBox::indicator:checked {{
    background-color: {self.tokens.colors.accent_primary};
    border-color: {self.tokens.colors.accent_primary};
    image: none;  /* Would need actual checkmark icon */
}}

QCheckBox::indicator:checked:hover {{
    background-color: {self.tokens.colors.accent_primary_bright};
}}

QCheckBox::indicator:disabled {{
    background-color: {self.tokens.colors.bg_primary_alt};
    border-color: {self.tokens.colors.border_subtle};
}}

/* Radio Button */
QRadioButton {{
    color: {self.tokens.colors.text_primary};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {self.tokens.colors.border_default};
    border-radius: 10px;
    background-color: {self.tokens.colors.bg_secondary};
}}

QRadioButton::indicator:hover {{
    border-color: {self.tokens.colors.accent_primary};
}}

QRadioButton::indicator:checked {{
    background-color: {self.tokens.colors.accent_primary};
    border: 6px solid {self.tokens.colors.accent_primary};
}}

QRadioButton::indicator:checked:hover {{
    background-color: {self.tokens.colors.accent_primary_bright};
    border-color: {self.tokens.colors.accent_primary_bright};
}}
"""

    def generate_slider_progress_stylesheet(self) -> str:
        """Generate stylesheet for sliders and progress bars."""
        return f"""
/* ========================================
   SLIDERS & PROGRESS BARS
   ======================================== */

/* Slider */
QSlider::groove:horizontal {{
    background-color: {self.tokens.colors.bg_secondary_alt};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background-color: {self.tokens.colors.accent_primary};
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {self.tokens.colors.accent_primary_bright};
}}

QSlider::add-page:horizontal {{
    background-color: {self.tokens.colors.bg_secondary_alt};
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background-color: {self.tokens.colors.accent_primary};
    border-radius: 3px;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {self.tokens.colors.bg_secondary};
    border: 1px solid {self.tokens.colors.border_subtle};
    border-radius: {self.tokens.radius.base}px;
    text-align: center;
    color: {self.tokens.colors.text_primary};
    font-weight: {self.tokens.typography.weight_semibold};
    height: 24px;
}}

QProgressBar::chunk {{
    background-color: {self.tokens.colors.accent_primary};
    border-radius: {self.tokens.radius.sm}px;
}}
"""

    def generate_tab_stylesheet(self) -> str:
        """Generate stylesheet for tab widgets."""
        return f"""
/* ========================================
   TAB WIDGET
   ======================================== */

QTabWidget::pane {{
    background-color: {self.tokens.colors.bg_secondary};
    border: 1px solid {self.tokens.colors.border_subtle};
    border-radius: {self.tokens.radius.md}px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {self.tokens.colors.bg_primary_alt};
    color: {self.tokens.colors.text_secondary};
    border: 1px solid {self.tokens.colors.border_subtle};
    border-bottom: none;
    border-top-left-radius: {self.tokens.radius.md}px;
    border-top-right-radius: {self.tokens.radius.md}px;
    padding: 12px 24px;
    margin-right: 4px;
    font-weight: {self.tokens.typography.weight_medium};
}}

QTabBar::tab:hover {{
    background-color: {self.tokens.colors.bg_secondary};
    color: {self.tokens.colors.text_primary};
}}

QTabBar::tab:selected {{
    background-color: {self.tokens.colors.bg_secondary};
    color: {self.tokens.colors.accent_primary};
    border-bottom: 3px solid {self.tokens.colors.accent_primary};
    font-weight: {self.tokens.typography.weight_semibold};
}}

QTabBar::tab:!selected {{
    margin-top: 4px;
}}
"""

    def generate_list_tree_stylesheet(self) -> str:
        """Generate stylesheet for list and tree widgets."""
        return f"""
/* ========================================
   LIST & TREE WIDGETS
   ======================================== */

/* List Widget */
QListWidget {{
    background-color: {self.tokens.colors.bg_secondary};
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_subtle};
    border-radius: {self.tokens.radius.base}px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    color: {self.tokens.colors.text_primary};
    border: none;
    border-radius: {self.tokens.radius.sm}px;
    padding: 10px 12px;
    margin: 2px 0;
}}

QListWidget::item:hover {{
    background-color: {self.tokens.colors.bg_secondary_alt};
}}

QListWidget::item:selected {{
    background-color: {self.tokens.colors.accent_primary};
    color: {self.tokens.colors.text_primary};
}}

QListWidget::item:selected:hover {{
    background-color: {self.tokens.colors.accent_primary_bright};
}}

/* Tree Widget */
QTreeWidget {{
    background-color: {self.tokens.colors.bg_secondary};
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_subtle};
    border-radius: {self.tokens.radius.base}px;
    outline: none;
}}

QTreeWidget::item {{
    background-color: transparent;
    color: {self.tokens.colors.text_primary};
    padding: 8px 4px;
}}

QTreeWidget::item:hover {{
    background-color: {self.tokens.colors.bg_secondary_alt};
}}

QTreeWidget::item:selected {{
    background-color: {self.tokens.colors.accent_primary};
    color: {self.tokens.colors.text_primary};
}}

QTreeWidget::branch {{
    background-color: transparent;
}}
"""

    def generate_dialog_stylesheet(self) -> str:
        """Generate stylesheet for dialog windows."""
        return f"""
/* ========================================
   DIALOGS
   ======================================== */

QDialog {{
    background-color: {self.tokens.colors.bg_primary};
    color: {self.tokens.colors.text_primary};
}}

QDialogButtonBox {{
    button-layout: 0;  /* Windows layout */
}}

QDialogButtonBox QPushButton {{
    min-width: 100px;
}}

/* Group Box */
QGroupBox {{
    background-color: transparent;
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.md}px;
    margin-top: 12px;
    padding: 16px;
    font-weight: {self.tokens.typography.weight_semibold};
    color: {self.tokens.colors.text_primary};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: {self.tokens.colors.bg_primary};
    color: {self.tokens.colors.accent_primary};
}}
"""

    def generate_label_stylesheet(self) -> str:
        """Generate stylesheet for labels and text elements."""
        return f"""
/* ========================================
   LABELS & TEXT
   ======================================== */

QLabel {{
    color: {self.tokens.colors.text_primary};
    background-color: transparent;
}}

QLabel[labelStyle="heading"] {{
    font-size: {self.tokens.typography.size_2xl}pt;
    font-weight: {self.tokens.typography.weight_bold};
    color: {self.tokens.colors.text_primary};
}}

QLabel[labelStyle="subheading"] {{
    font-size: {self.tokens.typography.size_xl}pt;
    font-weight: {self.tokens.typography.weight_semibold};
    color: {self.tokens.colors.text_primary};
}}

QLabel[labelStyle="caption"] {{
    font-size: {self.tokens.typography.size_sm}pt;
    color: {self.tokens.colors.text_muted};
}}

QLabel[labelStyle="monospace"] {{
    font-family: {self.tokens.typography.font_monospace};
    color: {self.tokens.colors.accent_primary};
}}

QLabel[labelStyle="accent"] {{
    color: {self.tokens.colors.accent_primary};
    font-weight: {self.tokens.typography.weight_semibold};
}}

QLabel[labelStyle="success"] {{
    color: {self.tokens.colors.success};
}}

QLabel[labelStyle="warning"] {{
    color: {self.tokens.colors.warning};
}}

QLabel[labelStyle="error"] {{
    color: {self.tokens.colors.error};
}}
"""

    def generate_complete_stylesheet(self) -> str:
        """
        Generate the complete stylesheet for the entire application.

        Returns:
            Complete QSS stylesheet string
        """
        sections = [
            self.generate_base_stylesheet(),
            self.generate_button_stylesheet(),
            self.generate_input_stylesheet(),
            self.generate_checkbox_radio_stylesheet(),
            self.generate_slider_progress_stylesheet(),
            self.generate_tab_stylesheet(),
            self.generate_list_tree_stylesheet(),
            self.generate_dialog_stylesheet(),
            self.generate_label_stylesheet(),
        ]

        return "\n\n".join(sections)

    def generate_overlay_stylesheet(self, opacity: float = 0.75) -> str:
        """
        Generate stylesheet specifically for the in-game overlay.

        Args:
            opacity: Background opacity (0.0 to 1.0)

        Returns:
            QSS stylesheet for overlay window
        """
        # Deep space background with specified opacity
        # Convert opacity (0-1) to hex alpha (00-FF)
        alpha_hex = format(int(opacity * 255), '02x')
        bg_color = f"#{alpha_hex}0A0C14"

        return f"""
/* ========================================
   IN-GAME OVERLAY STYLES - FUTURISTIC HUD
   ======================================== */

QWidget {{
    background-color: transparent;
    color: {self.tokens.colors.text_primary};
    font-family: {self.tokens.typography.font_primary};
    font-size: {self.tokens.typography.size_base}pt;
}}

/* Main container gets frosted glass background */
QFrame {{
    background-color: {bg_color};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.lg}px;
}}

/* Minimize overlay chrome */
QPushButton {{
    background-color: #2600F0FF;
    color: {self.tokens.colors.accent_primary};
    border: 1px solid {self.tokens.colors.accent_primary};
    border-radius: {self.tokens.radius.sm}px;
    padding: 6px 12px;
    font-size: {self.tokens.typography.size_sm}pt;
    font-weight: {self.tokens.typography.weight_bold};
}}

QPushButton:hover {{
    background-color: {self.tokens.colors.accent_primary};
    color: #000000;
}}

/* Chat Display - slightly different background */
QTextEdit {{
    background-color: #66000000;
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_subtle};
    border-radius: {self.tokens.radius.base}px;
    font-size: {self.tokens.typography.size_sm}pt;
}}

/* Input Field */
QLineEdit {{
    background-color: #4D000000;
    color: {self.tokens.colors.text_primary};
    border: 1px solid {self.tokens.colors.border_default};
    border-radius: {self.tokens.radius.sm}px;
    padding: 8px;
    font-size: {self.tokens.typography.size_sm}pt;
    selection-background-color: {self.tokens.colors.accent_primary};
    selection-color: black;
}}

QLineEdit:hover {{
    border-color: {self.tokens.colors.accent_primary};
}}

QLineEdit:focus {{
    border: 1px solid {self.tokens.colors.accent_primary_bright};
    background-color: #0D00F0FF;
}}

/* Minimal Scrollbars for Overlay */
QScrollBar:vertical {{
    background: transparent;
    width: 4px;
}}

QScrollBar::handle:vertical {{
    background: {self.tokens.colors.accent_primary};
    border-radius: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: {self.tokens.colors.accent_primary_bright};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}
"""


# Singleton instance
design_system = OmnixDesignSystem()
