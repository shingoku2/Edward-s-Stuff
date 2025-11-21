"""
Panel Widgets
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.tokens import SPACING
from .hex_status import HexStatusWidget
from .neon_button import NeonButton, NeonToggle
from .neon_card import NeonCard


class GameStatusPanel(NeonCard):
    """Central game status module with hex display and stats."""

    def __init__(self):
        super().__init__()
        self.setObjectName("GameStatusPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING.xl, SPACING.xl, SPACING.xl, SPACING.xl)
        layout.setSpacing(SPACING.lg)

        title = QLabel("GAME DETECTED")
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.hex_widget = HexStatusWidget()
        layout.addWidget(self.hex_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        status_row = QHBoxLayout()
        status_row.setSpacing(SPACING.sm)
        indicator = QFrame()
        indicator.setObjectName("StatusIndicator")
        indicator.setFixedSize(14, 14)
        status_label = QLabel("ONLINE")
        status_label.setObjectName("StatusText")
        status_row.addStretch()
        status_row.addWidget(indicator)
        status_row.addWidget(status_label)
        status_row.addStretch()
        layout.addLayout(status_row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(SPACING.lg)
        stats_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for label, value in [("K/D", "1.52"), ("MATCH", "24"), ("WINS", "152")]:
            stat = self._build_stat(label, value)
            stats_row.addWidget(stat)
        layout.addLayout(stats_row)

    def _build_stat(self, label: str, value: str) -> QWidget:
        container = QFrame()
        container.setObjectName("StatContainer")
        stat_layout = QVBoxLayout(container)
        stat_layout.setContentsMargins(12, 6, 12, 6)
        stat_layout.setSpacing(4)
        label_widget = QLabel(label)
        label_widget.setObjectName("StatLabel")
        value_widget = QLabel(value)
        value_widget.setObjectName("StatValue")
        stat_layout.addWidget(label_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        stat_layout.addWidget(value_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        return container


class SettingsPanel(NeonCard):
    """Settings chip panel."""

    def __init__(self):
        super().__init__()
        self.setObjectName("SettingsPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING.xl, SPACING.xl, SPACING.xl, SPACING.xl)
        layout.setSpacing(SPACING.md)

        title = QLabel("SETTINGS")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        chips_layout = QVBoxLayout()
        chips_layout.setSpacing(SPACING.sm)
        for text in ["Overlay Mode", "General", "Notifications", "Privacy"]:
            toggle = NeonToggle(text)
            toggle.setObjectName("SettingToggle")
            chips_layout.addWidget(toggle)
        layout.addLayout(chips_layout)


class AIProviderPanel(NeonCard):
    """AI provider selection panel."""

    def __init__(self):
        super().__init__()
        self.setObjectName("AIProviderPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING.xl, SPACING.xl, SPACING.xl, SPACING.xl)
        layout.setSpacing(SPACING.lg)

        title = QLabel("AI PROVIDER")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(SPACING.md)

        self.synapse_btn = NeonButton("SYNAPSE")
        self.synapse_btn.setProperty("variant", "provider")
        self.synapse_btn.setCheckable(True)
        self.synapse_btn.setChecked(True)
        buttons_layout.addWidget(self.synapse_btn)

        self.hybridnex_btn = NeonButton("HYBRIDNEX")
        self.hybridnex_btn.setProperty("variant", "provider")
        self.hybridnex_btn.setCheckable(True)
        buttons_layout.addWidget(self.hybridnex_btn)

        self.synapse_btn.clicked.connect(lambda: self._select_provider(self.synapse_btn))
        self.hybridnex_btn.clicked.connect(lambda: self._select_provider(self.hybridnex_btn))

        layout.addLayout(buttons_layout)

    def _select_provider(self, btn: NeonButton):
        for candidate in [self.synapse_btn, self.hybridnex_btn]:
            candidate.setChecked(candidate is btn)
            candidate.setProperty("active", "true" if candidate.isChecked() else "false")
            candidate.style().unpolish(candidate)
            candidate.style().polish(candidate)
