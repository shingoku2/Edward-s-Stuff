"""
Knowledge Packs Tab for Settings Dialog
Allows users to create and manage knowledge packs for games
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QLineEdit, QTextEdit, QComboBox, QFileDialog,
    QMessageBox, QListWidget, QListWidgetItem, QGroupBox,
    QProgressDialog, QCheckBox, QSpinBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QFont

from knowledge_pack import KnowledgePack, KnowledgeSource
from knowledge_store import get_knowledge_pack_store
from knowledge_index import get_knowledge_index
from knowledge_ingestion import get_ingestion_pipeline, IngestionError
from game_profile import get_profile_store
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class IngestionWorker(QThread):
    """Worker thread for ingesting knowledge sources"""

    progress = pyqtSignal(int, str)  # Progress percentage and status message
    finished = pyqtSignal(bool, str)  # Success flag and message

    def __init__(self, pack, index):
        super().__init__()
        self.pack = pack
        self.index = index
        self.pipeline = get_ingestion_pipeline()

    def run(self):
        """Run ingestion in background"""
        try:
            total_sources = len(self.pack.sources)
            if total_sources == 0:
                self.finished.emit(True, "No sources to ingest")
                return

            for i, source in enumerate(self.pack.sources):
                # Update progress
                progress = int((i / total_sources) * 100)
                self.progress.emit(progress, f"Processing {source.title}...")

                # Skip if already has content
                if source.content:
                    continue

                # Ingest based on type
                try:
                    if source.type == 'file':
                        source.content = self.pipeline.ingest('file', file_path=source.path)
                    elif source.type == 'url':
                        source.content = self.pipeline.ingest('url', url=source.url)
                    # Notes already have content
                except IngestionError as e:
                    logger.error(f"Failed to ingest {source.title}: {e}")
                    source.content = f"[Ingestion failed: {str(e)}]"

            # Index the pack
            self.progress.emit(90, "Indexing knowledge pack...")
            self.index.add_pack(self.pack)

            self.progress.emit(100, "Complete!")
            self.finished.emit(True, f"Successfully indexed {total_sources} sources")

        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            self.finished.emit(False, f"Ingestion failed: {str(e)}")


class KnowledgePackDialog(QDialog):
    """Dialog for creating/editing knowledge packs"""

    def __init__(self, parent=None, pack=None, game_profiles=None):
        """
        Initialize dialog

        Args:
            parent: Parent widget
            pack: KnowledgePack to edit (None for new pack)
            game_profiles: List of available game profiles
        """
        super().__init__(parent)
        self.pack = pack
        self.game_profiles = game_profiles or []
        self.sources = pack.sources.copy() if pack else []

        self.setWindowTitle("Edit Knowledge Pack" if pack else "Create Knowledge Pack")
        self.setModal(True)
        self.resize(800, 600)

        self.setup_ui()

        # Populate if editing
        if pack:
            self.populate_fields()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout()

        # Basic info section
        info_group = QGroupBox("Pack Information")
        info_layout = QVBoxLayout()

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Elden Ring Build Guides")
        name_layout.addWidget(self.name_input)
        info_layout.addLayout(name_layout)

        # Description
        desc_label = QLabel("Description:")
        info_layout.addWidget(desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Describe what this knowledge pack contains...")
        self.desc_input.setMaximumHeight(60)
        info_layout.addWidget(self.desc_input)

        # Game profile selector
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Game Profile:"))
        self.profile_combo = QComboBox()
        for profile in self.game_profiles:
            self.profile_combo.addItem(profile.display_name, profile.id)
        profile_layout.addWidget(self.profile_combo)
        info_layout.addLayout(profile_layout)

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Enable this pack for queries")
        self.enabled_checkbox.setChecked(True)
        info_layout.addWidget(self.enabled_checkbox)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Sources section
        sources_group = QGroupBox("Knowledge Sources")
        sources_layout = QVBoxLayout()

        # Sources list
        self.sources_list = QListWidget()
        self.sources_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        sources_layout.addWidget(self.sources_list)

        # Source buttons
        source_buttons = QHBoxLayout()

        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.add_file_source)
        source_buttons.addWidget(add_file_btn)

        add_url_btn = QPushButton("Add URL")
        add_url_btn.clicked.connect(self.add_url_source)
        source_buttons.addWidget(add_url_btn)

        add_note_btn = QPushButton("Add Note")
        add_note_btn.clicked.connect(self.add_note_source)
        source_buttons.addWidget(add_note_btn)

        remove_source_btn = QPushButton("Remove Selected")
        remove_source_btn.clicked.connect(self.remove_source)
        source_buttons.addWidget(remove_source_btn)

        sources_layout.addLayout(source_buttons)
        sources_group.setLayout(sources_layout)
        layout.addWidget(sources_group)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_fields(self):
        """Populate fields when editing"""
        self.name_input.setText(self.pack.name)
        self.desc_input.setPlainText(self.pack.description)
        self.enabled_checkbox.setChecked(self.pack.enabled)

        # Select the game profile
        for i in range(self.profile_combo.count()):
            if self.profile_combo.itemData(i) == self.pack.game_profile_id:
                self.profile_combo.setCurrentIndex(i)
                break

        # Add sources to list
        self.refresh_sources_list()

    def refresh_sources_list(self):
        """Refresh the sources list widget"""
        self.sources_list.clear()
        for source in self.sources:
            type_icon = {"file": "📄", "url": "🌐", "note": "📝"}.get(source.type, "❓")
            item_text = f"{type_icon} {source.title}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, source.id)
            self.sources_list.addItem(item)

    def add_file_source(self):
        """Add a file source"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Knowledge File",
            "",
            "All Files (*);;Text Files (*.txt);;Markdown Files (*.md);;PDF Files (*.pdf)"
        )

        if file_path:
            source = KnowledgeSource(
                id=str(uuid.uuid4()),
                type="file",
                title=Path(file_path).name,
                path=file_path
            )
            self.sources.append(source)
            self.refresh_sources_list()

    def add_url_source(self):
        """Add a URL source"""
        from PyQt6.QtWidgets import QInputDialog

        url, ok = QInputDialog.getText(
            self,
            "Add URL Source",
            "Enter URL:"
        )

        if ok and url:
            # Get title
            title, ok = QInputDialog.getText(
                self,
                "Source Title",
                "Enter a title for this source:",
                text=url
            )

            if ok:
                source = KnowledgeSource(
                    id=str(uuid.uuid4()),
                    type="url",
                    title=title or url,
                    url=url
                )
                self.sources.append(source)
                self.refresh_sources_list()

    def add_note_source(self):
        """Add a note source"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Note")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout()

        # Title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        title_input = QLineEdit()
        title_layout.addWidget(title_input)
        layout.addLayout(title_layout)

        # Content
        layout.addWidget(QLabel("Content:"))
        content_input = QTextEdit()
        layout.addWidget(content_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Add")
        save_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_input.text() or "Untitled Note"
            content = content_input.toPlainText()

            if content:
                source = KnowledgeSource(
                    id=str(uuid.uuid4()),
                    type="note",
                    title=title,
                    content=content
                )
                self.sources.append(source)
                self.refresh_sources_list()

    def remove_source(self):
        """Remove selected source"""
        current_item = self.sources_list.currentItem()
        if current_item:
            source_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.sources = [s for s in self.sources if s.id != source_id]
            self.refresh_sources_list()

    def get_pack(self):
        """Get the KnowledgePack from form data"""
        pack_id = self.pack.id if self.pack else str(uuid.uuid4())
        game_profile_id = self.profile_combo.currentData()

        pack = KnowledgePack(
            id=pack_id,
            name=self.name_input.text(),
            description=self.desc_input.toPlainText(),
            game_profile_id=game_profile_id,
            sources=self.sources,
            enabled=self.enabled_checkbox.isChecked(),
            created_at=self.pack.created_at if self.pack else datetime.now(),
            updated_at=datetime.now()
        )

        return pack


class KnowledgePacksTab(QWidget):
    """Settings tab for managing knowledge packs"""

    packs_changed = pyqtSignal()  # Emitted when packs change

    def __init__(self, parent=None):
        """Initialize knowledge packs tab"""
        super().__init__(parent)
        self.store = get_knowledge_pack_store()
        self.index = get_knowledge_index()
        self.profile_store = get_profile_store()
        self.setup_ui()
        self.refresh_pack_list()

    def setup_ui(self):
        """Setup the tab UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Knowledge Packs")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        desc = QLabel(
            "Knowledge packs provide context-aware answers by attaching documents, URLs, and notes "
            "to specific games. The AI will use these sources when answering your questions."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Table of packs
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Pack Name", "Game", "Sources", "Status", "Last Updated", ""]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        create_btn = QPushButton("Create New Pack")
        create_btn.clicked.connect(self.create_pack)
        button_layout.addWidget(create_btn)

        edit_btn = QPushButton("Edit Pack")
        edit_btn.clicked.connect(self.edit_pack)
        button_layout.addWidget(edit_btn)

        reindex_btn = QPushButton("Re-index Pack")
        reindex_btn.clicked.connect(self.reindex_pack)
        button_layout.addWidget(reindex_btn)

        delete_btn = QPushButton("Delete Pack")
        delete_btn.clicked.connect(self.delete_pack)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def refresh_pack_list(self):
        """Refresh the pack table"""
        self.table.setRowCount(0)

        all_packs = self.store.load_all_packs()

        for pack in all_packs.values():
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Pack name
            name_item = QTableWidgetItem(pack.name)
            self.table.setItem(row, 0, name_item)

            # Game profile
            profile = self.profile_store.get_profile_by_id(pack.game_profile_id)
            game_name = profile.display_name if profile else pack.game_profile_id
            game_item = QTableWidgetItem(game_name)
            self.table.setItem(row, 1, game_item)

            # Sources count
            sources_item = QTableWidgetItem(str(pack.get_source_count()))
            self.table.setItem(row, 2, sources_item)

            # Status
            status = "✓ Enabled" if pack.enabled else "✗ Disabled"
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 3, status_item)

            # Last updated
            updated_str = pack.updated_at.strftime("%Y-%m-%d %H:%M")
            updated_item = QTableWidgetItem(updated_str)
            self.table.setItem(row, 4, updated_item)

            # Store pack ID in hidden column
            id_item = QTableWidgetItem(pack.id)
            self.table.setItem(row, 5, id_item)

    def create_pack(self):
        """Create a new knowledge pack"""
        game_profiles = self.profile_store.list_profiles()

        dialog = KnowledgePackDialog(
            parent=self,
            pack=None,
            game_profiles=game_profiles
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            pack = dialog.get_pack()

            # Validate
            if not pack.name:
                QMessageBox.warning(self, "Error", "Pack name is required")
                return

            # Save pack
            self.store.save_pack(pack)

            # Ingest and index in background
            self.run_ingestion(pack)

            self.refresh_pack_list()
            self.packs_changed.emit()

    def edit_pack(self):
        """Edit selected knowledge pack"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a pack to edit")
            return

        pack_id = self.table.item(current_row, 5).text()
        pack = self.store.load_pack(pack_id)

        if not pack:
            QMessageBox.warning(self, "Error", "Failed to load pack")
            return

        game_profiles = self.profile_store.list_profiles()

        dialog = KnowledgePackDialog(
            parent=self,
            pack=pack,
            game_profiles=game_profiles
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_pack = dialog.get_pack()

            # Save pack
            self.store.save_pack(updated_pack)

            # Re-index
            self.run_ingestion(updated_pack)

            self.refresh_pack_list()
            self.packs_changed.emit()

    def reindex_pack(self):
        """Re-index selected pack"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a pack to re-index")
            return

        pack_id = self.table.item(current_row, 5).text()
        pack = self.store.load_pack(pack_id)

        if not pack:
            QMessageBox.warning(self, "Error", "Failed to load pack")
            return

        # Remove old index
        self.index.remove_pack(pack_id)

        # Re-index
        self.run_ingestion(pack)

    def delete_pack(self):
        """Delete selected knowledge pack"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a pack to delete")
            return

        pack_id = self.table.item(current_row, 5).text()
        pack_name = self.table.item(current_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the pack '{pack_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from index
            self.index.remove_pack(pack_id)

            # Delete from store
            self.store.delete_pack(pack_id)

            self.refresh_pack_list()
            self.packs_changed.emit()

    def run_ingestion(self, pack):
        """Run ingestion in background with progress dialog"""
        # Create progress dialog
        progress = QProgressDialog("Ingesting knowledge sources...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)

        # Create worker
        worker = IngestionWorker(pack, self.index)

        # Connect signals
        worker.progress.connect(lambda p, msg: (progress.setValue(p), progress.setLabelText(msg)))
        worker.finished.connect(lambda success, msg: self.on_ingestion_finished(success, msg, progress))

        # Start worker
        worker.start()
        self.ingestion_worker = worker  # Keep reference

    def on_ingestion_finished(self, success, message, progress_dialog):
        """Handle ingestion completion"""
        progress_dialog.close()

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Ingestion Failed", message)
