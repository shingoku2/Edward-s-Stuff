# Omnix UI Design System

A comprehensive design system for the Omnix AI Gaming Companion, featuring a high-tech, AI-focused aesthetic with dark themes and vibrant electric blue accents.

## Overview

The Omnix UI Design System provides:
- **Design Tokens**: Centralized colors, typography, spacing, and other design values
- **Component Library**: Reusable PyQt6 components with consistent styling
- **QSS Stylesheets**: Pre-built stylesheets for the entire application
- **Icon System**: SVG-based scalable icons
- **Overlay Components**: Specialized components for in-game overlay

## Color Palette

### Backgrounds
- **Primary**: `#1A1A2E` - Deep charcoal
- **Primary Alt**: `#0F0F1A` - Near-black
- **Secondary**: `#2C2C4A` - Dark muted blue
- **Secondary Alt**: `#3A3A5A` - Lighter blue-grey

### Accent Colors
- **Primary Accent**: `#00BFFF` - Electric Blue (main interactive elements)
- **Bright Accent**: `#00FFFF` - Cyan (highlights, hover states)
- **Dark Accent**: `#1E90FF` - Dodger Blue (pressed states)
- **Secondary Accent**: `#39FF14` - Neon Green (success, warnings)
- **Tertiary Accent**: `#8A2BE2` - Purple (alternative states)

### Text
- **Primary**: `#FFFFFF` - White
- **Secondary**: `#E0E0E0` - Light grey
- **Muted**: `#B0B0B0` - Medium grey
- **Disabled**: `#707070` - Dark grey

### Status
- **Success**: `#39FF14` - Neon Green
- **Warning**: `#FFB800` - Amber
- **Error**: `#FF3B3B` - Red
- **Info**: `#00BFFF` - Electric Blue

## Typography

### Font Families
- **Primary**: Roboto, Open Sans, Montserrat (clean, modern sans-serif)
- **Monospace**: Fira Code, Source Code Pro (code, data displays)

### Font Sizes
- XS: 9pt
- SM: 10pt
- Base: 11pt
- MD: 12pt
- LG: 14pt
- XL: 16pt
- 2XL: 20pt
- 3XL: 24pt
- 4XL: 32pt

### Font Weights
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## Spacing

Based on a 4px unit system:
- XS: 4px
- SM: 8px
- MD: 12px
- Base: 16px
- LG: 24px
- XL: 32px
- 2XL: 48px
- 3XL: 64px

## Border Radius
- SM: 3px
- Base: 5px
- MD: 8px
- LG: 12px
- XL: 16px
- Full: 9999px (pill shape)

## Components

### Buttons

```python
from omnix.ui.components import OmnixButton

# Primary button (default)
btn_primary = OmnixButton("Click Me")

# Secondary button
btn_secondary = OmnixButton("Cancel", style="secondary")

# Danger button
btn_danger = OmnixButton("Delete", style="danger")

# Success button
btn_success = OmnixButton("Save", style="success")

# Icon button
btn_icon = OmnixIconButton(text="X", size=32)
```

### Input Fields

```python
from omnix.ui.components import OmnixLineEdit, OmnixTextEdit, OmnixComboBox

# Line edit
name_input = OmnixLineEdit(placeholder="Enter your name", clearable=True)

# Password input
password = OmnixLineEdit(placeholder="Password", echo_mode="password")

# Text edit
description = OmnixTextEdit(placeholder="Enter description...")

# Combo box
options = OmnixComboBox(items=["Option 1", "Option 2", "Option 3"])
```

### Cards & Panels

```python
from omnix.ui.components import OmnixCard, OmnixPanel, OmnixInfoCard

# Panel (simple container)
panel = OmnixPanel(padding=16)
panel.layout().addWidget(some_widget)

# Card (with header)
card = OmnixCard(title="Settings", hoverable=True)
card.add_content(settings_widget)

# Info card
info = OmnixInfoCard(
    title="Session Stats",
    description="Total playtime: 2h 34m",
    icon="📊"
)
```

### Layouts

```python
from omnix.ui.components import OmnixVBox, OmnixHBox, OmnixGrid, OmnixFormLayout

# Vertical layout
vbox = OmnixVBox(spacing=12)
vbox.add_widget(widget1)
vbox.add_widget(widget2)
vbox.add_stretch()

# Horizontal layout
hbox = OmnixHBox(spacing=8)
hbox.add_widget(label)
hbox.add_widget(input_field)

# Grid layout
grid = OmnixGrid(spacing=12)
grid.add_widget(widget1, 0, 0)
grid.add_widget(widget2, 0, 1)

# Form layout
form = OmnixFormLayout()
form.add_row("Username:", username_input)
form.add_row("Email:", email_input)
```

### Navigation

```python
from omnix.ui.components import OmnixSidebar, OmnixHeaderBar

# Sidebar navigation
sidebar = OmnixSidebar()
sidebar.add_button("Chat", "💬", on_chat_clicked)
sidebar.add_button("Settings", "⚙️", on_settings_clicked)
sidebar.add_button("Game Profiles", "🎮", on_profiles_clicked)
sidebar.add_stretch()
sidebar.add_button("About", "ℹ️", on_about_clicked)

# Header bar
header = OmnixHeaderBar(title="Omnix AI Assistant", logo_text="⬡")
header.set_status("Online", "success")
```

### Modals

```python
from omnix.ui.components import (
    OmnixDialog,
    OmnixConfirmDialog,
    OmnixMessageDialog,
    OmnixInputDialog
)

# Custom dialog
dialog = OmnixDialog(title="Custom Dialog", parent=self, width=500)
dialog.add_content(custom_widget)
dialog.add_default_buttons()
if dialog.exec():
    # OK clicked
    pass

# Confirmation dialog
confirm = OmnixConfirmDialog(
    title="Delete Profile",
    message="Are you sure you want to delete this profile?",
    confirm_text="Delete",
    is_dangerous=True,
    parent=self
)
if confirm.exec():
    # User confirmed deletion
    pass

# Message dialog
OmnixMessageDialog(
    title="Success",
    message="Settings saved successfully!",
    message_type="success",
    parent=self
).exec()

# Input dialog
input_dlg = OmnixInputDialog(
    title="New Profile",
    label="Profile Name:",
    placeholder="My Profile",
    parent=self
)
if input_dlg.exec():
    name = input_dlg.get_value()
```

### Overlay Components

```python
from omnix.ui.components.overlay import (
    OmnixOverlayPanel,
    OmnixOverlayChatWidget,
    OmnixOverlayTip,
    OmnixOverlayStatus
)

# Overlay panel
panel = OmnixOverlayPanel(opacity=0.75)
panel.layout().addWidget(content)

# Chat widget
chat = OmnixOverlayChatWidget()
chat.message_sent.connect(handle_message)
chat.add_message("AI", "How can I help you?")

# Contextual tip
tip = OmnixOverlayTip(
    message="Low HP! Consider healing.",
    duration=3000,
    tip_type="warning"
)
tip.show_tip()

# Status indicator
status = OmnixOverlayStatus()
status.set_status("Macro Active", "success")
```

## Icons

```python
from omnix.ui.icons import OmnixIcons, icons

# Get an icon
chat_icon = OmnixIcons.get_icon("chat")
settings_icon = icons.get_icon("settings", color="#00BFFF", size=32)

# Available icons
available = icons.available_icons()
# ['omnix_logo', 'chat', 'settings', 'knowledge', 'game', 'macro',
#  'ai', 'session', 'secure', 'add', 'close', 'minimize', 'maximize']

# Use icon in button
from omnix.ui.components import OmnixButton
button = OmnixButton("Chat")
button.setIcon(icons.get_icon("chat"))
```

## Applying the Design System

### Main Application

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from omnix.ui import design_system

app = QApplication([])

# Apply global stylesheet
app.setStyleSheet(design_system.generate_complete_stylesheet())

# Create main window
window = QMainWindow()
window.show()

app.exec()
```

### Overlay Window

```python
from PyQt6.QtWidgets import QWidget
from omnix.ui import design_system

overlay = QWidget()
overlay.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

# Apply overlay stylesheet
overlay.setStyleSheet(design_system.generate_overlay_stylesheet(opacity=0.75))
```

## Design Principles

### Visual Language
1. **Sharp, Clean Lines**: Minimalist UI with geometric shapes
2. **Subtle Glow Effects**: Electric blue glow on active/hover states
3. **Smooth Animations**: Fade, slide, pulse (150-350ms duration)
4. **Semi-transparency**: Frosted glass effect for overlays
5. **Dark Foundation**: Near-black backgrounds with vibrant accents

### Component Hierarchy
1. **Header**: Logo, title, status (60px height)
2. **Sidebar**: Icon-based navigation (80px+ width)
3. **Main Content**: Cards and panels on dark background
4. **Footer**: Actions and status information

### Accessibility
- High contrast text (white on dark backgrounds)
- Clear focus states (2px electric blue border)
- Adequate spacing (minimum 8px between interactive elements)
- Keyboard navigation support

## Best Practices

### DO
✓ Use design tokens for all colors, spacing, and typography
✓ Leverage pre-built components for consistency
✓ Apply hover/focus states for interactive elements
✓ Use appropriate button styles (primary for main actions, secondary for cancel)
✓ Maintain the dark theme aesthetic
✓ Use electric blue for primary actions and highlights

### DON'T
✗ Use hardcoded color values
✗ Create inline styles when components exist
✗ Mix different color schemes
✗ Use bright backgrounds (breaks the dark theme)
✗ Overuse animations (keep subtle and purposeful)
✗ Ignore accessibility (contrast, focus states)

## Migration Guide

For existing components:

```python
# Old approach (inline styles)
button = QPushButton("Save")
button.setStyleSheet("""
    QPushButton {
        background-color: #00BFFF;
        color: white;
        padding: 8px 16px;
        border-radius: 5px;
    }
""")

# New approach (design system)
from omnix.ui.components import OmnixButton
button = OmnixButton("Save", style="primary")
```

## Support

For questions or issues:
- Check this documentation
- Review example code in `src/omnix/ui/examples/`
- Consult the design tokens in `src/omnix/ui/tokens.py`
- Review component source in `src/omnix/ui/components/`
