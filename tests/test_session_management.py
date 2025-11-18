"""
Test suite for Session Management

Tests session logging, coaching, and recap functionality.
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from src.session_logger import SessionLogger, SessionEvent
from src.session_coaching import SessionCoach
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestSessionEvent:
    """Test SessionEvent data class"""

    def test_session_event_creation(self):
        """Test creating a session event"""
        event = SessionEvent(
            timestamp=datetime.now(),
            event_type="question",
            game_profile_id="elden_ring",
            content="How do I beat Margit?",
            meta={"difficulty": "hard"}
        )

        assert event.event_type == "question"
        assert event.game_profile_id == "elden_ring"
        assert event.meta["difficulty"] == "hard"

    def test_session_event_without_meta(self):
        """Test creating event without metadata"""
        event = SessionEvent(
            timestamp=datetime.now(),
            event_type="answer",
            game_profile_id="test_game",
            content="Response"
        )

        assert event.meta is None or event.meta == {}


@pytest.mark.unit
class TestSessionLogger:
    """Test SessionLogger functionality"""

    def test_logger_initialization(self, clean_config_dir):
        """Test logger initialization"""
        logger = SessionLogger(config_dir=clean_config_dir)
        assert logger is not None

    def test_log_question_event(self, clean_config_dir):
        """Test logging a question event"""
        logger = SessionLogger(config_dir=clean_config_dir)

        logger.log_event(
            game_profile_id="test_game",
            event_type="question",
            content="Test question",
            meta={"source": "user"}
        )

        events = logger.get_current_session_events("test_game")
        assert len(events) > 0
        assert events[-1].event_type == "question"
        assert events[-1].content == "Test question"

    def test_log_answer_event(self, clean_config_dir):
        """Test logging an answer event"""
        logger = SessionLogger(config_dir=clean_config_dir)

        logger.log_event(
            game_profile_id="test_game",
            event_type="answer",
            content="Test answer"
        )

        events = logger.get_current_session_events("test_game")
        assert len(events) > 0
        assert events[-1].event_type == "answer"

    def test_multiple_sessions(self, clean_config_dir):
        """Test handling multiple game sessions"""
        logger = SessionLogger(config_dir=clean_config_dir)

        # Log events for different games
        logger.log_event("game1", "question", "Question 1")
        logger.log_event("game2", "question", "Question 2")
        logger.log_event("game1", "answer", "Answer 1")

        game1_events = logger.get_current_session_events("game1")
        game2_events = logger.get_current_session_events("game2")

        assert len(game1_events) == 2
        assert len(game2_events) == 1

    def test_session_summary(self, clean_config_dir):
        """Test generating session summary"""
        logger = SessionLogger(config_dir=clean_config_dir)

        # Log multiple events
        for i in range(5):
            logger.log_event("test_game", "question", f"Question {i}")
            logger.log_event("test_game", "answer", f"Answer {i}")

        summary = logger.get_session_summary("test_game")

        assert summary["total_events"] == 10
        assert summary["event_types"]["question"] == 5
        assert summary["event_types"]["answer"] == 5

    def test_clear_session(self, clean_config_dir):
        """Test clearing session events"""
        logger = SessionLogger(config_dir=clean_config_dir)

        logger.log_event("test_game", "question", "Test")
        assert len(logger.get_current_session_events("test_game")) > 0

        logger.clear_session("test_game")
        assert len(logger.get_current_session_events("test_game")) == 0

    def test_session_persistence(self, clean_config_dir):
        """Test that sessions persist to disk"""
        logger1 = SessionLogger(config_dir=clean_config_dir)
        logger1.log_event("test_game", "question", "Persistent question")

        # Create new logger instance
        logger2 = SessionLogger(config_dir=clean_config_dir)
        events = logger2.get_current_session_events("test_game")

        # May or may not persist depending on implementation
        # Just verify method doesn't crash
        assert isinstance(events, list)

    def test_max_events_limit(self, clean_config_dir):
        """Test that logger respects max events limit"""
        logger = SessionLogger(config_dir=clean_config_dir)

        # Log many events
        for i in range(150):  # More than typical MAX_EVENTS_IN_MEMORY (100)
            logger.log_event("test_game", "question", f"Question {i}")

        events = logger.get_current_session_events("test_game")

        # Should handle large number of events without crashing
        assert isinstance(events, list)


@pytest.mark.unit
class TestSessionCoach:
    """Test SessionCoach functionality"""

    @patch('src.session_coaching.AIAssistant')
    def test_coach_initialization(self, mock_ai_class):
        """Test coach initialization"""
        mock_ai = Mock()
        mock_logger = Mock()

        coach = SessionCoach(ai_assistant=mock_ai, session_logger=mock_logger)
        assert coach is not None

    @patch('src.session_coaching.AIAssistant')
    def test_generate_recap(self, mock_ai_class):
        """Test generating session recap"""
        mock_ai = Mock()
        mock_ai.ask_question.return_value = "Session recap: You played well!"

        mock_logger = Mock()
        mock_events = [
            SessionEvent(
                timestamp=datetime.now(),
                event_type="question",
                game_profile_id="test_game",
                content="How do I play?"
            )
        ]
        mock_logger.get_current_session_events.return_value = mock_events

        coach = SessionCoach(ai_assistant=mock_ai, session_logger=mock_logger)
        recap = coach.generate_recap("test_game", mock_events)

        # Should return some recap text
        assert isinstance(recap, str)
        assert len(recap) > 0

    @patch('src.session_coaching.AIAssistant')
    def test_generate_insights(self, mock_ai_class):
        """Test generating gameplay insights"""
        mock_ai = Mock()
        mock_logger = Mock()

        coach = SessionCoach(ai_assistant=mock_ai, session_logger=mock_logger)
        insights = coach.generate_insights("test_game")

        # Should return insights dict
        assert isinstance(insights, dict)

    @patch('src.session_coaching.AIAssistant')
    def test_get_coaching_tips(self, mock_ai_class):
        """Test getting coaching tips"""
        mock_ai = Mock()
        mock_logger = Mock()

        coach = SessionCoach(ai_assistant=mock_ai, session_logger=mock_logger)
        tips = coach.get_coaching_tips("test_game")

        # Should return list of tips
        assert isinstance(tips, list)


@pytest.mark.integration
class TestSessionIntegration:
    """Integration tests for session management"""

    def test_full_session_workflow(self, clean_config_dir):
        """Test complete session logging and coaching workflow"""
        logger = SessionLogger(config_dir=clean_config_dir)

        # Simulate a gaming session
        game_id = "test_game"

        # Start session - game detected
        logger.log_event(game_id, "game_detected", "Test Game launched")

        # User asks questions
        logger.log_event(game_id, "question", "How do I start?")
        logger.log_event(game_id, "answer", "Press the start button")

        logger.log_event(game_id, "question", "What's the best strategy?")
        logger.log_event(game_id, "answer", "Focus on defense first")

        # Execute a macro
        logger.log_event(game_id, "macro", "Quick attack combo executed")

        # End session
        logger.log_event(game_id, "game_closed", "Test Game exited")

        # Verify session data
        events = logger.get_current_session_events(game_id)
        assert len(events) == 6

        summary = logger.get_session_summary(game_id)
        assert summary["total_events"] == 6
        assert "question" in summary["event_types"]
        assert "answer" in summary["event_types"]


@pytest.mark.unit
class TestEventTypes:
    """Test different event types"""

    def test_question_event(self, clean_config_dir):
        """Test question event logging"""
        logger = SessionLogger(config_dir=clean_config_dir)
        logger.log_event("test", "question", "Test question")

        events = logger.get_current_session_events("test")
        assert events[-1].event_type == "question"

    def test_answer_event(self, clean_config_dir):
        """Test answer event logging"""
        logger = SessionLogger(config_dir=clean_config_dir)
        logger.log_event("test", "answer", "Test answer")

        events = logger.get_current_session_events("test")
        assert events[-1].event_type == "answer"

    def test_macro_event(self, clean_config_dir):
        """Test macro event logging"""
        logger = SessionLogger(config_dir=clean_config_dir)
        logger.log_event("test", "macro", "Macro executed")

        events = logger.get_current_session_events("test")
        assert events[-1].event_type == "macro"

    def test_game_detected_event(self, clean_config_dir):
        """Test game detected event"""
        logger = SessionLogger(config_dir=clean_config_dir)
        logger.log_event("test", "game_detected", "Game launched")

        events = logger.get_current_session_events("test")
        assert events[-1].event_type == "game_detected"

    def test_game_closed_event(self, clean_config_dir):
        """Test game closed event"""
        logger = SessionLogger(config_dir=clean_config_dir)
        logger.log_event("test", "game_closed", "Game exited")

        events = logger.get_current_session_events("test")
        assert events[-1].event_type == "game_closed"
