"""
Omnix UI Design System Demo
=============================

Comprehensive demo showcasing all components of the Omnix UI design system.

Run this file to see a live demo of the design system:
    python src/ui/examples/demo.py
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QStackedWidget,
)
from PyQt6.QtCore import Qt

# Import design system
# Add parent directory to path for imports
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.ui import design_system, tokens, COLORS, SPACING
from src.ui.components import (
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
    OmnixHeaderBar,
    OmnixConfirmDialog,
    OmnixMessageDialog,
    OmnixInputDialog,
)
from src.ui.icons import icons


class OmnixDemoWindow(QMainWindow):
    """Main demo window showing all UI components."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Omnix UI Design System Demo")
        self.setMinimumSize(1200, 800)

        # Apply design system stylesheet
        self.setStyleSheet(design_system.generate_complete_stylesheet())

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = OmnixVBox(spacing=0, margins=(0, 0, 0, 0))
        central.setLayout(layout.layout())

        # Header
        header = OmnixHeaderBar(title="Omnix UI Design System Demo", logo_text="⬡")
        header.set_status("Demo Mode", "success")
        layout.add_widget(header)

        # Content area (sidebar + stacked widget)
        content = OmnixHBox(spacing=0, margins=(0, 0, 0, 0))

        # Sidebar
        self.sidebar = OmnixSidebar()
        self.sidebar.add_button("Buttons", "🔘", lambda: self.show_page(0))
        self.sidebar.add_button("Inputs", "📝", lambda: self.show_page(1))
        self.sidebar.add_button("Cards", "🃏", lambda: self.show_page(2))
        self.sidebar.add_button("Dialogs", "💬", lambda: self.show_page(3))
        self.sidebar.add_button("Colors", "🎨", lambda: self.show_page(4))
        content.add_widget(self.sidebar)

        # Stacked widget for pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self._create_buttons_page())
        self.pages.addWidget(self._create_inputs_page())
        self.pages.addWidget(self._create_cards_page())
        self.pages.addWidget(self._create_dialogs_page())
        self.pages.addWidget(self._create_colors_page())
        content.add_widget(self.pages)

        layout.add_widget(content)

    def show_page(self, index: int):
        """Show page at index."""
        self.pages.setCurrentIndex(index)

    def _create_buttons_page(self) -> QWidget:
        """Create buttons demo page."""
        page = OmnixVBox(spacing=SPACING.lg, margins=(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg))

        # Title
        title = QLabel("Buttons")
        title.setProperty("labelStyle", "heading")
        page.add_widget(title)

        # Primary buttons
        card = OmnixCard(title="Primary Buttons")
        hbox = OmnixHBox(spacing=SPACING.md)
        hbox.add_widget(OmnixButton("Default"))
        hbox.add_widget(OmnixButton("Primary", style="primary"))
        hbox.add_widget(OmnixButton("Secondary", style="secondary"))
        hbox.add_widget(OmnixButton("Success", style="success"))
        hbox.add_widget(OmnixButton("Danger", style="danger"))
        hbox.add_stretch()
        card.add_content(hbox)
        page.add_widget(card)

        # Icon buttons
        card = OmnixCard(title="Icon Buttons")
        hbox = OmnixHBox(spacing=SPACING.md)
        hbox.add_widget(OmnixIconButton(text="X", size=32))
        hbox.add_widget(OmnixIconButton(text="✓", size=40))
        hbox.add_widget(OmnixIconButton(text="⚙", size=48))
        hbox.add_stretch()
        card.add_content(hbox)
        page.add_widget(card)

        # Button with icons
        card = OmnixCard(title="Buttons with Icons")
        hbox = OmnixHBox(spacing=SPACING.md)
        btn1 = OmnixButton("Chat")
        btn1.setIcon(icons.get_icon("chat"))
        btn2 = OmnixButton("Settings")
        btn2.setIcon(icons.get_icon("settings"))
        btn3 = OmnixButton("Add New")
        btn3.setIcon(icons.get_icon("add"))
        hbox.add_widget(btn1)
        hbox.add_widget(btn2)
        hbox.add_widget(btn3)
        hbox.add_stretch()
        card.add_content(hbox)
        page.add_widget(card)

        page.add_stretch()
        return page

    def _create_inputs_page(self) -> QWidget:
        """Create inputs demo page."""
        page = OmnixVBox(spacing=SPACING.lg, margins=(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg))

        # Title
        title = QLabel("Input Fields")
        title.setProperty("labelStyle", "heading")
        page.add_widget(title)

        # Form
        card = OmnixCard(title="Form Inputs")
        form = OmnixFormLayout()
        form.add_row("Username:", OmnixLineEdit(placeholder="Enter username", clearable=True))
        form.add_row("Email:", OmnixLineEdit(placeholder="user@example.com", clearable=True))
        form.add_row("Password:", OmnixLineEdit(placeholder="Password", echo_mode="password"))
        form.add_row("Game:", OmnixComboBox(items=["League of Legends", "Valorant", "CS:GO"]))
        form.add_row("Description:", OmnixTextEdit(placeholder="Enter description..."))
        card.add_content(form)
        page.add_widget(card)

        page.add_stretch()
        return page

    def _create_cards_page(self) -> QWidget:
        """Create cards demo page."""
        page = OmnixVBox(spacing=SPACING.lg, margins=(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg))

        # Title
        title = QLabel("Cards & Panels")
        title.setProperty("labelStyle", "heading")
        page.add_widget(title)

        # Cards grid
        grid = OmnixGrid(spacing=SPACING.base)

        # Info cards
        card1 = OmnixInfoCard(
            title="Total Sessions",
            description="156 sessions completed",
            icon="📊"
        )
        card2 = OmnixInfoCard(
            title="Win Rate",
            description="67.3% overall",
            icon="🏆"
        )
        card3 = OmnixInfoCard(
            title="Play Time",
            description="234 hours tracked",
            icon="⏱️"
        )

        grid.add_widget(card1, 0, 0)
        grid.add_widget(card2, 0, 1)
        grid.add_widget(card3, 0, 2)

        page.add_widget(grid)

        # Regular cards
        card = OmnixCard(title="Settings Panel", hoverable=True)
        vbox = OmnixVBox()
        vbox.add_widget(QLabel("This is a hoverable card with custom content."))
        vbox.add_widget(OmnixButton("Click Me"))
        card.add_content(vbox)
        page.add_widget(card)

        page.add_stretch()
        return page

    def _create_dialogs_page(self) -> QWidget:
        """Create dialogs demo page."""
        page = OmnixVBox(spacing=SPACING.lg, margins=(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg))

        # Title
        title = QLabel("Dialogs & Modals")
        title.setProperty("labelStyle", "heading")
        page.add_widget(title)

        # Dialog buttons
        card = OmnixCard(title="Dialog Examples")
        vbox = OmnixVBox(spacing=SPACING.md)

        # Confirm dialog
        btn_confirm = OmnixButton("Show Confirmation Dialog")
        btn_confirm.clicked.connect(self._show_confirm_dialog)
        vbox.add_widget(btn_confirm)

        # Message dialog
        btn_message = OmnixButton("Show Message Dialog")
        btn_message.clicked.connect(self._show_message_dialog)
        vbox.add_widget(btn_message)

        # Input dialog
        btn_input = OmnixButton("Show Input Dialog")
        btn_input.clicked.connect(self._show_input_dialog)
        vbox.add_widget(btn_input)

        card.add_content(vbox)
        page.add_widget(card)

        page.add_stretch()
        return page

    def _create_colors_page(self) -> QWidget:
        """Create colors demo page."""
        page = OmnixVBox(spacing=SPACING.lg, margins=(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg))

        # Title
        title = QLabel("Color Palette")
        title.setProperty("labelStyle", "heading")
        page.add_widget(title)

        # Color swatches
        colors = [
            ("Primary BG", COLORS.bg_primary),
            ("Secondary BG", COLORS.bg_secondary),
            ("Accent Primary", COLORS.accent_primary),
            ("Accent Bright", COLORS.accent_primary_bright),
            ("Success", COLORS.success),
            ("Warning", COLORS.warning),
            ("Error", COLORS.error),
        ]

        grid = OmnixGrid(spacing=SPACING.base)
        for i, (name, color) in enumerate(colors):
            swatch = QWidget()
            swatch.setFixedSize(120, 80)
            swatch.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    border: 1px solid {COLORS.border_default};
                    border-radius: 8px;
                }}
            """)

            label = QLabel(f"{name}\n{color}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(f"color: {COLORS.text_primary}; font-size: 10pt;")

            grid.add_widget(swatch, i // 3, (i % 3) * 2)
            grid.add_widget(label, i // 3, (i % 3) * 2 + 1)

        page.add_widget(grid)
        page.add_stretch()
        return page

    def _show_confirm_dialog(self):
        """Show confirmation dialog."""
        dialog = OmnixConfirmDialog(
            title="Delete Profile",
            message="Are you sure you want to delete this profile? This action cannot be undone.",
            confirm_text="Delete",
            is_dangerous=True,
            parent=self
        )
        if dialog.exec():
            OmnixMessageDialog(
                title="Deleted",
                message="Profile has been deleted.",
                message_type="success",
                parent=self
            ).exec()

    def _show_message_dialog(self):
        """Show message dialog."""
        OmnixMessageDialog(
            title="Welcome!",
            message="This is a message dialog with an info icon.",
            message_type="info",
            parent=self
        ).exec()

    def _show_input_dialog(self):
        """Show input dialog."""
        dialog = OmnixInputDialog(
            title="New Profile",
            label="Enter profile name:",
            placeholder="My Gaming Profile",
            parent=self
        )
        if dialog.exec():
            name = dialog.get_value()
            OmnixMessageDialog(
                title="Profile Created",
                message=f"Profile '{name}' has been created!",
                message_type="success",
                parent=self
            ).exec()


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)

    # Set application-wide font
    from PyQt6.QtGui import QFont
    font = QFont("Roboto", 11)
    app.setFont(font)

    # Create and show demo window
    window = OmnixDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
