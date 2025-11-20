import pytest

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QStackedWidget, QWidget
except Exception as exc:  # pragma: no cover - environment guard
    pytest.skip(f"PyQt6 unavailable: {exc}", allow_module_level=True)

import gui
from gui import ChatWidget, OverlayWindow
from ui.components.buttons import OmnixButton
from ui.components.navigation import OmnixSidebar
from ui.design_system import OmnixDesignSystem


@pytest.mark.unit
def test_design_system_neon_button_styles():
    styles = OmnixDesignSystem().generate_button_stylesheet()
    assert "NEON" in styles
    assert "QPushButton" in styles


@pytest.mark.ui
def test_sidebar_navigation_switches_pages(qtbot):
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
    class DummyAssistant:
        def ask_question(self, question, game_context=None):
            return "ok"

    class DummyDesignSystem:
        def generate_overlay_stylesheet(self, opacity):
            return ""

    class DummyConfig:
        overlay_x = 10
        overlay_y = 20
        overlay_width = 300
        overlay_height = 200
        overlay_minimized = False
        overlay_opacity = 0.5
        ai_provider = "anthropic"
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
def test_chat_widget_uses_worker_thread(monkeypatch, qtbot):
    started = []

    def fake_start(self):
        started.append(self.question)

    monkeypatch.setattr(gui.AIWorkerThread, "start", fake_start, raising=False)

    class DummyAssistant:
        def ask_question(self, question, game_context=None):
            return "response"

    widget = ChatWidget(DummyAssistant())
    qtbot.addWidget(widget)

    widget.input_field.setText("Hello")
    qtbot.mouseClick(widget.send_button, Qt.MouseButton.LeftButton)

    assert started == ["Hello"]
    assert not widget.send_button.isEnabled()
