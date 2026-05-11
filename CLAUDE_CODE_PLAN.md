# OMNIX — Claude Code Implementation Plan: Option A (Pure PyQt6)
**Last Updated:** 2025-05-10  
**Target:** Eliminate QWebEngineView + React. Replace with 100% native PyQt6.  
**Scope:** GUI migration, dependency cleanup, licensing layer, CI/CD updates.

---

## CONTEXT FOR CLAUDE CODE

You are working on **Omnix**, a PyQt6 desktop AI gaming companion.

**The problem:** `src/gui.py` currently uses `QWebEngineView` as the central widget of `MainWindow`, loading a React/Vite frontend from `frontend/dist/index.html`. `OverlayWindow` also uses `QWebEngineView`. This ships a full Chromium engine (~150MB), requires Node.js to build, and forces a solo dev to maintain two UI frameworks simultaneously.

**The goal:** Rip out ALL `QWebEngineView`, `QWebChannel`, `JSBridge`, and React references. Replace with native PyQt6 widgets using the existing QSS/design-system already present in `src/ui/` and `src/omnix_hud.py`. All backend logic (AI, game detection, macros, knowledge system) stays UNCHANGED.

**What must NOT change:**
- `src/ai_assistant.py`
- `src/ai_router.py`
- `src/providers.py`
- `src/game_detector.py`
- `src/game_watcher.py`
- `src/knowledge_*.py`
- `src/macro_*.py`
- `src/session_*.py`
- `src/credential_store.py`
- `src/config.py`
- `src/hrm_*.py`
- All `tests/` files except `tests/ui/test_web_integration.py`

---

## PHASE 0 — AUDIT & BACKUP (Do This First)

### Step 0.1 — Create a git branch
```bash
git checkout -b feature/pure-pyqt6-migration
git push -u origin feature/pure-pyqt6-migration
```

### Step 0.2 — Archive the frontend (do NOT delete yet)
```bash
# Move frontend to an archive branch reference — don't delete from disk yet
# We'll remove it from main in Phase 4 after all tests pass
git tag archive/react-frontend HEAD
```

### Step 0.3 — Inventory what uses QWebEngineView
Run this and document the output:
```bash
grep -rn "QWebEngineView\|QWebChannel\|JSBridge\|webengine\|web_view\|frontend/dist" src/ tests/ --include="*.py"
```

**Expected hits:**
- `src/gui.py` — MainWindow.__init__, OverlayWindow.__init__, JSBridge class
- `tests/ui/test_web_integration.py` — entire file (delete this)
- `requirements.txt` — `PyQt6-WebEngine` entry

---

## PHASE 1 — REQUIREMENTS & DEPENDENCY CLEANUP

### Step 1.1 — Update `requirements.txt`

**REMOVE these lines:**
```
PyQt6-WebEngine>=6.6.0
PyQtWebEngine>=5.15.0   # if present
```

**ADD these lines (if not already present):**
```
PyQt6>=6.6.0
psutil>=5.9.0
pynput>=1.7.6
cryptography>=41.0.0
keyring>=24.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dotenv>=1.0.0
PyYAML>=6.0.1
supabase>=2.0.0          # ADD — for licensing layer
```

### Step 1.2 — Update `requirements-dev.txt`

**REMOVE:**
```
# Any Node.js / npm related entries
```

**ADD (if not present):**
```
pytest-qt>=4.4.0
```

### Step 1.3 — Update `BUILD.bat`

Find and remove any block that runs:
```bat
cd frontend
npm install
npm run build
cd ..
```

Replace with a comment:
```bat
REM React frontend removed — pure PyQt6 UI (see feature/pure-pyqt6-migration)
```

---

## PHASE 2 — DELETE DEAD CODE

### Step 2.1 — Delete `tests/ui/test_web_integration.py`
This file tests QWebEngineView and JSBridge. Both are being removed.
```bash
git rm tests/ui/test_web_integration.py
```

### Step 2.2 — Delete `src/gui.py`'s `JSBridge` class entirely
Open `src/gui.py`. Delete the entire `JSBridge` class (lines containing `class JSBridge(QObject):` through its last method). This is roughly 50 lines.

### Step 2.3 — Remove dead imports from `src/gui.py`

**Remove these import lines:**
```python
import json
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
```

**Keep all other imports.**

### Step 2.4 — Note: Do NOT delete `frontend/` from disk yet
Keep it on disk for reference. It will be removed from git tracking in Phase 5.

---

## PHASE 3 — BUILD THE NATIVE PyQt6 MAIN WINDOW

This is the core of the migration. Rewrite `MainWindow.__init__` and add native panel methods.

### Step 3.1 — Full replacement of `MainWindow` in `src/gui.py`

Replace the entire `MainWindow` class with the implementation below. **Keep `AIWorkerThread` and `OverlayWindow` — they stay, but `OverlayWindow` gets rewritten in Step 3.2.**

```python
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
        from PyQt6.QtWidgets import QTextEdit, QScrollArea

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

        from PyQt6.QtWidgets import QLabel as L, QComboBox
        model_label = L("AI Model")
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
        html = (
            f'<p style="margin:4px 0;">'
            f'<span style="color:{color};font-size:9px;letter-spacing:2px;'
            f'text-transform:uppercase;">{sender}</span><br/>'
            f'<span style="color:#e5e7eb;font-size:12px;">{text}</span>'
            f'</p><hr style="border:none;border-top:1px solid #1e293b;"/>'
        )
        self.chat_display.append(html)
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
                self.config, self.credential_store, parent=self
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
```

---

### Step 3.2 — Rewrite `OverlayWindow` in `src/gui.py`

Replace the entire `OverlayWindow` class with this pure PyQt6 version:

```python
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
        from PyQt6.QtWidgets import QTextEdit
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
        html = (
            f'<p style="margin:2px 0;">'
            f'<span style="color:{color};font-size:8px;letter-spacing:2px;">{sender}</span><br/>'
            f'<span style="color:#e5e7eb;font-size:11px;">{text}</span>'
            f'</p>'
        )
        self.chat_display.append(html)
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
```

---

### Step 3.3 — Update `src/gui.py` imports (final clean state)

The top of `src/gui.py` should import exactly this — no more, no less:

```python
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict, Optional
import psutil

from PyQt6.QtCore import QEvent, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QSizePolicy,
)

from src.config import Config
from src.credential_store import CredentialStore
from src.ui.design_system import OmnixDesignSystem, design_system
from src.keybind_manager import KeybindManager
from src.macro_manager import MacroManager
from src.ui.theme_manager import OmnixThemeManager
from src.settings_dialog import TabbedSettingsDialog
from src.omnix_hud import OMNIX_GLOBAL_QSS
```

---

### Step 3.4 — Add QSS for new widget IDs

In `src/omnix_hud.py` (or `src/ui/omnix.qss`), append these QSS rules to `OMNIX_GLOBAL_QSS`:

```python
# Append to OMNIX_GLOBAL_QSS string in src/omnix_hud.py

OMNIX_GLOBAL_QSS += """
/* ── Main panels ── */
QFrame#hud-panel {
    background-color: rgba(10, 16, 32, 0.97);
    border-radius: 14px;
    border: 1px solid rgba(34, 211, 238, 0.35);
}

QFrame#overlay-frame {
    background-color: rgba(5, 11, 20, 0.94);
    border-radius: 12px;
    border: 1px solid rgba(34, 211, 238, 0.5);
}

/* ── Labels ── */
QLabel#panel-title {
    font-size: 9px;
    letter-spacing: 0.30em;
    text-transform: uppercase;
    color: #22d3ee;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(34, 211, 238, 0.2);
}

QLabel#game-name-label {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #f0f9ff;
    padding: 12px 0;
}

QLabel#game-info-label {
    font-size: 11px;
    color: #94a3b8;
    padding: 4px 8px;
}

QLabel#stat-value {
    font-size: 12px;
    color: #22d3ee;
    letter-spacing: 0.1em;
}

QLabel#stat-label {
    font-size: 9px;
    letter-spacing: 0.2em;
    color: #64748b;
}

/* ── Chat ── */
QTextEdit#chat-display {
    background-color: rgba(8, 11, 25, 0.95);
    border-radius: 8px;
    border: 1px solid rgba(39, 39, 80, 0.8);
    color: #e5e7eb;
    font-size: 12px;
    padding: 8px;
}

QLineEdit#chat-input {
    background-color: rgba(8, 11, 25, 0.98);
    border-radius: 999px;
    border: 1px solid rgba(39, 39, 80, 0.9);
    padding: 8px 16px;
    font-size: 12px;
    color: #e5e7eb;
}
QLineEdit#chat-input:focus {
    border-color: rgba(34, 211, 238, 0.8);
}

/* ── Buttons ── */
QPushButton#neon-button-primary {
    background-color: rgba(34, 211, 238, 0.12);
    color: #22d3ee;
    border: 1px solid rgba(34, 211, 238, 0.7);
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 700;
}
QPushButton#neon-button-primary:hover {
    background-color: #22d3ee;
    color: #000;
}

QPushButton#neon-button-secondary {
    background-color: rgba(99, 102, 241, 0.12);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.5);
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 600;
}
QPushButton#neon-button-secondary:hover {
    background-color: #6366f1;
    color: #fff;
}

/* ── Combo ── */
QComboBox#omnix-combo {
    background-color: rgba(8, 11, 25, 0.95);
    border: 1px solid rgba(34, 211, 238, 0.4);
    border-radius: 6px;
    color: #e5e7eb;
    padding: 4px 8px;
    font-size: 11px;
}
QComboBox#omnix-combo:focus {
    border-color: #22d3ee;
}
"""
```

---

## PHASE 4 — SUPABASE LICENSING LAYER

### Step 4.1 — Create `src/licensing.py`

```python
"""
Omnix License Validator
Checks Supabase for a valid active subscription.
Runs on startup and every 24h.
"""
from __future__ import annotations

import logging
import time
import hashlib
import platform
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

_SUPABASE_URL = ""   # Populated from config / env
_SUPABASE_ANON_KEY = ""


def get_machine_id() -> str:
    """Deterministic per-machine fingerprint (no PII)."""
    node = platform.node()
    proc = platform.processor()
    raw = f"{node}:{proc}:{platform.machine()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


class LicenseValidator:
    """
    Validates license key against Supabase `licenses` table.

    Table schema expected:
        licenses (
            id          uuid primary key,
            key         text unique not null,
            email       text,
            status      text,           -- 'active' | 'expired' | 'cancelled'
            expires_at  timestamptz,
            seat_limit  int default 1,
            created_at  timestamptz
        )
    """

    GRACE_PERIOD_HOURS = 72   # Offline grace period

    def __init__(self, supabase_url: str, anon_key: str):
        self.url = supabase_url.rstrip("/")
        self.anon_key = anon_key
        self._last_valid: Optional[float] = None

    def validate(self, license_key: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, message).
        Falls back to grace period if Supabase is unreachable.
        """
        try:
            import requests
            resp = requests.get(
                f"{self.url}/rest/v1/licenses",
                params={"key": f"eq.{license_key}", "select": "status,expires_at"},
                headers={
                    "apikey": self.anon_key,
                    "Authorization": f"Bearer {self.anon_key}",
                },
                timeout=8,
            )
            if resp.status_code != 200:
                return self._grace_fallback("Supabase returned non-200")

            data = resp.json()
            if not data:
                return False, "License key not found."

            record = data[0]
            if record.get("status") != "active":
                return False, f"License is {record.get('status', 'unknown')}."

            # Check expiry
            expires_at = record.get("expires_at")
            if expires_at:
                from datetime import datetime, timezone
                exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if exp < datetime.now(timezone.utc):
                    return False, "License expired."

            self._last_valid = time.time()
            return True, "License valid."

        except Exception as e:
            logger.warning(f"License check failed: {e}")
            return self._grace_fallback(str(e))

    def _grace_fallback(self, reason: str) -> Tuple[bool, str]:
        if self._last_valid and (time.time() - self._last_valid) < self.GRACE_PERIOD_HOURS * 3600:
            logger.info("License: offline grace period active")
            return True, "Offline mode (grace period)."
        return False, f"Cannot verify license: {reason}"


# Singleton
_validator: Optional[LicenseValidator] = None


def get_validator(supabase_url: str = "", anon_key: str = "") -> LicenseValidator:
    global _validator
    if _validator is None:
        _validator = LicenseValidator(supabase_url, anon_key)
    return _validator
```

### Step 4.2 — Create `src/license_dialog.py`

```python
"""
License activation dialog shown on first run or when license is invalid.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

from src.licensing import LicenseValidator


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
            from src.credential_store import CredentialStore
            store = CredentialStore()
            store.set_credential("omnix_license_key", key)
            QMessageBox.information(self, "Activated", "License activated successfully!")
            self.accept()
```

### Step 4.3 — Hook licensing into `main.py`

At the top of `main.py`'s `main()` function, add this block **before** the `MainWindow` is created:

```python
# ── License check ────────────────────────────────────────────────────────
import os
from src.licensing import get_validator
from src.credential_store import CredentialStore

_cred_store = CredentialStore()
_license_key = _cred_store.get_credential("omnix_license_key") or os.getenv("OMNIX_LICENSE_KEY", "")

_supabase_url = os.getenv("SUPABASE_URL", "")
_supabase_key = os.getenv("SUPABASE_ANON_KEY", "")

# Skip licensing in dev mode
_dev_mode = os.getenv("OMNIX_DEV_MODE", "").lower() in ("1", "true", "yes")

if not _dev_mode and _supabase_url:
    _validator = get_validator(_supabase_url, _supabase_key)
    _valid, _msg = _validator.validate(_license_key) if _license_key else (False, "No key")

    if not _valid:
        from src.license_dialog import LicenseDialog
        dlg = LicenseDialog(_validator)
        if dlg.exec() != dlg.DialogCode.Accepted:
            logger.warning("License not activated. Exiting.")
            sys.exit(1)
```

### Step 4.4 — Add to `.env.example`

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
OMNIX_LICENSE_KEY=
OMNIX_DEV_MODE=1    # Set to 1 during development to skip licensing
```

---

## PHASE 5 — CLEANUP & FRONTEND REMOVAL

### Step 5.1 — Remove `frontend/` from git tracking
```bash
# Add to .gitignore
echo "frontend/node_modules/" >> .gitignore
echo "frontend/dist/" >> .gitignore

# Remove from tracking (keep on disk in case needed for reference)
git rm -r --cached frontend/
git commit -m "chore: remove React frontend from tracking (pure PyQt6 migration)"
```

### Step 5.2 — Remove `QWebEngineWidgets` from `PyInstaller` spec

In `GamingAIAssistant.spec`, find and remove any `collect_submodules('PyQt6.QtWebEngineWidgets')` or similar entries.

### Step 5.3 — Update `pytest.ini` / `setup.cfg`

Remove `tests/ui/test_web_integration.py` from any explicit include lists.

Add to `addopts` if not present:
```ini
addopts = --ignore=tests/ui/test_web_integration.py
```

---

## PHASE 6 — ADD MISSING QSS TO `src/ui/design_system.py`

Verify `get_overlay_stylesheet()` returns valid CSS for the new `QFrame#overlay-frame` widget ID.

In `src/ui/design_system.py`, update `get_overlay_stylesheet()` to include:

```python
QFrame#overlay-frame {{
    background-color: rgba(5, 11, 20, {opacity});
    border-radius: 12px;
    border: 1px solid rgba(34, 211, 238, 0.5);
}}
```

where `{opacity}` is computed from the `opacity` float parameter (format to hex alpha as already done in that method).

---

## PHASE 7 — TESTING

### Step 7.1 — Run the test suite
```bash
# Ensure no import of QWebEngineView anywhere
grep -rn "QWebEngineView\|QWebChannel\|JSBridge" src/ tests/ --include="*.py"
# Expected: 0 results

# Run tests
python -m pytest tests/unit/ tests/integration/ -v --tb=short

# Run GUI smoke test (headless)
OMNIX_DEV_MODE=1 QT_QPA_PLATFORM=offscreen python -m pytest tests/ui/ -v --tb=short -k "not web_integration"
```

### Step 7.2 — Smoke test the actual app
```bash
OMNIX_DEV_MODE=1 python main.py
```

Verify:
- [ ] Main window opens with 3-column layout
- [ ] Chat input accepts text and shows response
- [ ] Overlay window opens via "TOGGLE OVERLAY" button
- [ ] Overlay is draggable
- [ ] Overlay minimize button works
- [ ] System stats (CPU/RAM) update every second
- [ ] Game detection runs without error
- [ ] Settings dialog opens
- [ ] No `QWebEngineView` or `QWebChannel` errors in log

### Step 7.3 — Verify binary size reduction
```bash
python build_windows_exe.py
# Check dist/ folder — binary should be ~40-70MB, not 150MB+
du -sh dist/
```

---

## PHASE 8 — DOCUMENTATION UPDATES

### Step 8.1 — Update `CLAUDE.md`

Replace the "Technology Stack" section with:

```markdown
## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | PyQt6 6.6.0+ (100% native — no QWebEngineView) |
| AI Inference | Ollama (local/remote LLM) |
| Process Monitoring | psutil |
| Macro Automation | pynput |
| Security | cryptography (AES-256) + keyring |
| Licensing | Supabase (REST API) |
| Packaging | PyInstaller |

**React/QWebEngineView removed in v2.1** — see git tag `archive/react-frontend`.
```

### Step 8.2 — Update `aicontext.md`

Add to the changelog section:

```markdown
### 2025-05-10: Pure PyQt6 Migration (MAJOR — Option A)
- ✅ REMOVED QWebEngineView from MainWindow and OverlayWindow
- ✅ REMOVED JSBridge class and QWebChannel dependency
- ✅ REMOVED React/Vite frontend (frontend/ removed from git tracking)
- ✅ REMOVED PyQt6-WebEngine from requirements.txt
- ✅ BUILT native PyQt6 MainWindow with 3-column dashboard layout
- ✅ BUILT native PyQt6 OverlayWindow (draggable, minimizable, position-saving)
- ✅ ADDED Supabase licensing layer (src/licensing.py, src/license_dialog.py)
- ✅ ADDED OMNIX_DEV_MODE env var to bypass licensing in development
- ✅ Binary size reduction: ~150MB → ~50-70MB target
- ✅ Eliminated Node.js/npm as build dependency
- ✅ Eliminated QWebEngineView Chromium overhead from runtime
```

---

## PHASE 9 — FUTURE ENHANCEMENTS (Post-Launch)

These are NOT part of this plan — log as GitHub issues for later:

| Feature | Issue Label |
|---|---|
| Model picker fetches live Ollama model list | `enhancement` |
| Macro Manager full UI in right panel | `enhancement` |
| Knowledge Base browser in tab | `enhancement` |
| Session coaching panel below game info | `enhancement` |
| Hotkey to show/hide overlay (global keybind) | `enhancement` |
| Tray icon with right-click menu | `enhancement` |
| Stripe payment link in license dialog | `enhancement` |
| Dark/light theme toggle | `enhancement` |

---

## EXECUTION ORDER SUMMARY

```
Phase 0  → git branch + audit (15 min)
Phase 1  → requirements.txt cleanup (10 min)
Phase 2  → delete dead code: JSBridge, test_web_integration.py (15 min)
Phase 3  → rewrite MainWindow + OverlayWindow in gui.py (2-3 hrs)
Phase 4  → create licensing.py + license_dialog.py + hook main.py (1 hr)
Phase 5  → remove frontend/ from git, update PyInstaller spec (20 min)
Phase 6  → verify/update design_system.py QSS (20 min)
Phase 7  → run full test suite + smoke test app (30 min)
Phase 8  → update CLAUDE.md + aicontext.md (15 min)
Phase 9  → open GitHub issues for post-launch features (10 min)

TOTAL: ~5-6 hours of focused work
```

---

## CRITICAL RULES FOR CLAUDE CODE

1. **Never touch** `src/ai_assistant.py`, `src/providers.py`, `src/game_detector.py`, `src/knowledge_*.py`, `src/macro_*.py`, `src/session_*.py`, `src/credential_store.py`, `src/config.py`
2. **Never** add `QWebEngineView`, `QWebChannel`, or `JSBridge` back under any circumstances
3. **Never** add Node.js/npm as a dependency
4. **Always** run `grep -rn "QWebEngineView" src/` after each phase to verify it's gone
5. **Always** update `aicontext.md` after each phase completes
6. **Always** run `python -m pytest tests/unit/ -x -q` before committing any phase
7. **Use** `OMNIX_DEV_MODE=1` in `.env` during all development — never commit a license key
8. If any import fails, check `requirements.txt` before touching source files
9. The QSS `objectName` values are load-bearing — match them exactly as specified
10. `OverlayWindow` must remain `WA_TranslucentBackground = True` and `FramelessWindowHint`
