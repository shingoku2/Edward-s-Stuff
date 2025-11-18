"""
Appearance Configuration Tabs (Refactored for New Design System)
Contains UI tabs for appearance customization using OmnixThemeManager
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QSlider, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QMessageBox, QColorDialog, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

# Import new design system
from ui.theme_manager import OmnixThemeManager

logger = logging.getLogger(__name__)


class AppAppearanceTab(QWidget):
    """Tab for configuring main app appearance using new design system"""

    theme_changed = pyqtSignal()  # Emits when theme changes

    def __init__(self, theme_manager: OmnixThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager

        # Register callback for theme updates
        self.theme_manager.add_update_callback(self.on_theme_updated)

        self.init_ui()

    def init_ui(self):
        """Initialize app appearance tab UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Main Application Appearance")
        header.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {self.theme_manager.tokens.colors.accent_primary}; padding: 10px;")
        layout.addWidget(header)

        # Colors Section
        colors_group = QGroupBox("Color Palette")
        colors_layout = QVBoxLayout()

        # Primary Accent Color
        self._add_color_picker(colors_layout, "Primary Accent", "accent_primary",
                               "Main accent color used for buttons, links, and highlights")

        # Secondary Accent Color
        self._add_color_picker(colors_layout, "Secondary Accent", "accent_secondary",
                               "Secondary accent color for warnings and special elements")

        # Background Colors
        self._add_color_picker(colors_layout, "Primary Background", "bg_primary",
                               "Main application background color")

        self._add_color_picker(colors_layout, "Secondary Background", "bg_secondary",
                               "Panel and container background color")

        # Text Colors
        self._add_color_picker(colors_layout, "Primary Text", "text_primary",
                               "Main text color")

        self._add_color_picker(colors_layout, "Secondary Text", "text_secondary",
                               "Secondary/muted text color")

        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)

        # Typography Section
        typography_group = QGroupBox("Typography")
        typography_layout = QVBoxLayout()

        # Font Family
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Font Family:")
        font_family_layout.addWidget(font_family_label)

        self.font_family_input = QLineEdit()
        self.font_family_input.setText(self.theme_manager.tokens.typography.font_primary)
        self.font_family_input.setPlaceholderText("e.g., Roboto, Arial, sans-serif")
        self.font_family_input.textChanged.connect(self.on_font_family_changed)
        font_family_layout.addWidget(self.font_family_input)

        typography_layout.addLayout(font_family_layout)

        # Base Font Size
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Base Font Size:")
        font_size_layout.addWidget(font_size_label)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(self.theme_manager.tokens.typography.size_base)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        font_size_layout.addWidget(self.font_size_spin)

        font_size_layout.addStretch()
        typography_layout.addLayout(font_size_layout)

        typography_group.setLayout(typography_layout)
        layout.addWidget(typography_group)

        # Spacing & Layout Section
        spacing_group = QGroupBox("Spacing & Layout")
        spacing_layout = QVBoxLayout()

        # Base Spacing
        base_spacing_layout = QHBoxLayout()
        base_spacing_label = QLabel("Base Spacing:")
        base_spacing_layout.addWidget(base_spacing_label)

        self.base_spacing_spin = QSpinBox()
        self.base_spacing_spin.setRange(8, 32)
        self.base_spacing_spin.setValue(self.theme_manager.tokens.spacing.base)
        self.base_spacing_spin.setSuffix(" px")
        self.base_spacing_spin.valueChanged.connect(self.on_base_spacing_changed)
        base_spacing_layout.addWidget(self.base_spacing_spin)

        base_spacing_layout.addStretch()
        spacing_layout.addLayout(base_spacing_layout)

        # Border Radius
        border_radius_layout = QHBoxLayout()
        border_radius_label = QLabel("Border Radius:")
        border_radius_layout.addWidget(border_radius_label)

        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 20)
        self.border_radius_spin.setValue(self.theme_manager.tokens.radius.base)
        self.border_radius_spin.setSuffix(" px")
        self.border_radius_spin.valueChanged.connect(self.on_border_radius_changed)
        border_radius_layout.addWidget(self.border_radius_spin)

        border_radius_layout.addStretch()
        spacing_layout.addLayout(border_radius_layout)

        spacing_group.setLayout(spacing_layout)
        layout.addWidget(spacing_group)

        # Action Buttons
        button_layout = QHBoxLayout()

        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(reset_button)

        preview_button = QPushButton("Apply Changes")
        preview_button.clicked.connect(self.apply_theme)
        button_layout.addWidget(preview_button)

        save_button = QPushButton("Save Theme")
        save_button.clicked.connect(self.save_theme)
        button_layout.addWidget(save_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Customization Info
        info_layout = QHBoxLayout()
        customizations_count = len(self.theme_manager._customized_tokens)
        info_label = QLabel(f"Customizations: {customizations_count} tokens modified")
        info_label.setStyleSheet(f"color: {self.theme_manager.tokens.colors.text_muted}; font-size: 10pt;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        layout.addStretch()
        self.setLayout(layout)

    def _add_color_picker(self, layout: QVBoxLayout, label: str, token_key: str, description: str):
        """
        Add a color picker control.

        Args:
            layout: Layout to add to
            label: Display label
            token_key: Token key in colors palette
            description: Tooltip description
        """
        row_layout = QHBoxLayout()

        # Label
        label_widget = QLabel(f"{label}:")
        label_widget.setMinimumWidth(150)
        label_widget.setToolTip(description)
        row_layout.addWidget(label_widget)

        # Color button
        color_button = QPushButton()
        color_button.setFixedSize(100, 30)
        current_color = getattr(self.theme_manager.tokens.colors, token_key)
        self._update_color_button(color_button, current_color)
        color_button.clicked.connect(lambda: self._choose_color(token_key, color_button))
        color_button.setToolTip(description)
        row_layout.addWidget(color_button)

        # Reset individual token button
        reset_btn = QPushButton("Reset")
        reset_btn.setMaximumWidth(60)
        reset_btn.clicked.connect(lambda: self._reset_token('colors', token_key, color_button))
        row_layout.addWidget(reset_btn)

        # Customization indicator
        is_customized = self.theme_manager.is_customized('colors', token_key)
        indicator = QLabel("●" if is_customized else "○")
        indicator.setStyleSheet(f"color: {self.theme_manager.tokens.colors.accent_primary}; font-size: 12pt;")
        indicator.setToolTip("Modified" if is_customized else "Default")
        row_layout.addWidget(indicator)

        row_layout.addStretch()
        layout.addLayout(row_layout)

    def _choose_color(self, token_key: str, button: QPushButton):
        """Open color picker and update token."""
        current_color = getattr(self.theme_manager.tokens.colors, token_key)
        qcolor = QColor(current_color)

        color = QColorDialog.getColor(qcolor, self, f"Choose {token_key} Color")

        if color.isValid():
            hex_color = color.name()
            self.theme_manager.update_color(token_key, hex_color)
            self._update_color_button(button, hex_color)
            self.theme_changed.emit()

    def _update_color_button(self, button: QPushButton, color: str):
        """Update button to show color."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                color: #ffffff;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: #00BFFF;
            }}
        """)
        button.setText(color.upper())

    def _reset_token(self, category: str, key: str, button: QPushButton = None):
        """Reset a specific token to default."""
        self.theme_manager.reset_token(category, key)

        if button and category == 'colors':
            new_color = getattr(self.theme_manager.tokens.colors, key)
            self._update_color_button(button, new_color)

        self.theme_changed.emit()
        QMessageBox.information(self, "Token Reset", f"Reset {category}.{key} to default value")

    def on_font_family_changed(self, text: str):
        """Handle font family change."""
        if text.strip():
            self.theme_manager.update_typography('font_primary', text)
            self.theme_changed.emit()

    def on_font_size_changed(self, value: int):
        """Handle font size change."""
        self.theme_manager.update_typography('size_base', value)
        self.theme_changed.emit()

    def on_base_spacing_changed(self, value: int):
        """Handle base spacing change."""
        self.theme_manager.update_spacing('base', value)
        self.theme_changed.emit()

    def on_border_radius_changed(self, value: int):
        """Handle border radius change."""
        self.theme_manager.update_radius('base', value)
        self.theme_changed.emit()

    def on_theme_updated(self):
        """Callback when theme is updated externally."""
        # Could refresh UI here if needed
        pass

    def restore_defaults(self):
        """Restore all defaults."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all default theme settings? This will reset all customizations.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.theme_manager.reset_to_defaults()
            # Rebuild UI with defaults - need to clear and recreate
            while self.layout().count():
                child = self.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.init_ui()  # Rebuild UI with defaults
            self.theme_changed.emit()
            QMessageBox.information(self, "Defaults Restored", "All theme settings have been restored to defaults.")

    def apply_theme(self):
        """Apply current theme (triggers UI update)."""
        self.theme_changed.emit()
        QMessageBox.information(
            self,
            "Theme Applied",
            "Theme changes applied! Restart the application for all changes to take effect."
        )

    def save_theme(self):
        """Save theme to file."""
        self.theme_manager.save_theme()
        QMessageBox.information(
            self,
            "Theme Saved",
            f"Theme saved successfully!\n\nCustomizations: {len(self.theme_manager._customized_tokens)} tokens"
        )


class OverlayAppearanceTab(QWidget):
    """Tab for configuring overlay-specific appearance"""

    overlay_appearance_changed = pyqtSignal(dict)

    def __init__(self, theme_manager: OmnixThemeManager, config, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize overlay appearance tab UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Overlay Window Appearance")
        header.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {self.theme_manager.tokens.colors.accent_primary}; padding: 10px;")
        layout.addWidget(header)

        # Overlay Opacity
        opacity_group = QGroupBox("Overlay Opacity")
        opacity_layout = QVBoxLayout()

        opacity_slider_layout = QHBoxLayout()
        opacity_label = QLabel("Background Opacity:")
        opacity_slider_layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(int(getattr(self.config, 'overlay_opacity', 0.95) * 100))
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        opacity_slider_layout.addWidget(self.opacity_slider)

        self.opacity_value_label = QLabel(f"{self.opacity_slider.value()}%")
        self.opacity_value_label.setMinimumWidth(50)
        opacity_slider_layout.addWidget(self.opacity_value_label)

        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)

        opacity_layout.addLayout(opacity_slider_layout)
        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)

        # Window Settings
        window_group = QGroupBox("Window Settings")
        window_layout = QVBoxLayout()

        # Stay on Top
        self.stay_on_top_check = QCheckBox("Always Stay on Top")
        self.stay_on_top_check.setChecked(getattr(self.config, 'overlay_stay_on_top', True))
        self.stay_on_top_check.setToolTip("Keep overlay window above other applications")
        window_layout.addWidget(self.stay_on_top_check)

        # Edge Snapping
        self.edge_snapping_check = QCheckBox("Enable Edge Snapping")
        self.edge_snapping_check.setChecked(getattr(self.config, 'overlay_edge_snapping', True))
        self.edge_snapping_check.setToolTip("Automatically snap window to screen edges")
        window_layout.addWidget(self.edge_snapping_check)

        # Show Minimize Button
        self.show_minimize_check = QCheckBox("Show Minimize Button")
        self.show_minimize_check.setChecked(getattr(self.config, 'overlay_show_minimize', True))
        self.show_minimize_check.setToolTip("Display minimize button in overlay header")
        window_layout.addWidget(self.show_minimize_check)

        window_group.setLayout(window_layout)
        layout.addWidget(window_group)

        # Preview Section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        preview_label = QLabel("Overlay uses the same color theme as the main application.")
        preview_label.setWordWrap(True)
        preview_label.setStyleSheet(f"color: {self.theme_manager.tokens.colors.text_secondary};")
        preview_layout.addWidget(preview_label)

        preview_button = QPushButton("Preview Overlay Stylesheet")
        preview_button.clicked.connect(self.preview_overlay_stylesheet)
        preview_layout.addWidget(preview_button)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Apply Button
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply Overlay Settings")
        apply_button.clicked.connect(self.apply_overlay_settings)
        button_layout.addWidget(apply_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    def on_opacity_changed(self, value: int):
        """Handle opacity slider change."""
        self.opacity_value_label.setText(f"{value}%")

    def preview_overlay_stylesheet(self):
        """Show preview of overlay stylesheet."""
        opacity = self.opacity_slider.value() / 100.0
        stylesheet = self.theme_manager.get_overlay_stylesheet(opacity)

        # Show first 500 characters in a message box
        preview_text = stylesheet[:500] + "\n\n... (truncated)"

        QMessageBox.information(
            self,
            "Overlay Stylesheet Preview",
            f"Opacity: {opacity:.2f}\n\n{preview_text}"
        )

    def apply_overlay_settings(self):
        """Apply overlay settings."""
        # Update config
        self.config.overlay_opacity = self.opacity_slider.value() / 100.0
        self.config.overlay_stay_on_top = self.stay_on_top_check.isChecked()
        self.config.overlay_edge_snapping = self.edge_snapping_check.isChecked()
        self.config.overlay_show_minimize = self.show_minimize_check.isChecked()

        # Save config
        self.config.save()

        self.overlay_appearance_changed.emit(self.get_overlay_settings())

        QMessageBox.information(
            self,
            "Settings Applied",
            "Overlay settings applied! Restart the application for changes to take effect."
        )

    def get_overlay_settings(self) -> dict:
        """Get current overlay settings as dict."""
        return {
            'opacity': self.opacity_slider.value() / 100.0,
            'stay_on_top': self.stay_on_top_check.isChecked(),
            'edge_snapping': self.edge_snapping_check.isChecked(),
            'show_minimize': self.show_minimize_check.isChecked(),
        }
