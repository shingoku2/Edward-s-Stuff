import pytest
from unittest.mock import MagicMock
import json
from src.gui import OverlayWindow, MainWindow


@pytest.mark.unit
def test_design_system_neon_button_styles():
    from src.ui.design_system import OmnixDesignSystem
    styles = OmnixDesignSystem().generate_button_stylesheet()
    assert "NEON" in styles
    assert "QPushButton" in styles


@pytest.mark.ui
def test_sidebar_navigation_switches_pages(qtbot):
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QStackedWidget, QWidget
    from src.ui.components.navigation import OmnixSidebar

    stack = QStackedWidget()
    stack.addWidget(QWidget())
    stack.addWidget(QWidget())

    sidebar = OmnixSidebar()
    sidebar.tab_changed.connect(stack.setCurrentIndex)
    first = sidebar.add_button("Chat", "\ud83d\udcac")
    second = sidebar.add_button("Settings", "\u2699")

    qtbot.addWidget(sidebar)
    qtbot.mouseClick(second, Qt.MouseButton.LeftButton)

    assert stack.currentIndex() == 1
    assert second.isChecked()
    assert not first.isChecked()


@pytest.mark.ui
def test_overlay_window_flags_and_toggle(qtbot):
    from PyQt6.QtCore import Qt

    class DummyAssistant:
        def ask_question(self, question, game_context=None):
            return "ok"

    class DummyDesignSystem:
        def get_overlay_stylesheet(self, opacity):
            return ""

    class DummyConfig:
        overlay_x = 10
        overlay_y = 20
        overlay_width = 300
        overlay_height = 200
        overlay_minimized = False
        overlay_opacity = 0.5
        ai_provider = "ollama"
        session_tokens = {}
        check_interval = 5
        overlay_hotkey = "ctrl+g"

    window = OverlayWindow(DummyAssistant(), DummyConfig(), DummyDesignSystem())
    qtbot.addWidget(window)

    flags = window.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowStaysOnTopHint

    original_height = window.height()
    window.toggle_minimize()
    assert window.height() <= original_height


@pytest.mark.ui
def test_main_window_send_message(monkeypatch, qtbot):
    """Test that MainWindow.send_message_to_ai properly triggers AI worker."""
    from src.gui import MainWindow, AIWorkerThread

    started = []

    def fake_start(self):
        started.append(self.question)

    monkeypatch.setattr(AIWorkerThread, "start", fake_start, raising=False)

    class DummyAssistant:
        def ask_question(self, question, game_context=None):
            return "response"

    class DummyCredentialStore:
        pass

    class DummyDesignSystem:
        def get_overlay_stylesheet(self, opacity):
            return ""

    class DummyConfig:
        overlay_x = 100
        overlay_y = 100
        overlay_width = 900
        overlay_height = 700
        overlay_minimized = False
        overlay_opacity = 0.95
        ai_provider = "ollama"
        session_tokens = {}
        check_interval = 5
        overlay_hotkey = "ctrl+shift+g"
        ollama_model = "llama3"

    window = MainWindow(
        ai_assistant=DummyAssistant(),
        config=DummyConfig(),
        credential_store=DummyCredentialStore(),
        design_system=DummyDesignSystem(),
        game_detector=None,
    )
    qtbot.addWidget(window)

    # Use the public API to send a message
    window.send_message_to_ai("Hello")

    assert started == ["Hello"]
