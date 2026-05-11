"""
Unit tests for AIWorkerThread and AI chat flow.

Tests that the background worker correctly calls the assistant
and emits signals with responses or errors.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from src.gui import AIWorkerThread


@pytest.mark.unit
class TestAIWorkerThread:
    """Test AIWorkerThread background worker."""

    def test_worker_initialization(self):
        """Test worker initializes with assistant, question, and context."""
        mock_assistant = Mock()
        worker = AIWorkerThread(mock_assistant, "What is the best build?")

        assert worker.assistant is mock_assistant
        assert worker.question == "What is the best build?"
        assert worker.game_context == {}

    def test_worker_with_game_context(self):
        """Test worker passes game context to assistant."""
        mock_assistant = Mock()
        mock_assistant.ask_question.return_value = "Use Intelligence build."

        context = {"game": "Elden Ring", "level": 50}
        worker = AIWorkerThread(mock_assistant, "Best build?", context)

        assert worker.game_context == context

    def test_worker_finished_signal_on_success(self):
        """Test finished signal is emitted with response on success."""
        mock_assistant = Mock()
        mock_assistant.ask_question.return_value = "Here is the answer."

        worker = AIWorkerThread(mock_assistant, "Test question")

        # Track signal emissions
        finished_response = []
        worker.finished.connect(lambda r: finished_response.append(r))

        # Run the worker
        worker.run()

        # Verify finished signal was emitted with response
        assert len(finished_response) == 1
        assert finished_response[0] == "Here is the answer."

    def test_worker_error_signal_on_exception(self):
        """Test error signal is emitted when assistant raises exception."""
        mock_assistant = Mock()
        mock_assistant.ask_question.side_effect = Exception("AI provider unavailable")

        worker = AIWorkerThread(mock_assistant, "Test question")

        # Track signal emissions
        error_messages = []
        worker.error.connect(lambda e: error_messages.append(e))

        # Run the worker
        worker.run()

        # Verify error signal was emitted
        assert len(error_messages) == 1
        assert "AI provider unavailable" in error_messages[0]

    def test_worker_with_none_assistant(self):
        """Test worker handles None assistant gracefully."""
        worker = AIWorkerThread(None, "Any question")

        # Track signal emissions
        finished_response = []
        worker.finished.connect(lambda r: finished_response.append(r))

        # Run the worker
        worker.run()

        # Should emit default standing-by message
        assert len(finished_response) == 1
        assert "standing by" in finished_response[0].lower()

    def test_worker_with_empty_response(self):
        """Test worker handles empty response from assistant."""
        mock_assistant = Mock()
        mock_assistant.ask_question.return_value = ""

        worker = AIWorkerThread(mock_assistant, "Test")

        finished_response = []
        worker.finished.connect(lambda r: finished_response.append(r))

        worker.run()

        # Should emit empty string
        assert len(finished_response) == 1
        assert finished_response[0] == ""

    def test_worker_with_none_response(self):
        """Test worker handles None response from assistant."""
        mock_assistant = Mock()
        mock_assistant.ask_question.return_value = None

        worker = AIWorkerThread(mock_assistant, "Test")

        finished_response = []
        worker.finished.connect(lambda r: finished_response.append(r))

        worker.run()

        # Should emit empty string (None converted to "")
        assert len(finished_response) == 1
        assert finished_response[0] == ""

    def test_worker_passes_question_and_context_to_assistant(self):
        """Test that worker passes both question and context to assistant."""
        mock_assistant = Mock()
        mock_assistant.ask_question.return_value = "Response"

        context = {"game": "Dark Souls", "boss": "Ornstein"}
        worker = AIWorkerThread(mock_assistant, "How to beat Ornstein?", context)

        worker.run()

        # Verify ask_question was called with correct arguments
        mock_assistant.ask_question.assert_called_once_with(
            "How to beat Ornstein?", game_context=context
        )


@pytest.mark.unit
class TestAIWorkerThreadSignals:
    """Test AIWorkerThread Qt signal connections."""

    def test_worker_has_finished_signal(self):
        """Test worker has finished pyqtSignal."""
        worker = AIWorkerThread(Mock(), "test")
        assert hasattr(worker, 'finished')

    def test_worker_has_error_signal(self):
        """Test worker has error pyqtSignal."""
        worker = AIWorkerThread(Mock(), "test")
        assert hasattr(worker, 'error')

    def test_multiple_signal_connections(self):
        """Test multiple functions can connect to finished signal."""
        mock_assistant = Mock()
        mock_assistant.ask_question.return_value = "Done"

        worker = AIWorkerThread(mock_assistant, "test")

        results1 = []
        results2 = []
        worker.finished.connect(lambda r: results1.append(r))
        worker.finished.connect(lambda r: results2.append(r))

        worker.run()

        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0] == results2[0]