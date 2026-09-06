"""
License activation dialog shown on first run or when license is invalid.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from omnix.licensing import LicenseValidator


class LicenseDialog(QDialog):
    def __init__(self, validator: LicenseValidator, parent=None):
        super().__init__(parent)
        self.validator = validator
        self.setWindowTitle("OMNIX // Activate License")
        self.setFixedSize(420, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("OMNIX LICENSE ACTIVATION")
        title.setObjectName("omnix-logo-subtitle")
        layout.addWidget(title)

        info = QLabel("Enter your license key to activate Omnix.\nPurchase at omnix.gg")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.setObjectName("chat-input")
        layout.addWidget(self.key_input)

        self.status_label = QLabel("")
        self.status_label.setObjectName("stat-value")
        layout.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        activate_btn = QPushButton("ACTIVATE")
        activate_btn.setObjectName("neon-button-primary")
        activate_btn.clicked.connect(self._on_activate)
        btn_row.addWidget(activate_btn)

        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setObjectName("neon-button-secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

    def _on_activate(self) -> None:
        key = self.key_input.text().strip()
        if not key:
            self.status_label.setText("Please enter a license key.")
            return

        self.status_label.setText("Validating...")
        valid, msg = self.validator.validate(key)
        self.status_label.setText(msg)

        if valid:
            # Save the key to config/keyring
            from omnix.credential_store import CredentialStore

            store = CredentialStore()
            store.set_credential("omnix", "license_key", key)
            QMessageBox.information(self, "Activated", "License activated successfully!")
            self.accept()
