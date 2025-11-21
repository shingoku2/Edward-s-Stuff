"""
Chat and ChatPanel Widgets
"""
import logging

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.tokens import SPACING
from ai_assistant import AIWorkerThread
from ui.components import OmnixLineEdit

logger = logging.getLogger(__name__)


class ChatWidget(NeonCard):
    """Chat interface widget for Q&A interactions with AI assistant."""

    def __init__(self, ai_assistant, title: str = "CHAT"):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.ai_worker = None
        self.game_context_provider = None
        self.title = title
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING.xl, SPACING.lg, SPACING.xl, SPACING.lg)
        layout.setSpacing(SPACING.lg)
        self.setObjectName("ChatWidget")

        if self.title:
            header = QVBoxLayout()
            header.setSpacing(4)
            top_row = QHBoxLayout()
            title_label = QLabel(self.title)
            title_label.setObjectName("ChatTitle")
            subtitle = QLabel("Ready to assist")
            subtitle.setObjectName("ChatSubtitle")
            top_row.addWidget(title_label)
            top_row.addStretch()
            top_row.addWidget(subtitle)
            header.addLayout(top_row)

            accent = QFrame()
            accent.setObjectName("ChatDivider")
            accent.setFixedHeight(1)
            header.addWidget(accent)
            layout.addLayout(header)

        # Chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(SPACING.sm)
        self.messages_layout.addStretch()
        self.messages_container.setLayout(self.messages_layout)

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

        # User input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(SPACING.sm)

        self.input_field = OmnixLineEdit(placeholder="Ask anything about your match...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = NeonButton("SEND")
        self.send_button.setObjectName("SendButton")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self.clear_button = NeonButton("CLEAR")
        self.clear_button.setObjectName("ClearButton")
        self.clear_button.clicked.connect(self.clear_chat)
        action_row.addWidget(self.clear_button)
        layout.addLayout(action_row)

    def set_game_context_provider(self, provider):
        self.game_context_provider = provider

    def send_message(self):
        question = self.input_field.text().strip()

        if not question:
            return

        if not self.ai_assistant:
            self.add_message(
                "System",
                "⚠️ AI assistant not configured. Please click the ⚙️ Settings button to add your API keys.",
                is_user=False,
            )
            self.input_field.clear()
            return

        self.add_message("You", question, is_user=True)
        self.input_field.clear()

        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        self.send_button.setText("Thinking...")

        game_context = None
        if callable(self.game_context_provider):
            try:
                game_context = self.game_context_provider()
            except Exception as exc:
                logger.error(f"Failed to gather game context: {exc}", exc_info=True)
                game_context = None

        self.ai_worker = AIWorkerThread(self.ai_assistant, question, game_context=game_context)
        self.ai_worker.response_ready.connect(self.on_ai_response)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.start()

    def on_ai_response(self, response: str):
        self.add_message("AI Assistant", response, is_user=False)

    def on_ai_error(self, error: str):
        self.add_message("System", f"Error: {error}", is_user=False)

    def on_ai_finished(self):
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.send_button.setText("SEND")
        self.ai_worker = None

    def add_message(self, sender: str, message: str, is_user: bool = True):
        message_escaped = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        bubble = QFrame()
        bubble.setObjectName("ChatBubbleUser" if is_user else "ChatBubbleAI")
        bubble.setProperty("role", "user" if is_user else "ai")
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(SPACING.md, SPACING.sm, SPACING.md, SPACING.sm)
        bubble_layout.setSpacing(4)

        sender_label = QLabel(sender)
        sender_label.setObjectName("ChatSender")
        text_label = QLabel(message_escaped)
        text_label.setObjectName("ChatText")
        text_label.setWordWrap(True)

        bubble_layout.addWidget(sender_label)
        bubble_layout.addWidget(text_label)
        bubble.setLayout(bubble_layout)

        effect = QGraphicsOpacityEffect()
        bubble.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        insert_index = max(self.messages_layout.count() - 1, 0)
        self.messages_layout.insertWidget(insert_index, bubble)
        self._fade_in(effect)

        QTimer.singleShot(0, self._scroll_to_bottom)

    def _fade_in(self, effect: QGraphicsOpacityEffect):
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(220)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _scroll_to_bottom(self):
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear_chat(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if self.ai_assistant:
            self.ai_assistant.clear_history()
        logger.info("Chat history cleared")


class ChatPanel(ChatWidget):
    """Chat widget wrapper for the dashboard."""

    def __init__(self, ai_assistant):
        super().__init__(ai_assistant, title="CHAT")
        self.setObjectName("ChatPanel")
