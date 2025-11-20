# Omnix Dashboard Component

## Overview

The Omnix Dashboard is a futuristic gaming overlay interface that provides quick access to all major features of the Omnix AI Gaming Companion. It features a glassmorphism design with neon accents and a cyberpunk aesthetic.

## Architecture

The dashboard consists of two main components:

### 1. OmnixStatusCard (Hero Section)
- **Title**: "Omnix AI Assistant" in large cyan/blue text
- **Status Indicator**: Active/Inactive with color-coded dot
  - Active: Neon magenta (#FF0055)
  - Inactive: Muted gray
- **Activity Display**: Shows current game being played with gamepad icon

### 2. OmnixDashboard (Main Component)
- **Layout**: 3x2 grid of action buttons
- **Glassmorphism**: Semi-transparent backgrounds with subtle borders
- **Responsive**: Adapts to different screen sizes

## Action Grid

The dashboard provides 6 main actions organized in a 3-column, 2-row grid:

| Row 1 | | |
|-------|-------|-------|
| **Chat** | **AI Provider** | **Settings** |
| Speech bubble icon | AI robot icon | Gear icon |

| Row 2 | | |
|-------|-------|-------|
| **Game Profiles** | **Knowledge Pack** | **Session Coaching** |
| Gamepad icon | Book icon | Session icon |

## Design Specifications

### Color Palette
- **Primary Background**: Deep Space (#050508, #14192899 with alpha)
- **Accent Primary**: Cyber Cyan (#00F0FF)
- **Accent Secondary**: Neon Magenta (#FF0055)
- **Text Primary**: White (#FFFFFF)
- **Text Secondary**: Cool Grey (#A0A0B0)

### Typography
- **Title**: 32pt, Bold, Letter-spacing 0.05em
- **Status**: 16pt, Semibold
- **Activity**: 12pt, Regular
- **Button Labels**: 10pt, Medium

### Spacing
- **Container Padding**: 64px
- **Grid Spacing**: 16px
- **Card Padding**: 32px
- **Element Spacing**: 16px

### Border Radius
- **Cards**: 12px
- **Buttons**: 6px

## Usage

### Basic Usage

```python
from ui.components import OmnixDashboard

# Create dashboard
dashboard = OmnixDashboard()

# Set game status
dashboard.set_active(True)
dashboard.set_game("Elden Ring")

# Connect signals
dashboard.chat_clicked.connect(open_chat)
dashboard.provider_clicked.connect(open_provider_settings)
dashboard.settings_clicked.connect(open_settings)
dashboard.profiles_clicked.connect(open_game_profiles)
dashboard.knowledge_clicked.connect(open_knowledge_packs)
dashboard.coaching_clicked.connect(open_session_coaching)
```

### As Overlay

```python
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from ui.components import OmnixDashboard
from ui.design_system import OmnixDesignSystem

# Create window
window = QMainWindow()
window.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.WindowStaysOnTopHint
)
window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

# Apply design system
design_system = OmnixDesignSystem()
window.setStyleSheet(design_system.generate_base_stylesheet())

# Set dashboard as central widget
dashboard = OmnixDashboard()
window.setCentralWidget(dashboard)

window.show()
```

### Dynamic Updates

```python
# Update status
dashboard.set_active(False)  # Set to inactive

# Update game
dashboard.set_game("Cyberpunk 2077")  # Change game
dashboard.set_game(None)  # No game detected
```

## Signals

The dashboard emits the following signals when buttons are clicked:

| Signal | Description |
|--------|-------------|
| `chat_clicked()` | User clicked Chat button |
| `provider_clicked()` | User clicked AI Provider button |
| `settings_clicked()` | User clicked Settings button |
| `profiles_clicked()` | User clicked Game Profiles button |
| `knowledge_clicked()` | User clicked Knowledge Pack button |
| `coaching_clicked()` | User clicked Session Coaching button |

## Component Hierarchy

```
OmnixDashboard (QWidget)
├── OmnixStatusCard (QFrame)
│   ├── Title Label ("Omnix AI Assistant")
│   ├── Status Container (QWidget)
│   │   ├── Status Dot (QLabel)
│   │   └── Status Text (QLabel)
│   └── Activity Container (QWidget)
│       ├── Game Icon (QLabel)
│       └── Activity Text (QLabel)
└── Action Grid Container (QWidget)
    └── Grid Layout (QGridLayout)
        ├── Chat Button (OmnixDashboardButton)
        ├── AI Provider Button (OmnixDashboardButton)
        ├── Settings Button (OmnixDashboardButton)
        ├── Game Profiles Button (OmnixDashboardButton)
        ├── Knowledge Pack Button (OmnixDashboardButton)
        └── Session Coaching Button (OmnixDashboardButton)
```

## Icon Mapping

The dashboard uses the Omnix icon system with the following mappings:

| UI Element | Icon Name | SVG Description |
|------------|-----------|-----------------|
| Chat | `"chat"` | Speech bubble with lines |
| AI Provider | `"ai"` | Robot/AI circuit design |
| Settings | `"settings"` | Gear with 8 spokes |
| Game Profiles | `"game"` | Game controller |
| Knowledge Pack | `"knowledge"` | Book with circuit overlay |
| Session Coaching | `"session"` | Session/timer icon |
| Game Activity | `"game"` | Game controller (in status card) |

## Testing

Run the dashboard test:

```bash
# Test dashboard component
python test_dashboard.py
```

This will open a window displaying the dashboard with test data:
- Status: Active
- Game: Elden Ring
- All buttons functional with console output

## Customization

### Custom Styling

```python
dashboard = OmnixDashboard()

# Access status card
dashboard.status_card.setStyleSheet("""
    OmnixStatusCard {
        background-color: #custom;
    }
""")

# Access individual buttons
dashboard.buttons['chat'].setStyleSheet("""
    OmnixDashboardButton {
        min-width: 150px;
    }
""")
```

### Custom Button Actions

```python
def custom_chat_handler():
    print("Custom chat logic")
    # Your logic here

dashboard.chat_clicked.connect(custom_chat_handler)
```

## Design Notes

### Glassmorphism Effect
The dashboard uses semi-transparent backgrounds (#RRGGBBAA hex format) to create a frosted glass effect. This is Qt-compatible and avoids the rgba() decimal alpha issues.

### Hover States
All dashboard buttons have hover states that:
- Brighten the background
- Change border to accent primary color
- Provide visual feedback

### Accessibility
- High contrast colors (cyan on dark)
- Large touch targets (120x120px minimum)
- Clear visual hierarchy
- Semantic HTML-like structure

## Integration with Omnix

The dashboard integrates with the main Omnix application:

```python
# In main GUI
from ui.components import OmnixDashboard

class OmnixMainWindow(QMainWindow):
    def show_dashboard(self):
        self.dashboard = OmnixDashboard()
        self.dashboard.set_active(self.ai_assistant.is_active)
        self.dashboard.set_game(self.current_game)

        # Connect to existing methods
        self.dashboard.chat_clicked.connect(self.show_chat)
        self.dashboard.settings_clicked.connect(self.show_settings)
        # ... etc

        self.dashboard.show()
```

## Future Enhancements

Potential improvements for future versions:

1. **Animations**: Smooth transitions between states
2. **Notifications**: Badge counters on buttons
3. **Themes**: Light/dark mode toggle
4. **Customization**: User-configurable layout
5. **Shortcuts**: Keyboard shortcuts for each action
6. **Mini Mode**: Compact version with fewer buttons
7. **Performance Metrics**: Live stats display
8. **Quick Actions**: Context menu on buttons

## Files

| File | Description |
|------|-------------|
| `src/ui/components/dashboard.py` | Main dashboard component |
| `src/ui/components/dashboard_button.py` | Individual action buttons |
| `test_dashboard.py` | Test script for dashboard |
| `DASHBOARD.md` | This documentation file |

## License

Part of the Omnix AI Gaming Companion project.
