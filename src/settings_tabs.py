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

from keybind_manager import Keybind, KeybindManager, KeybindAction, DEFAULT_KEYBINDS
from macro_manager import Macro, MacroManager, MacroAction, MacroActionType, DEFAULT_MACROS
from theme_manager import (
    Theme, ThemeManager, ThemeMode, UIScale, LayoutMode,
    OverlayAppearance, OverlayPosition,
    DEFAULT_DARK_THEME, DEFAULT_LIGHT_THEME
)

logger = logging.getLogger(__name__)


class KeybindingsTab(QWidget):
    """Tab for managing keybindings"""

    keybinds_changed = pyqtSignal(dict)  # Emits keybinds dict

    def __init__(self, keybind_manager: KeybindManager, parent=None):
        super().__init__(parent)
        self.keybind_manager = keybind_manager
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
        dialog = KeybindEditDialog(None, self.keybind_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
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

        dialog = KeybindEditDialog(keybind, self.keybind_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
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

    def __init__(self, keybind: Optional[Keybind], keybind_manager: KeybindManager, parent=None):
        super().__init__(parent)
        self.keybind = keybind
        self.keybind_manager = keybind_manager
        self.is_new = (keybind is None)
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
            for action in KeybindAction:
                self.action_input.addItem(action.value)
            self.action_input.setEditable(True)
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
        if not action:
            QMessageBox.warning(self, "Invalid Input", "Action cannot be empty.")
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

        # Create or update keybind
        self.keybind = Keybind(
            action=action,
            keys=keys,
            description=description,
            enabled=enabled,
            system_wide=system_wide
        )

        self.accept()

    def get_keybind(self) -> Optional[Keybind]:
        """Get the keybind"""
        return self.keybind


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
            item_text = f"{macro.name} - {len(macro.actions)} actions"
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
            macro.actions = example['actions']

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

        # Actions list
        actions_label = QLabel("Actions:")
        layout.addWidget(actions_label)

        self.actions_list = QListWidget()
        if self.macro:
            for action in self.macro.actions:
                self.add_action_to_list(action)
        layout.addWidget(self.actions_list)

        # Action buttons
        action_button_layout = QHBoxLayout()

        add_action_button = QPushButton("Add Action")
        add_action_button.clicked.connect(self.add_action)
        action_button_layout.addWidget(add_action_button)

        remove_action_button = QPushButton("Remove Selected")
        remove_action_button.clicked.connect(self.remove_action)
        action_button_layout.addWidget(remove_action_button)

        move_up_button = QPushButton("Move Up")
        move_up_button.clicked.connect(self.move_action_up)
        action_button_layout.addWidget(move_up_button)

        move_down_button = QPushButton("Move Down")
        move_down_button.clicked.connect(self.move_action_down)
        action_button_layout.addWidget(move_down_button)

        action_button_layout.addStretch()
        layout.addLayout(action_button_layout)

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

    def add_action_to_list(self, action: MacroAction):
        """Add an action to the list"""
        action_text = f"{action.action_type}"
        if action.parameters:
            params_str = ", ".join([f"{k}={v}" for k, v in action.parameters.items()])
            action_text += f" ({params_str})"
        if action.delay_after > 0:
            action_text += f" [delay: {action.delay_after}ms]"

        item = QListWidgetItem(action_text)
        item.setData(Qt.ItemDataRole.UserRole, action)
        self.actions_list.addItem(item)

    def add_action(self):
        """Add a new action"""
        dialog = MacroActionDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()
            if action:
                self.add_action_to_list(action)

    def remove_action(self):
        """Remove selected action"""
        current_row = self.actions_list.currentRow()
        if current_row >= 0:
            self.actions_list.takeItem(current_row)

    def move_action_up(self):
        """Move action up"""
        current_row = self.actions_list.currentRow()
        if current_row > 0:
            item = self.actions_list.takeItem(current_row)
            self.actions_list.insertItem(current_row - 1, item)
            self.actions_list.setCurrentRow(current_row - 1)

    def move_action_down(self):
        """Move action down"""
        current_row = self.actions_list.currentRow()
        if current_row < self.actions_list.count() - 1 and current_row >= 0:
            item = self.actions_list.takeItem(current_row)
            self.actions_list.insertItem(current_row + 1, item)
            self.actions_list.setCurrentRow(current_row + 1)

    def save_macro(self):
        """Save the macro"""
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        enabled = self.enabled_check.isChecked()

        # Validate
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Macro name cannot be empty.")
            return

        # Get actions
        actions = []
        for i in range(self.actions_list.count()):
            item = self.actions_list.item(i)
            action = item.data(Qt.ItemDataRole.UserRole)
            if action:
                actions.append(action)

        if not actions:
            QMessageBox.warning(self, "Invalid Input", "Macro must have at least one action.")
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

        self.macro.actions = actions
        self.macro.enabled = enabled

        self.accept()

    def get_macro(self) -> Optional[Macro]:
        """Get the macro"""
        return self.macro


class MacroActionDialog(QDialog):
    """Dialog for editing a macro action"""

    def __init__(self, action: Optional[MacroAction], parent=None):
        super().__init__(parent)
        self.action = action
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Add Action" if not self.action else "Edit Action")
        self.setModal(True)
        self.setFixedWidth(400)

        layout = QVBoxLayout()

        # Action type
        type_label = QLabel("Action Type:")
        layout.addWidget(type_label)

        self.type_combo = QComboBox()
        for action_type in MacroActionType:
            self.type_combo.addItem(action_type.value)

        if self.action:
            index = self.type_combo.findText(self.action.action_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        # Parameters section
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_widget.setLayout(self.params_layout)
        layout.addWidget(self.params_widget)

        # Delay
        delay_label = QLabel("Delay After (ms):")
        layout.addWidget(delay_label)

        self.delay_input = QSpinBox()
        self.delay_input.setRange(0, 10000)
        self.delay_input.setValue(0 if not self.action else self.action.delay_after)
        layout.addWidget(self.delay_input)

        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_action)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Load initial parameters UI
        self.on_type_changed(self.type_combo.currentText())

    def on_type_changed(self, action_type: str):
        """Handle action type change"""
        # Clear parameters layout
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add parameter inputs based on type
        if action_type == MacroActionType.SEND_MESSAGE.value:
            msg_label = QLabel("Message:")
            self.params_layout.addWidget(msg_label)

            self.message_input = QTextEdit()
            self.message_input.setMaximumHeight(100)
            if self.action and 'message' in self.action.parameters:
                self.message_input.setPlainText(self.action.parameters['message'])
            self.params_layout.addWidget(self.message_input)

        elif action_type == MacroActionType.WAIT.value:
            wait_label = QLabel("Wait Duration (ms):")
            self.params_layout.addWidget(wait_label)

            self.wait_input = QSpinBox()
            self.wait_input.setRange(0, 60000)
            self.wait_input.setValue(1000)
            if self.action and 'duration' in self.action.parameters:
                self.wait_input.setValue(self.action.parameters['duration'])
            self.params_layout.addWidget(self.wait_input)

        elif action_type == MacroActionType.CUSTOM_COMMAND.value:
            cmd_label = QLabel("Command:")
            self.params_layout.addWidget(cmd_label)

            self.command_input = QLineEdit()
            if self.action and 'command' in self.action.parameters:
                self.command_input.setText(self.action.parameters['command'])
            self.params_layout.addWidget(self.command_input)

    def save_action(self):
        """Save the action"""
        action_type = self.type_combo.currentText()
        delay_after = self.delay_input.value()
        parameters = {}

        # Get parameters based on type
        if action_type == MacroActionType.SEND_MESSAGE.value:
            message = self.message_input.toPlainText().strip()
            if not message:
                QMessageBox.warning(self, "Invalid Input", "Message cannot be empty.")
                return
            parameters['message'] = message

        elif action_type == MacroActionType.WAIT.value:
            parameters['duration'] = self.wait_input.value()

        elif action_type == MacroActionType.CUSTOM_COMMAND.value:
            command = self.command_input.text().strip()
            if not command:
                QMessageBox.warning(self, "Invalid Input", "Command cannot be empty.")
                return
            parameters['command'] = command

        # Create action
        self.action = MacroAction(
            action_type=action_type,
            parameters=parameters,
            delay_after=delay_after
        )

        self.accept()

    def get_action(self) -> Optional[MacroAction]:
        """Get the action"""
        return self.action
