"""
Session Recap Dialog
Displays AI-powered session recap and coaching
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QTabWidget, QWidget, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from session_coaching import get_session_coach, SessionCoach
from session_logger import get_session_logger
from config import Config

logger = logging.getLogger(__name__)


class RecapWorker(QThread):
    """Worker thread for generating session recap"""

    finished = pyqtSignal(str)  # Recap text
    error = pyqtSignal(str)  # Error message

    def __init__(self, coach, game_profile_id, game_name, recap_type="session"):
        super().__init__()
        self.coach = coach
        self.game_profile_id = game_profile_id
        self.game_name = game_name
        self.recap_type = recap_type

    def run(self):
        """Generate recap in background"""
        try:
            if self.recap_type == "session":
                recap = self.coach.generate_session_recap(
                    game_profile_id=self.game_profile_id,
                    game_name=self.game_name
                )
            elif self.recap_type == "progress":
                recap = self.coach.get_progress_summary(
                    game_profile_id=self.game_profile_id,
                    game_name=self.game_name,
                    days=7
                )
            else:
                recap = "Unknown recap type"

            self.finished.emit(recap)
        except Exception as e:
            logger.error(f"Failed to generate recap: {e}", exc_info=True)
            self.error.emit(f"Failed to generate recap: {str(e)}")


class SessionRecapDialog(QDialog):
    """Dialog for displaying session recap and coaching"""

    def __init__(self, parent=None, game_profile_id=None, game_name=None, config=None):
        """
        Initialize session recap dialog

        Args:
            parent: Parent widget
            game_profile_id: Current game profile ID
            game_name: Current game display name
            config: Config instance
        """
        super().__init__(parent)
        self.game_profile_id = game_profile_id
        self.game_name = game_name or "this game"
        self.config = config or Config()

        self.coach = get_session_coach(config=self.config)
        self.session_logger = get_session_logger()

        self.setWindowTitle(f"Session Recap - {self.game_name}")
        self.setModal(False)  # Allow interaction with main window
        self.resize(700, 600)

        self.setup_ui()

        # Auto-generate session recap on open
        if self.game_profile_id:
            self.generate_session_recap()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Session Coaching - {self.game_name}")
        title_font = title.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tab widget for different recap types
        self.tab_widget = QTabWidget()

        # Session Recap Tab
        self.session_tab = QWidget()
        session_layout = QVBoxLayout()

        session_desc = QLabel("Summary of your current gaming session:")
        session_desc.setWordWrap(True)
        session_layout.addWidget(session_desc)

        self.session_text = QTextEdit()
        self.session_text.setReadOnly(True)
        self.session_text.setPlaceholderText("Generating session recap...")
        session_layout.addWidget(self.session_text)

        refresh_session_btn = QPushButton("Refresh Session Recap")
        refresh_session_btn.clicked.connect(self.generate_session_recap)
        session_layout.addWidget(refresh_session_btn)

        self.session_tab.setLayout(session_layout)
        self.tab_widget.addTab(self.session_tab, "Current Session")

        # Progress Tab
        self.progress_tab = QWidget()
        progress_layout = QVBoxLayout()

        progress_desc = QLabel("Review your progress over the past week:")
        progress_desc.setWordWrap(True)
        progress_layout.addWidget(progress_desc)

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setPlaceholderText("Click 'Generate Progress Summary' to analyze your weekly progress")
        progress_layout.addWidget(self.progress_text)

        generate_progress_btn = QPushButton("Generate Progress Summary")
        generate_progress_btn.clicked.connect(self.generate_progress_summary)
        progress_layout.addWidget(generate_progress_btn)

        self.progress_tab.setLayout(progress_layout)
        self.tab_widget.addTab(self.progress_tab, "Weekly Progress")

        # Session Stats Tab
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout()

        stats_desc = QLabel("Session statistics and activity:")
        stats_desc.setWordWrap(True)
        stats_layout.addWidget(stats_desc)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)

        refresh_stats_btn = QPushButton("Refresh Stats")
        refresh_stats_btn.clicked.connect(self.update_stats)
        stats_layout.addWidget(refresh_stats_btn)

        self.stats_tab.setLayout(stats_layout)
        self.tab_widget.addTab(self.stats_tab, "Session Stats")

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Initialize stats
        if self.game_profile_id:
            self.update_stats()

    def generate_session_recap(self):
        """Generate session recap using AI"""
        if not self.game_profile_id:
            self.session_text.setPlainText("No game profile selected")
            return

        self.session_text.setPlainText("Generating session recap with AI...\n\nThis may take a few moments.")

        # Create worker
        self.recap_worker = RecapWorker(
            coach=self.coach,
            game_profile_id=self.game_profile_id,
            game_name=self.game_name,
            recap_type="session"
        )

        # Connect signals
        self.recap_worker.finished.connect(self.on_session_recap_finished)
        self.recap_worker.error.connect(self.on_recap_error)

        # Start worker
        self.recap_worker.start()

    def generate_progress_summary(self):
        """Generate weekly progress summary"""
        if not self.game_profile_id:
            self.progress_text.setPlainText("No game profile selected")
            return

        self.progress_text.setPlainText("Generating progress summary with AI...\n\nThis may take a few moments.")

        # Create worker
        self.progress_worker = RecapWorker(
            coach=self.coach,
            game_profile_id=self.game_profile_id,
            game_name=self.game_name,
            recap_type="progress"
        )

        # Connect signals
        self.progress_worker.finished.connect(self.on_progress_recap_finished)
        self.progress_worker.error.connect(self.on_recap_error)

        # Start worker
        self.progress_worker.start()

    def on_session_recap_finished(self, recap_text):
        """Handle session recap completion"""
        self.session_text.setPlainText(recap_text)

    def on_progress_recap_finished(self, recap_text):
        """Handle progress recap completion"""
        self.progress_text.setPlainText(recap_text)

    def on_recap_error(self, error_msg):
        """Handle recap generation error"""
        self.session_text.setPlainText(f"Error: {error_msg}")

    def update_stats(self):
        """Update session statistics"""
        if not self.game_profile_id:
            self.stats_text.setPlainText("No game profile selected")
            return

        # Get session summary
        summary = self.session_logger.get_session_summary(self.game_profile_id)

        # Format stats
        stats_lines = []
        stats_lines.append("=== Current Session Statistics ===\n")
        stats_lines.append(f"Session ID: {summary['session_id']}")
        stats_lines.append(f"Started: {summary['start_time'] or 'N/A'}")
        stats_lines.append(f"Duration: {summary['duration_minutes']} minutes")
        stats_lines.append(f"Total Events: {summary['total_events']}\n")

        if summary['event_types']:
            stats_lines.append("Event Breakdown:")
            for event_type, count in summary['event_types'].items():
                stats_lines.append(f"  - {event_type.title()}: {count}")
        else:
            stats_lines.append("No events logged yet in this session.")

        self.stats_text.setPlainText("\n".join(stats_lines))
