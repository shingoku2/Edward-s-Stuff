"""
BottomBar Widget
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout

from ui.tokens import SPACING
from .neon_button import NeonButton


class BottomBar(QFrame):
    """Bottom overlay bar."""

    def __init__(self, overlay_handler, settings_handler):
        super().__init__()
        self.setObjectName("BottomBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING.xl, SPACING.md, SPACING.xl, SPACING.md)
        layout.setSpacing(SPACING.lg)

        self.overlay_button = NeonButton("OVERLAY")
        self.overlay_button.setObjectName("OverlayButton")
        self.overlay_button.clicked.connect(overlay_handler)
        layout.addWidget(self.overlay_button)
        layout.addStretch()

        self.settings_button = NeonButton("SETTINGS")
        self.settings_button.setObjectName("FooterSettingsButton")
        self.settings_button.clicked.connect(settings_handler)
        layout.addWidget(self.settings_button)
