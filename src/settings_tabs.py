"""
Settings Tabs Module
Contains UI tabs for the Settings dialog
"""

import logging
from typing import Dict, Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QSlider, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QTextEdit, QScrollArea, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from keybind_manager import Keybind, KeybindManager, KeybindAction, MacroKeybind, DEFAULT_KEYBINDS
from macro_manager import Macro, MacroManager, MacroStep, MacroStepType, DEFAULT_MACROS
from theme_manager import (
    Theme, ThemeManager, ThemeMode, UIScale, LayoutMode,
    OverlayAppearance, OverlayPosition,
    DEFAULT_DARK_THEME, DEFAULT_LIGHT_THEME
)

logger = logging.getLogger(__name__)


class KeybindingsTab(QWidget):
    """Tab for managing keybindings"""

    keybinds_changed = pyqtSignal(dict)  # Emits keybinds dict

    def __init__(self, keybind_manager: KeybindManager, macro_manager: MacroManager = None, parent=None):
        super().__init__(parent)
        self.keybind_manager = keybind_manager
        self.macro_manager = macro_manager
        self.init_ui()

    def init_ui(self):
        """Initialize keybindings tab UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Configure Keybindings")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #14b8a6; padding: 10px;")
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "Assign keyboard shortcuts to actions. Use modifiers: Ctrl, Shift, Alt, Win.\n"
            "Example: ctrl+shift+g, alt+f4, ctrl+alt+delete"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #9ca3af; font-size: 10pt; padding: 5px;")
        layout.addWidget(instructions)

        # Keybinds table
        self.keybinds_table = QTableWidget()
        self.keybinds_table.setColumnCount(5)
        self.keybinds_table.setHorizontalHeaderLabels(["Action", "Description", "Keys", "System-Wide", "Enabled"])
        self.keybinds_table.horizontalHeader().setStretchLastSection(False)
        self.keybinds_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.keybinds_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.keybinds_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.keybinds_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.keybinds_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.keybinds_table.setAlternatingRowColors(True)
        layout.addWidget(self.keybinds_table)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Keybind")
        add_button.clicked.connect(self.add_keybind)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_selected_keybind)
        button_layout.addWidget(edit_button)

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected_keybind)
        button_layout.addWidget(remove_button)

        restore_button = QPushButton("Restore Defaults")
        restore_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(restore_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Conflict warning label
        self.conflict_label = QLabel("")
        self.conflict_label.setStyleSheet("color: #ef4444; font-weight: bold; padding: 5px;")
        self.conflict_label.setWordWrap(True)
        layout.addWidget(self.conflict_label)

        self.setLayout(layout)

        # Load initial keybinds
        self.load_keybinds()

    def load_keybinds(self):
        """Load keybinds into table"""
        self.keybinds_table.setRowCount(0)
        keybinds = self.keybind_manager.get_all_keybinds()

        # If no keybinds, load defaults
        if not keybinds:
            for default_keybind in DEFAULT_KEYBINDS:
                self.keybind_manager.register_keybind(default_keybind, lambda: None, override=True)
            keybinds = self.keybind_manager.get_all_keybinds()

        for keybind in keybinds:
            self.add_keybind_row(keybind)

    def add_keybind_row(self, keybind: Keybind):
        """Add a keybind row to the table"""
        row = self.keybinds_table.rowCount()
        self.keybinds_table.insertRow(row)

        # Action name
        action_item = QTableWidgetItem(keybind.action)
        action_item.setFlags(action_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.keybinds_table.setItem(row, 0, action_item)

        # Description
        desc_item = QTableWidgetItem(keybind.description)
        desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.keybinds_table.setItem(row, 1, desc_item)

        # Keys (editable)
        keys_item = QTableWidgetItem(keybind.keys)
        self.keybinds_table.setItem(row, 2, keys_item)

        # System-wide checkbox
        system_wide_item = QTableWidgetItem()
        system_wide_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        system_wide_item.setCheckState(Qt.CheckState.Checked if keybind.system_wide else Qt.CheckState.Unchecked)
        self.keybinds_table.setItem(row, 3, system_wide_item)

        # Enabled checkbox
        enabled_item = QTableWidgetItem()
        enabled_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        enabled_item.setCheckState(Qt.CheckState.Checked if keybind.enabled else Qt.CheckState.Unchecked)
        self.keybinds_table.setItem(row, 4, enabled_item)

        # Connect cell change signal
        self.keybinds_table.itemChanged.connect(self.on_keybind_changed)

    def on_keybind_changed(self, item):
        """Handle keybind table changes"""
        row = item.row()
        col = item.column()

        # Get action name
        action_item = self.keybinds_table.item(row, 0)
        if not action_item:
            return

        action = action_item.text()
        keybind = self.keybind_manager.get_keybind(action)
        if not keybind:
            return

        # Handle keys column change
        if col == 2:
            new_keys = item.text().strip()

            # Validate keys
            is_valid, error_msg = self.keybind_manager.validate_keys(new_keys)
            if not is_valid:
                self.conflict_label.setText(f"⚠ Invalid keys: {error_msg}")
                item.setBackground(QColor("#ef4444"))
                return

            # Check for conflicts
            conflicts = self.keybind_manager.get_conflicts(new_keys, action)
            if conflicts:
                conflict_names = ", ".join([k.action for k in conflicts])
                self.conflict_label.setText(f"⚠ Key combination conflicts with: {conflict_names}")
                item.setBackground(QColor("#f59e0b"))
                return

            # Update keybind
            keybind.keys = new_keys
            item.setBackground(QColor("#10b981"))
            self.conflict_label.setText("")

        # Handle system-wide checkbox
        elif col == 3:
            keybind.system_wide = (item.checkState() == Qt.CheckState.Checked)

        # Handle enabled checkbox
        elif col == 4:
            keybind.enabled = (item.checkState() == Qt.CheckState.Checked)

        # Emit changes
        self.emit_keybinds()

    def add_keybind(self):
        """Add a new keybind"""
        dialog = KeybindEditDialog(None, self.keybind_manager, self.macro_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Check if it's a macro keybind
            if dialog.is_macro_action():
                macro_keybind = dialog.get_macro_keybind()
                if macro_keybind:
                    # For now, register with a placeholder callback
                    # The actual macro execution should be wired at the application level
                    self.keybind_manager.register_macro_keybind(macro_keybind, lambda: None, override=True)
                    QMessageBox.information(
                        self,
                        "Macro Keybind Created",
                        f"Macro keybind created: {macro_keybind.keys}\n\n"
                        "Note: The macro execution will be active after saving settings and restarting."
                    )
            else:
                keybind = dialog.get_keybind()
                if keybind:
                    self.keybind_manager.register_keybind(keybind, lambda: None, override=True)
            self.load_keybinds()
            self.emit_keybinds()

    def edit_selected_keybind(self):
        """Edit the selected keybind"""
        current_row = self.keybinds_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a keybind to edit.")
            return

        action_item = self.keybinds_table.item(current_row, 0)
        if not action_item:
            return

        action = action_item.text()
        keybind = self.keybind_manager.get_keybind(action)
        if not keybind:
            return

        dialog = KeybindEditDialog(keybind, self.keybind_manager, self.macro_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Check if it's a macro keybind
            if dialog.is_macro_action():
                macro_keybind = dialog.get_macro_keybind()
                if macro_keybind:
                    self.keybind_manager.register_macro_keybind(macro_keybind, lambda: None, override=True)
                    QMessageBox.information(
                        self,
                        "Macro Keybind Updated",
                        f"Macro keybind updated: {macro_keybind.keys}\n\n"
                        "Note: The macro execution will be active after saving settings and restarting."
                    )
            else:
                updated_keybind = dialog.get_keybind()
                if updated_keybind:
                    self.keybind_manager.register_keybind(updated_keybind, lambda: None, override=True)
            self.load_keybinds()
            self.emit_keybinds()

    def remove_selected_keybind(self):
        """Remove the selected keybind"""
        current_row = self.keybinds_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a keybind to remove.")
            return

        action_item = self.keybinds_table.item(current_row, 0)
        if not action_item:
            return

        action = action_item.text()

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove the keybind for '{action}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.keybind_manager.unregister_keybind(action)
            self.load_keybinds()
            self.emit_keybinds()

    def restore_defaults(self):
        """Restore default keybinds"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore default keybindings? This will remove all custom keybinds.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear all keybinds
            for action in list(self.keybind_manager.keybinds.keys()):
                self.keybind_manager.unregister_keybind(action)

            # Load defaults
            for default_keybind in DEFAULT_KEYBINDS:
                self.keybind_manager.register_keybind(default_keybind, lambda: None, override=True)

            self.load_keybinds()
            self.emit_keybinds()
            QMessageBox.information(self, "Defaults Restored", "Default keybindings have been restored.")

    def emit_keybinds(self):
        """Emit keybinds changed signal"""
        keybinds_dict = self.keybind_manager.save_to_dict()
        self.keybinds_changed.emit(keybinds_dict)

    def get_keybinds(self) -> dict:
        """Get current keybinds as dictionary"""
        return self.keybind_manager.save_to_dict()


class KeybindEditDialog(QDialog):
    """Dialog for editing a keybind"""

    def __init__(self, keybind: Optional[Keybind], keybind_manager: KeybindManager,
                 macro_manager: MacroManager = None, parent=None):
        super().__init__(parent)
        self.keybind = keybind
        self.keybind_manager = keybind_manager
        self.macro_manager = macro_manager
        self.is_new = (keybind is None)
        self.is_macro_keybind = False  # Track if this is a macro keybind
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Edit Keybind" if not self.is_new else "Add Keybind")
        self.setModal(True)
        self.setFixedWidth(500)

        layout = QVBoxLayout()

        # Action
        action_label = QLabel("Action:")
        layout.addWidget(action_label)

        if self.is_new:
            self.action_input = QComboBox()
            # Add available actions
            self.action_input.addItem("--- Built-in Actions ---")
            for action in KeybindAction:
                self.action_input.addItem(f"  {action.value}")

            # Add macros if macro_manager is available
            if self.macro_manager:
                macros = self.macro_manager.get_all_macros()
                if macros:
                    self.action_input.addItem("--- Macros ---")
                    for macro in macros:
                        self.action_input.addItem(f"  macro:{macro.id}")

            # Set to first actual action (skip the separator)
            self.action_input.setCurrentIndex(1)
        else:
            self.action_input = QLineEdit(self.keybind.action)
            self.action_input.setReadOnly(True)

        layout.addWidget(self.action_input)

        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)

        self.desc_input = QLineEdit()
        if self.keybind:
            self.desc_input.setText(self.keybind.description)
        layout.addWidget(self.desc_input)

        # Keys
        keys_label = QLabel("Key Combination:")
        layout.addWidget(keys_label)

        self.keys_input = QLineEdit()
        if self.keybind:
            self.keys_input.setText(self.keybind.keys)
        self.keys_input.setPlaceholderText("e.g., ctrl+shift+g")
        layout.addWidget(self.keys_input)

        # System-wide
        self.system_wide_check = QCheckBox("System-wide (works outside the app)")
        if self.keybind:
            self.system_wide_check.setChecked(self.keybind.system_wide)
        layout.addWidget(self.system_wide_check)

        # Enabled
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True if not self.keybind else self.keybind.enabled)
        layout.addWidget(self.enabled_check)

        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_keybind)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_keybind(self):
        """Save the keybind"""
        if self.is_new:
            action = self.action_input.currentText().strip()
        else:
            action = self.action_input.text().strip()

        description = self.desc_input.text().strip()
        keys = self.keys_input.text().strip()
        system_wide = self.system_wide_check.isChecked()
        enabled = self.enabled_check.isChecked()

        # Validate
        if not action or action.startswith("---"):
            QMessageBox.warning(self, "Invalid Input", "Please select a valid action.")
            return

        if not description:
            QMessageBox.warning(self, "Invalid Input", "Description cannot be empty.")
            return

        if not keys:
            QMessageBox.warning(self, "Invalid Input", "Key combination cannot be empty.")
            return

        # Validate keys
        is_valid, error_msg = self.keybind_manager.validate_keys(keys)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Keys", f"Invalid key combination: {error_msg}")
            return

        # Check for conflicts (exclude current action if editing)
        conflicts = self.keybind_manager.get_conflicts(keys, action if not self.is_new else None)
        if conflicts:
            conflict_names = ", ".join([k.action for k in conflicts])
            reply = QMessageBox.question(
                self,
                "Keybind Conflict",
                f"This key combination conflicts with: {conflict_names}\n\nDo you want to override it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Check if this is a macro keybind (starts with "macro:")
        if action.startswith("macro:"):
            # Extract macro ID
            macro_id = action.replace("macro:", "").strip()

            # Verify the macro exists
            if self.macro_manager:
                macro = self.macro_manager.get_macro(macro_id)
                if not macro:
                    QMessageBox.warning(self, "Invalid Macro", f"Macro '{macro_id}' not found.")
                    return

                # Create a MacroKeybind
                self.macro_keybind = MacroKeybind(
                    macro_id=macro_id,
                    keys=keys,
                    description=description
                )
                self.is_macro_keybind = True
            else:
                QMessageBox.warning(self, "Macro Manager Missing", "Cannot create macro keybind without macro manager.")
                return
        else:
            # Create or update regular keybind
            self.keybind = Keybind(
                action=action,
                keys=keys,
                description=description,
                enabled=enabled,
                system_wide=system_wide
            )
            self.is_macro_keybind = False

        self.accept()

    def get_keybind(self) -> Optional[Keybind]:
        """Get the keybind"""
        return self.keybind

    def get_macro_keybind(self) -> Optional['MacroKeybind']:
        """Get the macro keybind if this is a macro action"""
        return getattr(self, 'macro_keybind', None)

    def is_macro_action(self) -> bool:
        """Check if the saved action is a macro"""
        return self.is_macro_keybind


class MacrosTab(QWidget):
    """Tab for managing macros"""

    macros_changed = pyqtSignal(dict)  # Emits macros dict

    def __init__(self, macro_manager: MacroManager, parent=None):
        super().__init__(parent)
        self.macro_manager = macro_manager
        self.init_ui()

    def init_ui(self):
        """Initialize macros tab UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Configure Macros")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #14b8a6; padding: 10px;")
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "Create macros to automate sequences of actions. "
            "Macros can be triggered manually or assigned to keybinds."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #9ca3af; font-size: 10pt; padding: 5px;")
        layout.addWidget(instructions)

        # Macros list
        self.macros_list = QListWidget()
        self.macros_list.itemClicked.connect(self.on_macro_selected)
        layout.addWidget(self.macros_list)

        # Buttons
        button_layout = QHBoxLayout()

        create_button = QPushButton("Create Macro")
        create_button.clicked.connect(self.create_macro)
        button_layout.addWidget(create_button)

        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_selected_macro)
        button_layout.addWidget(edit_button)

        duplicate_button = QPushButton("Duplicate")
        duplicate_button.clicked.connect(self.duplicate_selected_macro)
        button_layout.addWidget(duplicate_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected_macro)
        button_layout.addWidget(delete_button)

        restore_button = QPushButton("Load Examples")
        restore_button.clicked.connect(self.load_examples)
        button_layout.addWidget(restore_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Load initial macros
        self.load_macros()

    def load_macros(self):
        """Load macros into list"""
        self.macros_list.clear()
        macros = self.macro_manager.get_all_macros()

        # If no macros, load examples
        if not macros:
            self.load_examples(silent=True)
            macros = self.macro_manager.get_all_macros()

        for macro in macros:
            item_text = f"{macro.name} - {len(macro.steps)} steps"
            if not macro.enabled:
                item_text += " (Disabled)"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, macro.id)
            self.macros_list.addItem(item)

    def on_macro_selected(self, item):
        """Handle macro selection"""
        # Could show preview here
        pass

    def create_macro(self):
        """Create a new macro"""
        dialog = MacroEditDialog(None, self.macro_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            macro = dialog.get_macro()
            if macro:
                self.load_macros()
                self.emit_macros()

    def edit_selected_macro(self):
        """Edit the selected macro"""
        current_item = self.macros_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a macro to edit.")
            return

        macro_id = current_item.data(Qt.ItemDataRole.UserRole)
        macro = self.macro_manager.get_macro(macro_id)
        if not macro:
            return

        dialog = MacroEditDialog(macro, self.macro_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_macro = dialog.get_macro()
            if updated_macro:
                self.load_macros()
                self.emit_macros()

    def duplicate_selected_macro(self):
        """Duplicate the selected macro"""
        current_item = self.macros_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a macro to duplicate.")
            return

        macro_id = current_item.data(Qt.ItemDataRole.UserRole)
        duplicated = self.macro_manager.duplicate_macro(macro_id)
        if duplicated:
            self.load_macros()
            self.emit_macros()
            QMessageBox.information(self, "Success", f"Macro duplicated: {duplicated.name}")

    def delete_selected_macro(self):
        """Delete the selected macro"""
        current_item = self.macros_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a macro to delete.")
            return

        macro_id = current_item.data(Qt.ItemDataRole.UserRole)
        macro = self.macro_manager.get_macro(macro_id)
        if not macro:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the macro '{macro.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.macro_manager.delete_macro(macro_id)
            self.load_macros()
            self.emit_macros()

    def load_examples(self, silent=False):
        """Load example macros"""
        for example in DEFAULT_MACROS:
            macro = self.macro_manager.create_macro(
                example['name'],
                example['description']
            )
            macro.steps = example.get('steps', [])

        self.load_macros()
        self.emit_macros()

        if not silent:
            QMessageBox.information(self, "Examples Loaded", "Example macros have been loaded.")

    def emit_macros(self):
        """Emit macros changed signal"""
        macros_dict = self.macro_manager.save_to_dict()
        self.macros_changed.emit(macros_dict)

    def get_macros(self) -> dict:
        """Get current macros as dictionary"""
        return self.macro_manager.save_to_dict()


class MacroEditDialog(QDialog):
    """Dialog for editing a macro"""

    def __init__(self, macro: Optional[Macro], macro_manager: MacroManager, parent=None):
        super().__init__(parent)
        self.macro = macro
        self.macro_manager = macro_manager
        self.is_new = (macro is None)
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Edit Macro" if not self.is_new else "Create Macro")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        # Name
        name_label = QLabel("Macro Name:")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        if self.macro:
            self.name_input.setText(self.macro.name)
        layout.addWidget(self.name_input)

        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)

        self.desc_input = QLineEdit()
        if self.macro:
            self.desc_input.setText(self.macro.description)
        layout.addWidget(self.desc_input)

        # Enabled
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True if not self.macro else self.macro.enabled)
        layout.addWidget(self.enabled_check)

        # Steps list
        steps_label = QLabel("Steps:")
        layout.addWidget(steps_label)

        self.steps_list = QListWidget()
        if self.macro:
            for step in self.macro.steps:
                self.add_step_to_list(step)
        layout.addWidget(self.steps_list)

        # Step buttons
        step_button_layout = QHBoxLayout()

        add_step_button = QPushButton("Add Step")
        add_step_button.clicked.connect(self.add_step)
        step_button_layout.addWidget(add_step_button)

        remove_step_button = QPushButton("Remove Selected")
        remove_step_button.clicked.connect(self.remove_step)
        step_button_layout.addWidget(remove_step_button)

        move_up_button = QPushButton("Move Up")
        move_up_button.clicked.connect(self.move_step_up)
        step_button_layout.addWidget(move_up_button)

        move_down_button = QPushButton("Move Down")
        move_down_button.clicked.connect(self.move_step_down)
        step_button_layout.addWidget(move_down_button)

        step_button_layout.addStretch()
        layout.addLayout(step_button_layout)

        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_macro)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_step_to_list(self, step: MacroStep):
        """Add a step to the list"""
        step_text = f"{step.type}"

        # Build a description of the step based on its type
        details = []
        if step.key:
            details.append(f"key={step.key}")
        if step.button:
            details.append(f"button={step.button}")
        if step.x is not None and step.y is not None:
            details.append(f"pos=({step.x},{step.y})")
        if step.duration_ms > 0:
            details.append(f"duration={step.duration_ms}ms")
        if step.scroll_amount != 0:
            details.append(f"scroll={step.scroll_amount}")

        if details:
            step_text += f" ({', '.join(details)})"

        item = QListWidgetItem(step_text)
        item.setData(Qt.ItemDataRole.UserRole, step)
        self.steps_list.addItem(item)

    def add_step(self):
        """Add a new step"""
        dialog = MacroStepDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            step = dialog.get_step()
            if step:
                self.add_step_to_list(step)

    def remove_step(self):
        """Remove selected step"""
        current_row = self.steps_list.currentRow()
        if current_row >= 0:
            self.steps_list.takeItem(current_row)

    def move_step_up(self):
        """Move step up"""
        current_row = self.steps_list.currentRow()
        if current_row > 0:
            item = self.steps_list.takeItem(current_row)
            self.steps_list.insertItem(current_row - 1, item)
            self.steps_list.setCurrentRow(current_row - 1)

    def move_step_down(self):
        """Move step down"""
        current_row = self.steps_list.currentRow()
        if current_row < self.steps_list.count() - 1 and current_row >= 0:
            item = self.steps_list.takeItem(current_row)
            self.steps_list.insertItem(current_row + 1, item)
            self.steps_list.setCurrentRow(current_row + 1)

    def save_macro(self):
        """Save the macro"""
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        enabled = self.enabled_check.isChecked()

        # Validate
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Macro name cannot be empty.")
            return

        # Get steps
        steps = []
        for i in range(self.steps_list.count()):
            item = self.steps_list.item(i)
            step = item.data(Qt.ItemDataRole.UserRole)
            if step:
                steps.append(step)

        if not steps:
            QMessageBox.warning(self, "Invalid Input", "Macro must have at least one step.")
            return

        # Create or update macro
        if self.is_new:
            self.macro = self.macro_manager.create_macro(name, description)
        else:
            self.macro_manager.update_macro(
                self.macro.id,
                name=name,
                description=description,
                enabled=enabled
            )

        self.macro.steps = steps
        self.macro.enabled = enabled

        self.accept()

    def get_macro(self) -> Optional[Macro]:
        """Get the macro"""
        return self.macro


class MacroStepDialog(QDialog):
    """Dialog for editing a macro step"""

    def __init__(self, step: Optional[MacroStep], parent=None):
        super().__init__(parent)
        self.step = step
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Add Step" if not self.step else "Edit Step")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        # Step type
        type_label = QLabel("Step Type:")
        layout.addWidget(type_label)

        self.type_combo = QComboBox()
        for step_type in MacroStepType:
            self.type_combo.addItem(step_type.value)

        if self.step:
            index = self.type_combo.findText(self.step.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        # Parameters section
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        layout.addWidget(self.params_widget)

        # Duration (for delays)
        duration_label = QLabel("Duration (ms):")
        layout.addWidget(duration_label)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 60000)
        self.duration_input.setValue(0 if not self.step else self.step.duration_ms)
        layout.addWidget(self.duration_input)

        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_step)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Load initial parameters UI
        self.on_type_changed(self.type_combo.currentText())

    def on_type_changed(self, step_type: str):
        """Handle step type change"""
        # Clear parameters layout
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add parameter inputs based on type
        if step_type == MacroStepType.KEY_PRESS.value:
            key_label = QLabel("Key:")
            self.params_layout.addWidget(key_label)

            self.key_input = QLineEdit()
            self.key_input.setPlaceholderText("e.g., 'a', 'space', 'ctrl+shift+e'")
            if self.step and self.step.key:
                self.key_input.setText(self.step.key)
            self.params_layout.addWidget(self.key_input)

        elif step_type == MacroStepType.KEY_SEQUENCE.value:
            key_label = QLabel("Key Sequence:")
            self.params_layout.addWidget(key_label)

            self.key_input = QLineEdit()
            self.key_input.setPlaceholderText("e.g., 'hello', 'test123'")
            if self.step and self.step.key:
                self.key_input.setText(self.step.key)
            self.params_layout.addWidget(self.key_input)

        elif step_type == MacroStepType.MOUSE_CLICK.value:
            button_label = QLabel("Mouse Button:")
            self.params_layout.addWidget(button_label)

            self.button_combo = QComboBox()
            self.button_combo.addItems(["left", "right", "middle"])
            if self.step and self.step.button:
                index = self.button_combo.findText(self.step.button)
                if index >= 0:
                    self.button_combo.setCurrentIndex(index)
            self.params_layout.addWidget(self.button_combo)

        elif step_type == MacroStepType.MOUSE_MOVE.value:
            x_label = QLabel("X Position:")
            self.params_layout.addWidget(x_label)

            self.x_input = QSpinBox()
            self.x_input.setRange(0, 10000)
            if self.step and self.step.x is not None:
                self.x_input.setValue(self.step.x)
            self.params_layout.addWidget(self.x_input)

            y_label = QLabel("Y Position:")
            self.params_layout.addWidget(y_label)

            self.y_input = QSpinBox()
            self.y_input.setRange(0, 10000)
            if self.step and self.step.y is not None:
                self.y_input.setValue(self.step.y)
            self.params_layout.addWidget(self.y_input)

        elif step_type == MacroStepType.MOUSE_SCROLL.value:
            amount_label = QLabel("Scroll Amount:")
            self.params_layout.addWidget(amount_label)

            self.scroll_input = QSpinBox()
            self.scroll_input.setRange(-100, 100)
            if self.step:
                self.scroll_input.setValue(self.step.scroll_amount)
            self.params_layout.addWidget(self.scroll_input)

        elif step_type == MacroStepType.DELAY.value:
            # Duration is already shown for delays
            pass

    def save_step(self):
        """Save the step"""
        step_type = self.type_combo.currentText()
        duration_ms = self.duration_input.value()

        # Validate and extract parameters based on type
        key = None
        button = None
        x = None
        y = None
        scroll_amount = 0

        if step_type == MacroStepType.KEY_PRESS.value:
            key = self.key_input.text().strip()
            if not key:
                QMessageBox.warning(self, "Invalid Input", "Key cannot be empty.")
                return

        elif step_type == MacroStepType.KEY_SEQUENCE.value:
            key = self.key_input.text().strip()
            if not key:
                QMessageBox.warning(self, "Invalid Input", "Key sequence cannot be empty.")
                return

        elif step_type == MacroStepType.MOUSE_CLICK.value:
            button = self.button_combo.currentText()

        elif step_type == MacroStepType.MOUSE_MOVE.value:
            x = self.x_input.value()
            y = self.y_input.value()

        elif step_type == MacroStepType.MOUSE_SCROLL.value:
            scroll_amount = self.scroll_input.value()

        # Create step
        self.step = MacroStep(
            type=step_type,
            key=key,
            button=button,
            x=x,
            y=y,
            scroll_amount=scroll_amount,
            duration_ms=duration_ms
        )

        self.accept()

    def get_step(self) -> Optional[MacroStep]:
        """Get the step"""
        return self.step
