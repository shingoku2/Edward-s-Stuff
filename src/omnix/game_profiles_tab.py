"""
Game Profiles Settings Tab
Provides UI for managing game profiles in Settings dialog
"""

import logging
from typing import Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from omnix.game_profile import GameProfile, get_profile_store
from omnix.providers_tab import FetchModelsThread

logger = logging.getLogger(__name__)


class GameProfileDialog(QDialog):
    """Dialog for creating/editing game profiles"""

    def __init__(
        self,
        parent=None,
        profile: Optional[GameProfile] = None,
        available_providers: Optional[list] = None,
        ollama_host: Optional[str] = None,
    ):
        """
        Initialize profile dialog.

        Args:
            parent: Parent widget
            profile: Existing profile to edit, or None for new profile
            available_providers: List of available AI providers
            ollama_host: Ollama base URL, used to fetch installed models
        """
        super().__init__(parent)
        self.profile = profile
        self.available_providers = available_providers or ["ollama"]
        self.ollama_host = ollama_host or "http://localhost:11434"
        self.fetch_thread: Optional[FetchModelsThread] = None
        self.setWindowTitle(f"{'Edit' if profile else 'Create'} Game Profile")
        self.setMinimumWidth(600)
        self.setup_ui()
        self.refresh_models()

    def setup_ui(self) -> None:
        """Setup the dialog UI"""
        layout = QVBoxLayout()

        # Display name
        layout.addWidget(QLabel("Display Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Elden Ring")
        if self.profile:
            self.name_input.setText(self.profile.display_name)
        layout.addWidget(self.name_input)

        # ID (disabled for existing profiles)
        layout.addWidget(QLabel("Profile ID:"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g., elden_ring (auto-generated if left blank)")
        if self.profile:
            self.id_input.setText(self.profile.id)
            self.id_input.setReadOnly(True)
        layout.addWidget(self.id_input)

        # Executable names
        layout.addWidget(QLabel("Executable Names (one per line):"))
        self.exe_input = QTextEdit()
        self.exe_input.setPlaceholderText("e.g.:\neldenring.exe\nelden ring.exe")
        self.exe_input.setMaximumHeight(80)
        if self.profile:
            self.exe_input.setText("\n".join(self.profile.exe_names))
        layout.addWidget(self.exe_input)

        # System prompt
        layout.addWidget(QLabel("System Prompt (AI Behavior):"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Describe how the AI should behave for this game. "
            "E.g., 'You are an Elden Ring expert. Help with boss strategies and build optimization.'"
        )
        self.prompt_input.setMinimumHeight(120)
        if self.profile:
            self.prompt_input.setText(self.profile.system_prompt)
        layout.addWidget(self.prompt_input)

        # Provider selection
        layout.addWidget(QLabel("Default AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(self.available_providers)
        if self.profile:
            idx = self.provider_combo.findText(self.profile.default_provider)
            if idx >= 0:
                self.provider_combo.setCurrentIndex(idx)
        layout.addWidget(self.provider_combo)

        # Model (optional)
        layout.addWidget(QLabel("Model (optional, provider-specific):"))
        model_row = QHBoxLayout()
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        model_line_edit = self.model_input.lineEdit()
        if model_line_edit is not None:
            model_line_edit.setPlaceholderText("e.g., llama3")
        if self.profile and self.profile.default_model:
            self.model_input.addItem(self.profile.default_model)
            self.model_input.setCurrentText(self.profile.default_model)
        model_row.addWidget(self.model_input, stretch=1)

        self.refresh_models_btn = QPushButton("🔄 Refresh")
        self.refresh_models_btn.clicked.connect(self.refresh_models)
        model_row.addWidget(self.refresh_models_btn)

        layout.addLayout(model_row)

        # Overlay mode
        layout.addWidget(QLabel("Default Overlay Mode:"))
        self.overlay_mode_combo = QComboBox()
        self.overlay_mode_combo.addItems(["compact", "full"])
        if self.profile:
            idx = self.overlay_mode_combo.findText(self.profile.overlay_mode_default)
            if idx >= 0:
                self.overlay_mode_combo.setCurrentIndex(idx)
        layout.addWidget(self.overlay_mode_combo)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_profile(self) -> Optional[GameProfile]:
        """Extract profile data from dialog"""
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Display name is required")
            return None

        if not self.prompt_input.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "System prompt is required")
            return None

        exe_names = [
            line.strip() for line in self.exe_input.toPlainText().split("\n") if line.strip()
        ]

        # Generate ID if new profile
        if not self.profile:
            profile_id = self.id_input.text().strip()
            if not profile_id:
                # Auto-generate from display name
                profile_id = self.name_input.text().lower().replace(" ", "_").replace("-", "_")
        else:
            profile_id = self.profile.id

        return GameProfile(
            id=profile_id,
            display_name=self.name_input.text().strip(),
            exe_names=exe_names,
            system_prompt=self.prompt_input.toPlainText().strip(),
            default_provider=self.provider_combo.currentText(),
            default_model=self.model_input.currentText().strip() or None,
            overlay_mode_default=self.overlay_mode_combo.currentText(),
        )

    def refresh_models(self) -> None:
        """Fetch installed Ollama models to populate the model dropdown"""
        if self.fetch_thread and self.fetch_thread.isRunning():
            return

        self.refresh_models_btn.setEnabled(False)
        self.fetch_thread = FetchModelsThread(self.ollama_host)
        self.fetch_thread.models_fetched.connect(self.on_models_fetched)
        self.fetch_thread.fetch_failed.connect(self.on_models_fetch_failed)
        self.fetch_thread.finished.connect(lambda: self.refresh_models_btn.setEnabled(True))
        self.fetch_thread.start()

    def on_models_fetched(self, models: list) -> None:
        """Handle successful model fetch"""
        current = self.model_input.currentText()
        self.model_input.clear()
        if models:
            self.model_input.addItems(models)
        if current:
            self.model_input.setCurrentText(current)

    def on_models_fetch_failed(self, error: str) -> None:
        """Handle model fetch failure"""
        logger.warning(f"Failed to fetch models for game profile dialog: {error}")

    def closeEvent(self, event) -> None:
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait(1000)
        super().closeEvent(event)


class GameProfilesTab(QWidget):
    """Settings tab for managing game profiles"""

    profile_changed = pyqtSignal()  # Emitted when profiles change

    def __init__(
        self,
        parent=None,
        available_providers: Optional[list] = None,
        ollama_host: Optional[str] = None,
    ):
        """
        Initialize game profiles tab.

        Args:
            parent: Parent widget
            available_providers: List of available AI providers
            ollama_host: Ollama base URL, used to fetch installed models
        """
        super().__init__(parent)
        self.store = get_profile_store()
        self.available_providers = available_providers or ["ollama"]
        self.ollama_host = ollama_host or "http://localhost:11434"
        self.setup_ui()
        self.refresh_profile_list()

    def setup_ui(self) -> None:
        """Setup the tab UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Game Profiles")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        desc = QLabel(
            "Manage AI profiles for different games. Each profile can have custom prompts, "
            "AI providers, and overlay modes. Built-in profiles are shown but cannot be edited."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Table of profiles
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Game Name", "Executables", "Provider", "Mode", "Type"]
        )
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        create_btn = QPushButton("Create New Profile")
        create_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(create_btn)

        edit_btn = QPushButton("Edit Profile")
        edit_btn.clicked.connect(self.edit_profile)
        button_layout.addWidget(edit_btn)

        duplicate_btn = QPushButton("Duplicate Profile")
        duplicate_btn.clicked.connect(self.duplicate_profile)
        button_layout.addWidget(duplicate_btn)

        delete_btn = QPushButton("Delete Profile")
        delete_btn.clicked.connect(self.delete_profile)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def refresh_profile_list(self) -> None:
        """Refresh the profile table"""
        self.table.setRowCount(0)

        for profile in self.store.list_profiles():
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Game name
            name_item = QTableWidgetItem(profile.display_name)
            self.table.setItem(row, 0, name_item)

            # Executables
            exe_text = ", ".join(profile.exe_names) if profile.exe_names else "(any)"
            exe_item = QTableWidgetItem(exe_text)
            self.table.setItem(row, 1, exe_item)

            # Provider
            provider_item = QTableWidgetItem(profile.default_provider)
            self.table.setItem(row, 2, provider_item)

            # Overlay mode
            mode_item = QTableWidgetItem(profile.overlay_mode_default)
            self.table.setItem(row, 3, mode_item)

            # Type (built-in or custom)
            type_text = "Built-in" if profile.is_builtin else "Custom"
            type_item = QTableWidgetItem(type_text)
            self.table.setItem(row, 4, type_item)

    def create_profile(self) -> None:
        """Create a new profile"""
        dialog = GameProfileDialog(
            self,
            available_providers=self.available_providers,
            ollama_host=self.ollama_host,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            profile = dialog.get_profile()
            if profile:
                if self.store.create_profile(profile):
                    QMessageBox.information(
                        self, "Success", f"Profile '{profile.display_name}' created"
                    )
                    self.refresh_profile_list()
                    self.profile_changed.emit()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to create profile. ID '{profile.id}' may already exist.",
                    )

    def edit_profile(self) -> None:
        """Edit the selected profile"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a profile to edit")
            return

        profiles = self.store.list_profiles()
        profile = profiles[current_row]

        # Cannot edit built-in profiles
        if profile.is_builtin:
            QMessageBox.information(
                self,
                "Built-in Profile",
                "Built-in profiles cannot be edited. You can duplicate and customize instead.",
            )
            return

        dialog = GameProfileDialog(
            self,
            profile=profile,
            available_providers=self.available_providers,
            ollama_host=self.ollama_host,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_profile()
            if updated:
                if self.store.update_profile(updated):
                    QMessageBox.information(
                        self, "Success", f"Profile '{updated.display_name}' updated"
                    )
                    self.refresh_profile_list()
                    self.profile_changed.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update profile")

    def duplicate_profile(self) -> None:
        """Duplicate the selected profile"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a profile to duplicate")
            return

        profiles = self.store.list_profiles()
        profile = profiles[current_row]

        # Create a copy dialog
        dialog = GameProfileDialog(
            self,
            profile=None,  # New profile
            available_providers=self.available_providers,
            ollama_host=self.ollama_host,
        )

        # Pre-fill with data from original
        dialog.name_input.setText(f"{profile.display_name} (Copy)")
        dialog.exe_input.setText("\n".join(profile.exe_names))
        dialog.prompt_input.setText(profile.system_prompt)
        dialog.provider_combo.setCurrentText(profile.default_provider)
        if profile.default_model:
            dialog.model_input.setCurrentText(profile.default_model)
        dialog.overlay_mode_combo.setCurrentText(profile.overlay_mode_default)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_profile = dialog.get_profile()
            if new_profile:
                if self.store.create_profile(new_profile):
                    QMessageBox.information(
                        self, "Success", f"Profile '{new_profile.display_name}' created as copy"
                    )
                    self.refresh_profile_list()
                    self.profile_changed.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create duplicate profile")

    def delete_profile(self) -> None:
        """Delete the selected profile"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a profile to delete")
            return

        profiles = self.store.list_profiles()
        profile = profiles[current_row]

        # Cannot delete built-in profiles
        if profile.is_builtin:
            QMessageBox.information(
                self, "Built-in Profile", "Built-in profiles cannot be deleted."
            )
            return

        if (
            QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete '{profile.display_name}'?\n\nThis cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            if self.store.delete_profile(profile.id):
                QMessageBox.information(
                    self, "Deleted", f"Profile '{profile.display_name}' deleted"
                )
                self.refresh_profile_list()
                self.profile_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete profile")
