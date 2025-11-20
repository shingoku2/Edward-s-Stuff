#!/usr/bin/env python3
"""
UI smoke test helper for Omnix Gaming Companion.

This tool exercises key UI elements without requiring a visible display. It
launches the chat widget with a stubbed AI assistant, simulates user input,
waits for the threaded response, and can optionally capture a screenshot for
manual review. The process is headless-friendly via the offscreen Qt platform
plugin.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import ctypes.util
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

Qt = None
QTest = None
QApplication = None
ChatWidget = None

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_qt_modules():
    if ctypes.util.find_library("GL") is None:
        print("Missing dependency: libGL.so.1 (install via apt: libgl1)")
        sys.exit(2)

    global Qt, QTest, QApplication, ChatWidget

    from PyQt6.QtCore import Qt as QtCore
    from PyQt6.QtTest import QTest as QtTest
    from PyQt6.QtWidgets import QApplication as QtApplication

    from gui import ChatWidget as ChatWidgetType

    Qt = QtCore
    QTest = QtTest
    QApplication = QtApplication
    ChatWidget = ChatWidgetType


@dataclass
class UITestReport:
    """Structured results for a UI test run."""

    user_bubbles: int
    ai_bubbles: int
    duration_ms: int
    screenshot_path: Optional[Path]
    response_completed: bool

    @property
    def passed(self) -> bool:
        return (
            self.response_completed
            and self.user_bubbles >= 1
            and self.ai_bubbles >= 1
        )


class EchoAssistant:
    """Minimal AI assistant stub that echoes questions back."""

    def __init__(self):
        self.history = []
        self._session_handler = None

    def ask_question(self, question: str, game_context=None) -> str:
        self.history.append(question)
        prefix = "[context] " if game_context else ""
        return f"{prefix}Echo: {question}"

    def clear_history(self):
        self.history.clear()

    def register_session_refresh_handler(self, handler):
        self._session_handler = handler


def ensure_offscreen_platform():
    """Force the Qt offscreen platform if none is configured."""

    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"


def ensure_app():
    load_qt_modules()
    ensure_offscreen_platform()
    app = QApplication.instance()
    if app is None:
        app = QApplication(["ui-test-tool"])
    return app


def count_bubbles(widget: ChatWidget) -> Tuple[int, int]:
    user_count = 0
    ai_count = 0
    for index in range(widget.messages_layout.count()):
        item = widget.messages_layout.itemAt(index)
        bubble = item.widget()
        if bubble is None:
            continue
        role = bubble.property("role")
        if role == "user":
            user_count += 1
        elif role == "ai":
            ai_count += 1
    return user_count, ai_count


def wait_for_response(widget: ChatWidget, app: QApplication, timeout_ms: int) -> bool:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        app.processEvents()
        if widget.ai_worker is None:
            return True
        QTest.qWait(20)
    return widget.ai_worker is None


def capture_screenshot(widget: ChatWidget, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = widget.grab()
    pixmap.save(str(path))
    return path


def run_chat_smoke_test(message: str, width: int, height: int, wait_ms: int, screenshot: Optional[Path]) -> UITestReport:
    app = ensure_app()

    assistant = EchoAssistant()
    chat = ChatWidget(assistant, title="UI Test Chat")
    chat.resize(width, height)
    chat.show()
    app.processEvents()

    QTest.keyClicks(chat.input_field, message)
    QTest.keyPress(chat.input_field, Qt.Key.Key_Return)

    start = time.monotonic()
    response_done = wait_for_response(chat, app, wait_ms)
    duration_ms = int((time.monotonic() - start) * 1000)

    user_bubbles, ai_bubbles = count_bubbles(chat)

    screenshot_path = None
    if screenshot:
        screenshot_path = capture_screenshot(chat, screenshot)

    chat.close()
    app.processEvents()

    return UITestReport(
        user_bubbles=user_bubbles,
        ai_bubbles=ai_bubbles,
        duration_ms=duration_ms,
        screenshot_path=screenshot_path,
        response_completed=response_done,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Headless UI test helper for Omnix")
    parser.add_argument(
        "--message",
        default="Ping from UI test",
        help="Message to send through the chat widget.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=900,
        help="Widget width for rendering and screenshots.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=640,
        help="Widget height for rendering and screenshots.",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=1500,
        help="Maximum wait time in milliseconds for AI response thread.",
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        help="Optional path to save a PNG screenshot of the chat widget.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    report = run_chat_smoke_test(
        message=args.message,
        width=args.width,
        height=args.height,
        wait_ms=args.wait,
        screenshot=args.screenshot,
    )

    status = "PASS" if report.passed else "FAIL"
    print(f"[{status}] UI chat smoke test")
    print(f"  User bubbles : {report.user_bubbles}")
    print(f"  AI bubbles   : {report.ai_bubbles}")
    print(f"  Duration     : {report.duration_ms} ms")
    print(f"  Response done: {report.response_completed}")
    if report.screenshot_path:
        print(f"  Screenshot   : {report.screenshot_path}")

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
