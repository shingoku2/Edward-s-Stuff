"""
Appearance Configuration Tabs
Contains UI tabs for appearance customization
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QSlider, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QMessageBox, QColorDialog, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette

from theme_manager import (
    Theme, ThemeManager, ThemeMode, UIScale, LayoutMode,
    OverlayAppearance, OverlayPosition,
    DEFAULT_DARK_THEME, DEFAULT_LIGHT_THEME
)

logger = logging.getLogger(__name__)


class AppAppearanceTab(QWidget):
    """Tab for configuring main app appearance"""

    theme_changed = pyqtSignal(dict)  # Emits theme dict

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_theme = theme_manager.current_theme
        self.init_ui()

    def init_ui(self):
        """Initialize app appearance tab UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Main Application Appearance")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #14b8a6; padding: 10px;")
        layout.addWidget(header)

        # Theme Mode
        theme_group = QGroupBox("Theme Mode")
        theme_layout = QVBoxLayout()

        self.theme_button_group = QButtonGroup()

        self.dark_radio = QRadioButton("Dark Mode")
        self.light_radio = QRadioButton("Light Mode")
        self.auto_radio = QRadioButton("Auto (System)")

        self.theme_button_group.addButton(self.dark_radio, 0)
        self.theme_button_group.addButton(self.light_radio, 1)
        self.theme_button_group.addButton(self.auto_radio, 2)

        if self.current_theme.mode == ThemeMode.DARK.value:
            self.dark_radio.setChecked(True)
        elif self.current_theme.mode == ThemeMode.LIGHT.value:
            self.light_radio.setChecked(True)
        else:
            self.auto_radio.setChecked(True)

        self.theme_button_group.buttonClicked.connect(self.on_theme_mode_changed)

        theme_layout.addWidget(self.dark_radio)
        theme_layout.addWidget(self.light_radio)
        theme_layout.addWidget(self.auto_radio)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Colors
        colors_group = QGroupBox("Colors")
        colors_layout = QVBoxLayout()

        # Primary color
        primary_layout = QHBoxLayout()
        primary_label = QLabel("Primary Color:")
        primary_layout.addWidget(primary_label)

        self.primary_button = QPushButton()
        self.primary_button.setFixedSize(100, 30)
        self.update_color_button(self.primary_button, self.current_theme.primary_color)
        self.primary_button.clicked.connect(lambda: self.choose_color('primary'))
        primary_layout.addWidget(self.primary_button)

        primary_layout.addStretch()
        colors_layout.addLayout(primary_layout)

        # Secondary color
        secondary_layout = QHBoxLayout()
        secondary_label = QLabel("Secondary Color:")
        secondary_layout.addWidget(secondary_label)

        self.secondary_button = QPushButton()
        self.secondary_button.setFixedSize(100, 30)
        self.update_color_button(self.secondary_button, self.current_theme.secondary_color)
        self.secondary_button.clicked.connect(lambda: self.choose_color('secondary'))
        secondary_layout.addWidget(self.secondary_button)

        secondary_layout.addStretch()
        colors_layout.addLayout(secondary_layout)

        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)

        # Typography
        typo_group = QGroupBox("Typography")
        typo_layout = QVBoxLayout()

        # Font size
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        font_size_layout.addWidget(font_size_label)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(self.current_theme.font_size)
        self.font_size_spin.setSuffix(" pt")
        font_size_layout.addWidget(self.font_size_spin)

        font_size_layout.addStretch()
        typo_layout.addLayout(font_size_layout)

        # UI Scale
        scale_layout = QHBoxLayout()
        scale_label = QLabel("UI Scale:")
        scale_layout.addWidget(scale_label)

        self.scale_combo = QComboBox()
        for scale in UIScale:
            self.scale_combo.addItem(scale.value.title(), scale.value)

        current_index = self.scale_combo.findData(self.current_theme.ui_scale)
        if current_index >= 0:
            self.scale_combo.setCurrentIndex(current_index)

        scale_layout.addWidget(self.scale_combo)

        scale_layout.addStretch()
        typo_layout.addLayout(scale_layout)

        typo_group.setLayout(typo_layout)
        layout.addWidget(typo_group)

        # Layout
        layout_group = QGroupBox("Layout")
        layout_layout = QVBoxLayout()

        # Layout mode
        layout_mode_layout = QHBoxLayout()
        layout_mode_label = QLabel("Density:")
        layout_mode_layout.addWidget(layout_mode_label)

        self.layout_mode_combo = QComboBox()
        for mode in LayoutMode:
            self.layout_mode_combo.addItem(mode.value.title(), mode.value)

        current_index = self.layout_mode_combo.findData(self.current_theme.layout_mode)
        if current_index >= 0:
            self.layout_mode_combo.setCurrentIndex(current_index)

        layout_mode_layout.addWidget(self.layout_mode_combo)

        layout_mode_layout.addStretch()
        layout_layout.addLayout(layout_mode_layout)

        # Transparency
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("Window Transparency:")
        transparency_layout.addWidget(transparency_label)

        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(50, 100)
        self.transparency_slider.setValue(int(self.current_theme.transparency * 100))
        self.transparency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.transparency_slider.setTickInterval(10)
        transparency_layout.addWidget(self.transparency_slider)

        self.transparency_value_label = QLabel(f"{int(self.current_theme.transparency * 100)}%")
        self.transparency_slider.valueChanged.connect(
            lambda v: self.transparency_value_label.setText(f"{v}%")
        )
        transparency_layout.addWidget(self.transparency_value_label)

        layout_layout.addLayout(transparency_layout)

        layout_group.setLayout(layout_layout)
        layout.addWidget(layout_group)

        # Buttons
        button_layout = QHBoxLayout()

        restore_button = QPushButton("Restore Defaults")
        restore_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(restore_button)

        preview_button = QPushButton("Preview Changes")
        preview_button.clicked.connect(self.preview_theme)
        button_layout.addWidget(preview_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    def on_theme_mode_changed(self, button):
        """Handle theme mode change"""
        if button == self.dark_radio:
            self.current_theme.mode = ThemeMode.DARK.value
            # Load dark theme defaults
            self.current_theme.background_color = DEFAULT_DARK_THEME.background_color
            self.current_theme.surface_color = DEFAULT_DARK_THEME.surface_color
            self.current_theme.text_color = DEFAULT_DARK_THEME.text_color
            self.current_theme.text_secondary_color = DEFAULT_DARK_THEME.text_secondary_color
        elif button == self.light_radio:
            self.current_theme.mode = ThemeMode.LIGHT.value
            # Load light theme defaults
            self.current_theme.background_color = DEFAULT_LIGHT_THEME.background_color
            self.current_theme.surface_color = DEFAULT_LIGHT_THEME.surface_color
            self.current_theme.text_color = DEFAULT_LIGHT_THEME.text_color
            self.current_theme.text_secondary_color = DEFAULT_LIGHT_THEME.text_secondary_color
        else:
            self.current_theme.mode = ThemeMode.AUTO.value

    def choose_color(self, color_type: str):
        """Open color picker dialog"""
        if color_type == 'primary':
            current_color = QColor(self.current_theme.primary_color)
            button = self.primary_button
        elif color_type == 'secondary':
            current_color = QColor(self.current_theme.secondary_color)
            button = self.secondary_button
        else:
            return

        color = QColorDialog.getColor(current_color, self, f"Choose {color_type.title()} Color")

        if color.isValid():
            hex_color = color.name()
            if color_type == 'primary':
                self.current_theme.primary_color = hex_color
            elif color_type == 'secondary':
                self.current_theme.secondary_color = hex_color

            self.update_color_button(button, hex_color)

    def update_color_button(self, button: QPushButton, color: str):
        """Update button with color"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #3a3a3a;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border-color: #14b8a6;
            }}
        """)
        button.setText(color)

    def preview_theme(self):
        """Preview theme changes"""
        self.apply_theme_settings()
        QMessageBox.information(
            self,
            "Preview",
            "Theme preview applied! Changes will be saved when you click 'Save Settings'."
        )

    def restore_defaults(self):
        """Restore default theme"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore default appearance settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.current_theme = Theme() if self.dark_radio.isChecked() else DEFAULT_DARK_THEME
            self.init_ui()  # Reload UI with defaults
            QMessageBox.information(self, "Defaults Restored", "Default appearance settings have been restored.")

    def apply_theme_settings(self):
        """Apply current theme settings to the theme object"""
        self.current_theme.font_size = self.font_size_spin.value()
        self.current_theme.ui_scale = self.scale_combo.currentData()
        self.current_theme.layout_mode = self.layout_mode_combo.currentData()
        self.current_theme.transparency = self.transparency_slider.value() / 100.0

        self.theme_manager.set_theme(self.current_theme)

    def emit_theme(self):
        """Emit theme changed signal"""
        self.apply_theme_settings()
        theme_dict = self.theme_manager.save_to_dict()
        self.theme_changed.emit(theme_dict)

    def get_theme(self) -> dict:
        """Get current theme as dictionary"""
        self.apply_theme_settings()
        return self.theme_manager.save_to_dict()


class OverlayAppearanceTab(QWidget):
    """Tab for configuring overlay appearance"""

    overlay_appearance_changed = pyqtSignal(dict)  # Emits overlay appearance dict

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.overlay_appearance = theme_manager.overlay_appearance
        self.init_ui()

    def init_ui(self):
        """Initialize overlay appearance tab UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("In-Game Overlay Appearance")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #14b8a6; padding: 10px;")
        layout.addWidget(header)

        # Position
        position_group = QGroupBox("Position")
        position_layout = QVBoxLayout()

        # Position preset
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Position Preset:")
        preset_layout.addWidget(preset_label)

        self.position_combo = QComboBox()
        for position in OverlayPosition:
            self.position_combo.addItem(position.value.replace('_', ' ').title(), position.value)

        current_index = self.position_combo.findData(self.overlay_appearance.position_preset)
        if current_index >= 0:
            self.position_combo.setCurrentIndex(current_index)

        self.position_combo.currentIndexChanged.connect(self.on_position_changed)
        preset_layout.addWidget(self.position_combo)

        preset_layout.addStretch()
        position_layout.addLayout(preset_layout)

        # Custom position (only enabled for CUSTOM preset)
        custom_layout = QHBoxLayout()

        x_label = QLabel("X:")
        custom_layout.addWidget(x_label)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 10000)
        self.x_spin.setValue(self.overlay_appearance.custom_x)
        custom_layout.addWidget(self.x_spin)

        y_label = QLabel("Y:")
        custom_layout.addWidget(y_label)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 10000)
        self.y_spin.setValue(self.overlay_appearance.custom_y)
        custom_layout.addWidget(self.y_spin)

        custom_layout.addStretch()
        position_layout.addLayout(custom_layout)

        position_group.setLayout(position_layout)
        layout.addWidget(position_group)

        # Size
        size_group = QGroupBox("Size")
        size_layout = QVBoxLayout()

        size_input_layout = QHBoxLayout()

        width_label = QLabel("Width:")
        size_input_layout.addWidget(width_label)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 3840)
        self.width_spin.setValue(self.overlay_appearance.width)
        self.width_spin.setSuffix(" px")
        size_input_layout.addWidget(self.width_spin)

        height_label = QLabel("Height:")
        size_input_layout.addWidget(height_label)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(300, 2160)
        self.height_spin.setValue(self.overlay_appearance.height)
        self.height_spin.setSuffix(" px")
        size_input_layout.addWidget(self.height_spin)

        size_input_layout.addStretch()
        size_layout.addLayout(size_input_layout)

        # Scale
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Scale:")
        scale_layout.addWidget(scale_label)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(50, 150)
        self.scale_slider.setValue(int(self.overlay_appearance.scale * 100))
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.setTickInterval(10)
        scale_layout.addWidget(self.scale_slider)

        self.scale_value_label = QLabel(f"{int(self.overlay_appearance.scale * 100)}%")
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_value_label.setText(f"{v}%")
        )
        scale_layout.addWidget(self.scale_value_label)

        size_layout.addLayout(scale_layout)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # Opacity
        opacity_group = QGroupBox("Opacity")
        opacity_layout = QHBoxLayout()

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(self.overlay_appearance.opacity * 100))
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        opacity_layout.addWidget(self.opacity_slider)

        self.opacity_value_label = QLabel(f"{int(self.overlay_appearance.opacity * 100)}%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_value_label.setText(f"{v}%")
        )
        opacity_layout.addWidget(self.opacity_value_label)

        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)

        # Behavior
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.edge_snapping_check = QCheckBox("Enable Edge Snapping")
        self.edge_snapping_check.setChecked(self.overlay_appearance.edge_snapping)
        behavior_layout.addWidget(self.edge_snapping_check)

        snap_layout = QHBoxLayout()
        snap_label = QLabel("Snap Threshold:")
        snap_layout.addWidget(snap_label)

        self.snap_threshold_spin = QSpinBox()
        self.snap_threshold_spin.setRange(5, 100)
        self.snap_threshold_spin.setValue(self.overlay_appearance.snap_threshold)
        self.snap_threshold_spin.setSuffix(" px")
        snap_layout.addWidget(self.snap_threshold_spin)

        snap_layout.addStretch()
        behavior_layout.addLayout(snap_layout)

        self.stay_on_top_check = QCheckBox("Always Stay On Top")
        self.stay_on_top_check.setChecked(self.overlay_appearance.stay_on_top)
        behavior_layout.addWidget(self.stay_on_top_check)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        # Visible Panels
        panels_group = QGroupBox("Visible Panels")
        panels_layout = QVBoxLayout()

        self.show_header_check = QCheckBox("Show Header")
        self.show_header_check.setChecked(self.overlay_appearance.show_header)
        panels_layout.addWidget(self.show_header_check)

        self.show_minimize_check = QCheckBox("Show Minimize Button")
        self.show_minimize_check.setChecked(self.overlay_appearance.show_minimize_button)
        panels_layout.addWidget(self.show_minimize_check)

        self.show_chat_check = QCheckBox("Show Chat Panel")
        self.show_chat_check.setChecked(self.overlay_appearance.show_chat)
        panels_layout.addWidget(self.show_chat_check)

        self.show_game_info_check = QCheckBox("Show Game Info")
        self.show_game_info_check.setChecked(self.overlay_appearance.show_game_info)
        panels_layout.addWidget(self.show_game_info_check)

        panels_group.setLayout(panels_layout)
        layout.addWidget(panels_group)

        # Buttons
        button_layout = QHBoxLayout()

        restore_button = QPushButton("Restore Defaults")
        restore_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(restore_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

        # Set initial enabled state for custom position
        self.on_position_changed(self.position_combo.currentIndex())

    def on_position_changed(self, index):
        """Handle position preset change"""
        position = self.position_combo.currentData()
        is_custom = (position == OverlayPosition.CUSTOM.value)

        self.x_spin.setEnabled(is_custom)
        self.y_spin.setEnabled(is_custom)

    def restore_defaults(self):
        """Restore default overlay appearance"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore default overlay appearance settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.overlay_appearance = OverlayAppearance()
            self.theme_manager.set_overlay_appearance(self.overlay_appearance)
            self.init_ui()  # Reload UI with defaults
            QMessageBox.information(self, "Defaults Restored", "Default overlay appearance settings have been restored.")

    def apply_overlay_settings(self):
        """Apply current overlay settings to the overlay appearance object"""
        self.overlay_appearance.position_preset = self.position_combo.currentData()
        self.overlay_appearance.custom_x = self.x_spin.value()
        self.overlay_appearance.custom_y = self.y_spin.value()
        self.overlay_appearance.width = self.width_spin.value()
        self.overlay_appearance.height = self.height_spin.value()
        self.overlay_appearance.scale = self.scale_slider.value() / 100.0
        self.overlay_appearance.opacity = self.opacity_slider.value() / 100.0
        self.overlay_appearance.edge_snapping = self.edge_snapping_check.isChecked()
        self.overlay_appearance.snap_threshold = self.snap_threshold_spin.value()
        self.overlay_appearance.stay_on_top = self.stay_on_top_check.isChecked()
        self.overlay_appearance.show_header = self.show_header_check.isChecked()
        self.overlay_appearance.show_minimize_button = self.show_minimize_check.isChecked()
        self.overlay_appearance.show_chat = self.show_chat_check.isChecked()
        self.overlay_appearance.show_game_info = self.show_game_info_check.isChecked()

        self.theme_manager.set_overlay_appearance(self.overlay_appearance)

    def emit_overlay_appearance(self):
        """Emit overlay appearance changed signal"""
        self.apply_overlay_settings()
        appearance_dict = self.theme_manager.save_to_dict()
        self.overlay_appearance_changed.emit(appearance_dict)

    def get_overlay_appearance(self) -> dict:
        """Get current overlay appearance as dictionary"""
        self.apply_overlay_settings()
        return self.theme_manager.save_to_dict()
