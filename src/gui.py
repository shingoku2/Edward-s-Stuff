"""
Omnix GUI Module
================

PyQt6 interface styled with the Omnix QSS theme. Pure native PyQt6 — no QWebEngineView.
Provides the main dashboard, chat panel, and in-game overlay window.
"""

from __future__ import annotations

import html
import logging
import sys
from pathlib import Path
from typing import Dict, Optional
import psutil

from PyQt6.QtCore import QEvent, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.config import Config
from src.credential_store import CredentialStore
from src.ui.design_system import OmnixDesignSystem, design_system
from src.keybind_manager import KeybindManager
from src.macro_manager import MacroManager
from src.ui.theme_manager import OmnixThemeManager
from src.settings_dialog import TabbedSettingsDialog
from src.omnix_hud import (
    NeonButton,
    ChatPanel,
    GameStatusWidget,
    StatBlock,
    OMNIX_GLOBAL_QSS,
)

logger = logging.getLogger(__name__)


class AIWorkerThread(QThread):
    """Background worker that calls the AI assistant without blocking the UI."""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, assistant, question: str, game_context: Optional[Dict] = None):
        super().__init__()
        self.assistant = assistant
        self.question = question
        self.game_context = game_context or {}

    def run(self) -> None:
        try:
            if self.assistant is None:
                response = "Omnix is standing by. Configure an AI provider to begin."
            else:
                response = self.assistant.ask_question(
                    self.question, game_context=self.game_context
                )
            self.finished.emit(response or "")
        except Exception as exc:
            logger.exception("AI worker failed")
            self.error.emit(str(exc))


class OverlayWindow(QWidget):
    """
    Frameless always-on-top in-game overlay — pure PyQt6, no WebEngine.
    Draggable, resizable, minimizable. Saves position/size to config.
    """

    def __init__(self, assistant, config: Config, ds: OmnixDesignSystem):
        super().__init__()
        self.assistant = assistant
        self.config = config
        self.design_system = ds
        self.ai_worker: Optional[AIWorkerThread] = None
        self._drag_pos = None
        self._minimized = bool(getattr(config, "overlay_minimized", False))
        self._saved_height = int(getattr(config, "overlay_height", 420))

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setGeometry(
            int(getattr(config, "overlay_x", 100)),
            int(getattr(config, "overlay_y", 100)),
            int(getattr(config, "overlay_width", 420)),
            self._saved_height,
        )
        self.setStyleSheet(ds.get_overlay_stylesheet(
            float(getattr(config, "overlay_opacity", 0.92))
        ))

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Outer frame (gives the frosted-glass border look)
        self._frame = QFrame()
        self._frame.setObjectName("overlay-frame")
        frame_layout = QVBoxLayout(self._frame)
        frame_layout.setContentsMargins(10, 6, 10, 10)
        frame_layout.setSpacing(6)

        # Title bar
        title_bar = self._build_title_bar()
        frame_layout.addLayout(title_bar)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chat-display")
        self.chat_display.setReadOnly(True)
        self.chat_display.setAcceptRichText(True)
        self.chat_display.setMinimumHeight(160)
        frame_layout.addWidget(self.chat_display, 1)

        # Input row
        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("chat-input")
        self.chat_input.setPlaceholderText("Ask OMNIX...")
        self.chat_input.returnPressed.connect(self._on_send)
        input_row.addWidget(self.chat_input, 1)

        send_btn = QPushButton("▶")
        send_btn.setFixedWidth(36)
        send_btn.clicked.connect(self._on_send)
        input_row.addWidget(send_btn)

        frame_layout.addLayout(input_row)
        root.addWidget(self._frame)

        # Save timer (debounced position/size save)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_geometry)

        if self._minimized:
            self._apply_minimized_state()

    def _build_title_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)

        logo = QLabel("OMNIX //")
        logo.setObjectName("omnix-logo-subtitle")
        bar.addWidget(logo)
        bar.addStretch()

        min_btn = QPushButton("─")
        min_btn.setFixedSize(22, 22)
        min_btn.setToolTip("Minimize overlay")
        min_btn.clicked.connect(self.toggle_minimize)
        bar.addWidget(min_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setToolTip("Hide overlay")
        close_btn.clicked.connect(self.hide)
        bar.addWidget(close_btn)

        return bar

    def toggle_minimize(self) -> None:
        self._minimized = not self._minimized
        self.config.overlay_minimized = self._minimized
        if self._minimized:
            self._saved_height = self.height()
            self._apply_minimized_state()
        else:
            self.chat_display.setVisible(True)
            self.chat_input.setVisible(True)
            self.setFixedHeight(self._saved_height)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)

    def _apply_minimized_state(self) -> None:
        self.chat_display.setVisible(False)
        self.chat_input.setVisible(False)
        self.setFixedHeight(40)

    def _on_send(self) -> None:
        text = self.chat_input.text().strip()
        if not text or self.ai_worker is not None:
            return
        self.chat_input.clear()
        self._append_chat("YOU", text, is_user=True)
        self.ai_worker = AIWorkerThread(self.assistant, text)
        self.ai_worker.finished.connect(self._on_response)
        self.ai_worker.error.connect(self._on_error)
        self.ai_worker.start()

    def _on_response(self, response: str) -> None:
        self._append_chat("OMNIX", response, is_user=False)
        self.ai_worker = None

    def _on_error(self, msg: str) -> None:
        self._append_chat("OMNIX", f"[ERROR] {msg}", is_user=False)
        self.ai_worker = None

    def _append_chat(self, sender: str, text: str, is_user: bool) -> None:
        color = "#ec4899" if is_user else "#22d3ee"
        safe_sender = html.escape(sender)
        safe_text = html.escape(text).replace("\n", "<br/>")
        chat_html = (
            f'<p style="margin:2px 0;">'
            f'<span style="color:{color};font-size:8px;letter-spacing:2px;">{safe_sender}</span><br/>'
            f'<span style="color:#e5e7eb;font-size:11px;">{safe_text}</span>'
            f'</p>'
        )
        self.chat_display.append(chat_html)
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    # Drag-to-move
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._save_timer.start(400)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self._save_timer.start(400)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._save_timer.start(400)

    def _save_geometry(self) -> None:
        try:
            self.config.overlay_x = self.x()
            self.config.overlay_y = self.y()
            self.config.overlay_width = self.width()
            self.config.overlay_height = self.height()
            self.config.save()
        except Exception as e:
            logger.warning(f"Failed to save overlay geometry: {e}")

    def closeEvent(self, event) -> None:
        self._save_geometry()
        super().closeEvent(event)


class MainWindow(QMainWindow):
    """
    Omnix main dashboard — pure PyQt6, no QWebEngineView.
    Layout: Header | [Chat Panel | Game Status | Stats/Settings] | Footer
    """

    def __init__(
        self,
        ai_assistant,
        config: Config,
        credential_store: CredentialStore,
        design_system: OmnixDesignSystem = design_system,
        game_detector=None,
    ):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.config = config
        self.credential_store = credential_store
        self.design_system = design_system or OmnixDesignSystem()
        self.game_detector = game_detector
        self.current_game: Optional[Dict] = None
        self.ai_worker: Optional[AIWorkerThread] = None

        self.setWindowTitle("OMNIX // HUD")
        self.resize(1280, 800)
        self.setMinimumSize(960, 640)
        self.setStyleSheet(OMNIX_GLOBAL_QSS)

        self.keybind_manager = KeybindManager()
        self.macro_manager = MacroManager()
        self.theme_manager = OmnixThemeManager()
        self.settings_dialog = None

        # Build overlay (native PyQt6 — no WebEngine)
        self.overlay_window = OverlayWindow(ai_assistant, config, self.design_system)

        # Central widget container
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        header = self._build_header()
        root_layout.addLayout(header)

        # ── Body (3-column grid) ─────────────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(12, 8, 12, 8)
        body.setSpacing(12)

        # Column 1 — Chat (flex: 3)
        self.chat_panel = self._build_chat_panel()
        body.addWidget(self.chat_panel, 3)

        # Column 2 — Game status + session (flex: 4)
        self.game_panel = self._build_game_panel()
        body.addWidget(self.game_panel, 4)

        # Column 3 — Stats + quick settings (flex: 3)
        right_column = QVBoxLayout()
        right_column.setSpacing(8)
        self.stats_panel = self._build_stats_panel()
        self.quick_settings_panel = self._build_quick_settings_panel()
        right_column.addWidget(self.stats_panel, 2)
        right_column.addWidget(self.quick_settings_panel, 3)
        right_wrapper = QWidget()
        right_wrapper.setLayout(right_column)
        body.addWidget(right_wrapper, 3)

        root_layout.addLayout(body, 1)

        # ── Footer ───────────────────────────────────────────────────────────
        footer = self._build_footer()
        root_layout.addLayout(footer)

        # ── Timers ───────────────────────────────────────────────────────────
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_system_stats)
        self.stats_timer.start(1000)

        if self.game_detector:
            self._start_game_detection()

    # ── PANEL BUILDERS ────────────────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        frame = QFrame()
        frame.setObjectName("top-bar")
        frame.setFixedHeight(54)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        h = QHBoxLayout(frame)
        h.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("OMNIX")
        logo.setObjectName("omnix-logo")
        h.addWidget(logo)

        sub = QLabel("// ALL-KNOWING GAMING COMPANION")
        sub.setObjectName("omnix-logo-subtitle")
        sub.setContentsMargins(10, 6, 0, 0)
        h.addWidget(sub)

        h.addStretch()

        self.game_status_label = QLabel("NO GAME DETECTED")
        self.game_status_label.setObjectName("top-bar-user")
        h.addWidget(self.game_status_label)

        layout.addWidget(frame)
        return layout

    def _build_chat_panel(self) -> QFrame:
        """Left column: chat history + input."""
        panel = QFrame()
        panel.setObjectName("hud-panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("CHAT")
        title.setObjectName("panel-title")
        layout.addWidget(title)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chat-display")
        self.chat_display.setReadOnly(True)
        self.chat_display.setAcceptRichText(True)
        layout.addWidget(self.chat_display, 1)

        # Input row
        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("chat-input")
        self.chat_input.setPlaceholderText("Ask OMNIX anything...")
        self.chat_input.returnPressed.connect(self._on_send_clicked)
        input_row.addWidget(self.chat_input, 1)

        send_btn = QPushButton("SEND")
        send_btn.setObjectName("neon-button-primary")
        send_btn.setFixedWidth(72)
        send_btn.clicked.connect(self._on_send_clicked)
        input_row.addWidget(send_btn)

        layout.addLayout(input_row)
        return panel

    def _build_game_panel(self) -> QFrame:
        """Center column: detected game info + session."""
        panel = QFrame()
        panel.setObjectName("hud-panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("GAME INTELLIGENCE")
        title.setObjectName("panel-title")
        layout.addWidget(title)

        self.game_name_label = QLabel("── STANDBY ──")
        self.game_name_label.setObjectName("game-name-label")
        self.game_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.game_name_label)

        self.game_info_label = QLabel("Launch a game to begin session tracking.")
        self.game_info_label.setObjectName("game-info-label")
        self.game_info_label.setWordWrap(True)
        self.game_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.game_info_label)

        layout.addStretch()

        session_title = QLabel("SESSION")
        session_title.setObjectName("panel-title")
        layout.addWidget(session_title)

        self.session_label = QLabel("No active session.")
        self.session_label.setObjectName("game-info-label")
        self.session_label.setWordWrap(True)
        layout.addWidget(self.session_label)

        return panel

    def _build_stats_panel(self) -> QFrame:
        """Top-right: CPU / RAM live stats."""
        panel = QFrame()
        panel.setObjectName("hud-panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QLabel("SYSTEM TELEMETRY")
        title.setObjectName("panel-title")
        layout.addWidget(title)

        self.cpu_label = QLabel("CPU: ---%")
        self.cpu_label.setObjectName("stat-value")
        layout.addWidget(self.cpu_label)

        self.ram_label = QLabel("RAM: ---%")
        self.ram_label.setObjectName("stat-value")
        layout.addWidget(self.ram_label)

        self.ai_status_label = QLabel("AI: IDLE")
        self.ai_status_label.setObjectName("stat-value")
        layout.addWidget(self.ai_status_label)

        return panel

    def _build_quick_settings_panel(self) -> QFrame:
        """Bottom-right: quick access settings."""
        panel = QFrame()
        panel.setObjectName("hud-panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("QUICK SETTINGS")
        title.setObjectName("panel-title")
        layout.addWidget(title)

        model_label = QLabel("AI Model")
        model_label.setObjectName("stat-label")
        layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.setObjectName("omnix-combo")
        self.model_combo.addItem(getattr(self.config, "ollama_model", "llama3"))
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        layout.addWidget(self.model_combo)

        layout.addStretch()

        macro_btn = QPushButton("MACRO MANAGER")
        macro_btn.setObjectName("neon-button-secondary")
        macro_btn.clicked.connect(self._open_macro_manager)
        layout.addWidget(macro_btn)

        knowledge_btn = QPushButton("KNOWLEDGE BASE")
        knowledge_btn.setObjectName("neon-button-secondary")
        knowledge_btn.clicked.connect(self._open_knowledge_manager)
        layout.addWidget(knowledge_btn)

        return panel

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setContentsMargins(12, 6, 12, 10)
        footer.setSpacing(12)

        overlay_btn = QPushButton("TOGGLE OVERLAY")
        overlay_btn.setObjectName("neon-button-primary")
        overlay_btn.setMinimumHeight(44)
        overlay_btn.clicked.connect(self._toggle_overlay)
        footer.addWidget(overlay_btn, 1)

        settings_btn = QPushButton("SYSTEM SETTINGS")
        settings_btn.setObjectName("neon-button-secondary")
        settings_btn.setMinimumHeight(44)
        settings_btn.clicked.connect(self._open_settings)
        footer.addWidget(settings_btn, 1)

        return footer

    # ── SLOT HANDLERS ─────────────────────────────────────────────────────────

    def _on_send_clicked(self) -> None:
        text = self.chat_input.text().strip()
        if not text or self.ai_worker is not None:
            return
        self.chat_input.clear()
        self._append_chat("YOU", text, is_user=True)
        self.ai_status_label.setText("AI: THINKING...")
        game_context = self.current_game or {}
        self.ai_worker = AIWorkerThread(self.ai_assistant, text, game_context)
        self.ai_worker.finished.connect(self._handle_response)
        self.ai_worker.error.connect(self._handle_error)
        self.ai_worker.start()

    def _handle_response(self, response: str) -> None:
        self._append_chat("OMNIX", response, is_user=False)
        self.ai_status_label.setText("AI: IDLE")
        self.ai_worker = None

    def _handle_error(self, message: str) -> None:
        self._append_chat("OMNIX", f"[ERROR] {message}", is_user=False)
        self.ai_status_label.setText("AI: ERROR")
        self.ai_worker = None

    def _append_chat(self, sender: str, text: str, is_user: bool) -> None:
        color = "#ec4899" if is_user else "#22d3ee"
        safe_sender = html.escape(sender)
        safe_text = html.escape(text).replace("\n", "<br/>")
        chat_html = (
            f'<p style="margin:4px 0;">'
            f'<span style="color:{color};font-size:9px;letter-spacing:2px;'
            f'text-transform:uppercase;">{safe_sender}</span><br/>'
            f'<span style="color:#e5e7eb;font-size:12px;">{safe_text}</span>'
            f'</p><hr style="border:none;border-top:1px solid #1e293b;"/>'
        )
        self.chat_display.append(chat_html)
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _update_system_stats(self) -> None:
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
            self.ram_label.setText(f"RAM: {ram:.1f}%")
        except Exception as e:
            logger.error(f"Stats update error: {e}")

    def _start_game_detection(self) -> None:
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self._check_game)
        self.game_timer.start(5000)

    def _check_game(self) -> None:
        try:
            if self.game_detector:
                detected = self.game_detector.detect_game()
                if detected:
                    name = detected.get("name", "Unknown")
                    self.current_game = detected
                    self.game_status_label.setText(f"GAME: {name.upper()}")
                    self.game_name_label.setText(name.upper())
                    info = detected.get("description", "Game detected. Ask OMNIX for assistance.")
                    self.game_info_label.setText(info)
                else:
                    self.current_game = None
                    self.game_status_label.setText("NO GAME DETECTED")
                    self.game_name_label.setText("── STANDBY ──")
                    self.game_info_label.setText("Launch a game to begin session tracking.")
        except Exception as e:
            logger.error(f"Game detection error: {e}")

    def _toggle_overlay(self) -> None:
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
        else:
            self.overlay_window.show()

    def _open_settings(self) -> None:
        if not self.settings_dialog:
            self.settings_dialog = TabbedSettingsDialog(
                self,
                self.config,
                self.keybind_manager,
                self.macro_manager,
                self.theme_manager,
            )
        self.settings_dialog.exec()

    def _open_macro_manager(self) -> None:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Macro Manager", "Macro manager coming in next phase.")

    def _open_knowledge_manager(self) -> None:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Knowledge Base", "Knowledge manager coming in next phase.")

    def _on_model_changed(self, model: str) -> None:
        if model:
            self.config.ollama_model = model
            try:
                self.config.save()
            except Exception as e:
                logger.error(f"Failed to save model config: {e}")

    def send_message_to_ai(self, text: str) -> None:
        """Public API — kept for backward compat."""
        self.chat_input.setText(text)
        self._on_send_clicked()

    def closeEvent(self, event) -> None:
        if self.overlay_window:
            self.overlay_window.close()
        if self.stats_timer:
            self.stats_timer.stop()
        super().closeEvent(event)


def run_gui(
    ai_assistant,
    config: Config,
    credential_store: CredentialStore,
    ds: OmnixDesignSystem = design_system,
    game_detector=None,
) -> None:
    """Launch the Omnix GUI."""
    app = QApplication.instance() or QApplication(sys.argv)

    # Set dark palette as fallback
    app.setStyle("Fusion")

    window = MainWindow(ai_assistant, config, credential_store, ds, game_detector)
    window.show()
    sys.exit(app.exec())


__all__ = [
    "AIWorkerThread",
    "OverlayWindow",
    "MainWindow",
    "run_gui",
]