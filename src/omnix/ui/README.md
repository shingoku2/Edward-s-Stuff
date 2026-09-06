# Omnix UI Design System

A comprehensive, production-ready UI design system for the Omnix AI Gaming Companion.

## Features

✨ **Complete Design System**
- Centralized design tokens (colors, typography, spacing)
- Pre-built, reusable components
- Comprehensive QSS stylesheets
- SVG-based icon system

🎨 **High-Tech Aesthetic**
- Dark theme with electric blue accents
- Semi-transparent overlays with frosted glass effect
- Smooth animations and transitions
- Sharp, minimalist geometric design

🔧 **Developer Friendly**
- Type-safe dataclasses for tokens
- Well-documented components
- Easy to extend and customize
- Backward compatible with existing theme system

## Quick Start

### Apply Design System to Application

```python
from PyQt6.QtWidgets import QApplication
from omnix.ui import design_system

app = QApplication([])

# Apply Omnix design system
app.setStyleSheet(design_system.generate_complete_stylesheet())
```

### Use Components

```python
from omnix.ui.components import OmnixButton, OmnixCard, OmnixSidebar

# Create a button
button = OmnixButton("Click Me", style="primary")

# Create a card
card = OmnixCard(title="Settings")
card.add_content(my_widget)

# Create sidebar navigation
sidebar = OmnixSidebar()
sidebar.add_button("Chat", "💬", on_chat_clicked)
```

### Access Design Tokens

```python
from omnix.ui.tokens import COLORS, TYPOGRAPHY, SPACING

# Use design tokens
background = COLORS.bg_primary  # "#1A1A2E"
accent = COLORS.accent_primary  # "#00BFFF"
font_size = TYPOGRAPHY.size_md  # 12pt
padding = SPACING.base  # 16px
```

## Structure

```
src/omnix/ui/
├── __init__.py              # Main exports
├── tokens.py                # Design tokens (colors, typography, spacing)
├── design_system.py         # QSS stylesheet generator
├── icons.py                 # SVG icon system
├── components/              # Reusable UI components
│   ├── __init__.py
│   ├── buttons.py          # Button components
│   ├── inputs.py           # Input field components
│   ├── cards.py            # Card and panel components
│   ├── layouts.py          # Layout utilities
│   ├── navigation.py       # Navigation components
│   ├── modals.py           # Dialog components
│   └── overlay.py          # In-game overlay components
├── examples/                # Example code and demos
│   └── demo.py             # Full UI demo application
└── DESIGN_SYSTEM.md        # Complete documentation
```

## Components

### Buttons
- `OmnixButton` - Primary, secondary, danger, success buttons
- `OmnixIconButton` - Circular icon-only button

### Inputs
- `OmnixLineEdit` - Single-line text input
- `OmnixTextEdit` - Multi-line text input
- `OmnixComboBox` - Dropdown selector

### Cards & Panels
- `OmnixPanel` - Basic container with styling
- `OmnixCard` - Card with optional header
- `OmnixInfoCard` - Information card with icon

### Layouts
- `OmnixVBox` - Vertical box layout
- `OmnixHBox` - Horizontal box layout
- `OmnixGrid` - Grid layout
- `OmnixFormLayout` - Form layout with labels

### Navigation
- `OmnixSidebar` - Sidebar navigation with icons
- `OmnixHeaderBar` - Application header with status
- `OmnixSidebarButton` - Navigation button

### Dialogs
- `OmnixDialog` - Base dialog component
- `OmnixConfirmDialog` - Confirmation dialog
- `OmnixMessageDialog` - Message/alert dialog
- `OmnixInputDialog` - Input dialog

### Overlay Components
- `OmnixOverlayPanel` - Semi-transparent panel
- `OmnixOverlayChatWidget` - In-game chat
- `OmnixOverlayTip` - Contextual tip popup
- `OmnixOverlayStatus` - Status indicator

## Running the Demo

See all components in action:

```bash
python src/omnix/ui/examples/demo.py
```

## Documentation

See [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) for complete documentation including:
- Color palette details
- Typography system
- Spacing and layout guidelines
- Component usage examples
- Best practices
- Migration guide

## Integration with Existing Code

For legacy callers, use the compatibility layer to translate existing themes to the new token system:

```python
from theme_compat import ThemeManagerCompat

compat = ThemeManagerCompat()
legacy_theme = compat.current_theme

# Update legacy values as needed
legacy_theme.primary_color = "#FF00FF"
compat.set_theme(legacy_theme)

# Apply updated stylesheet
app.setStyleSheet(compat.generate_stylesheet())
```

## Customization

Customize the design system by modifying tokens:

```python
from omnix.ui.tokens import tokens

# Customize colors
tokens.colors.accent_primary = "#FF00FF"  # Change to magenta
tokens.colors.bg_primary = "#000000"  # Pure black background

# Regenerate stylesheet
from omnix.ui.design_system import design_system
custom_stylesheet = design_system.generate_complete_stylesheet()
```

## Icons

Access built-in icons:

```python
from omnix.ui.icons import icons

# Get available icons
available = icons.available_icons()

# Use an icon
chat_icon = icons.get_icon("chat", color="#00BFFF", size=32)
button.setIcon(chat_icon)
```

Available icons:
- `omnix_logo` - Hexagonal O with circuit pattern
- `chat` - Speech bubble
- `settings` - Gear icon
- `knowledge` - Book with circuit overlay
- `game` - Game controller
- `macro` - Keyboard with arrow
- `ai` - AI head profile
- `session` - Stopwatch with graph
- `secure` - Shield with lock
- `add`, `close`, `minimize`, `maximize` - UI controls

## License

Part of the Omnix AI Gaming Companion project.
