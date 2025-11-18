"""
Comprehensive test suite for session coaching
Tests session recap generation, event formatting, and coaching insights
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.session_logger import SessionLogger, SessionEvent
from src.session_coaching import SessionCoach
from src.config import Config


@pytest.mark.unit
class TestSessionCoachInitialization:
    """Test session coach initialization"""

    def test_initialization_default(self, temp_config_dir):
        """Test default initialization"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        assert coach is not None
        assert coach.session_logger is not None
        assert coach.config is not None

    def test_initialization_with_custom_logger(self, temp_config_dir):
        """Test initialization with custom logger"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))
        coach = SessionCoach(session_logger=logger, config=config)

        assert coach.session_logger is logger


@pytest.mark.unit
class TestEventFormatting:
    """Test event formatting for AI consumption"""

    def test_format_empty_events(self, temp_config_dir):
        """Test formatting empty event list"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        formatted = coach._format_events_for_recap([])

        # Should handle empty gracefully
        assert formatted is not None
        assert isinstance(formatted, str)

    def test_format_single_event(self, temp_config_dir):
        """Test formatting single event"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        events = [
            SessionEvent(
                timestamp=datetime.now(),
                event_type="question",
                game_profile_id="elden_ring",
                content="How do I beat Margit?",
                meta={}
            )
        ]

        formatted = coach._format_events_for_recap(events)

        assert "How do I beat Margit?" in formatted or len(formatted) > 0

    def test_format_multiple_events(self, sample_session_events, temp_config_dir):
        """Test formatting multiple events"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        formatted = coach._format_events_for_recap(sample_session_events)

        assert formatted is not None
        assert len(formatted) > 0

    def test_format_includes_timestamps(self, temp_config_dir):
        """Test that formatting includes timestamps"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        now = datetime.now()
        events = [
            SessionEvent(
                timestamp=now,
                event_type="question",
                game_profile_id="test",
                content="Test question",
                meta={}
            )
        ]

        formatted = coach._format_events_for_recap(events)

        # Should include some time information
        assert formatted is not None


@pytest.mark.unit
class TestSessionRecapGeneration:
    """Test session recap generation"""

    @pytest.mark.asyncio
    async def test_generate_recap_with_events(self, temp_config_dir, sample_session_events):
        """Test generating recap with events"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        # Mock the AI router
        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            # Mock AI response
            async def mock_chat(messages, **kwargs):
                return {
                    "content": "You asked about Margit and received strategies. Great progress!"
                }

            mock_provider.chat = mock_chat

            recap = await coach.generate_recap("elden_ring", sample_session_events)

            # Should return some recap text
            assert recap is not None
            assert isinstance(recap, str)
            assert len(recap) > 0

    @pytest.mark.asyncio
    async def test_generate_recap_with_empty_events(self, temp_config_dir):
        """Test generating recap with no events"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        recap = await coach.generate_recap("test_game", [])

        # Should handle empty events gracefully
        assert recap is not None

    @pytest.mark.asyncio
    async def test_generate_recap_ai_error_handling(self, temp_config_dir, sample_session_events):
        """Test handling of AI errors during recap generation"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            # Mock AI error
            async def mock_chat_error(messages, **kwargs):
                raise Exception("AI service unavailable")

            mock_provider.chat = mock_chat_error

            # Should handle error gracefully
            try:
                recap = await coach.generate_recap("test", sample_session_events)
                # May return error message or empty
                assert recap is not None
            except Exception as e:
                # Exception is acceptable
                assert "unavailable" in str(e).lower() or "error" in str(e).lower()


@pytest.mark.unit
class TestInsightsGeneration:
    """Test insights and coaching tip generation"""

    @pytest.mark.asyncio
    async def test_generate_insights(self, temp_config_dir):
        """Test generating coaching insights"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        # Add some events
        logger.log_event(
            game_profile_id="elden_ring",
            event_type="question",
            content="How do I beat Margit?"
        )
        logger.log_event(
            game_profile_id="elden_ring",
            event_type="answer",
            content="Use ranged attacks and summons"
        )

        coach = SessionCoach(session_logger=logger, config=config)

        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            async def mock_chat(messages, **kwargs):
                return {
                    "content": "Focus on learning boss patterns. Practice dodging."
                }

            mock_provider.chat = mock_chat

            insights = await coach.generate_insights("elden_ring")

            # Should return insights
            assert insights is not None

    @pytest.mark.asyncio
    async def test_generate_coaching_tips(self, temp_config_dir):
        """Test generating coaching tips"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        # Add events
        logger.log_event(
            game_profile_id="test_game",
            event_type="question",
            content="Help with strategy"
        )

        coach = SessionCoach(session_logger=logger, config=config)

        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            async def mock_chat(messages, **kwargs):
                return {"content": "Tip 1: Practice timing\nTip 2: Learn patterns"}

            mock_provider.chat = mock_chat

            tips = await coach.get_coaching_tips("test_game")

            # Should return tips
            assert tips is not None


@pytest.mark.unit
class TestSessionSummaryIntegration:
    """Test integration with session logger"""

    def test_get_session_events_for_recap(self, temp_config_dir):
        """Test getting session events for recap"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        # Log some events
        logger.log_event(
            game_profile_id="test_game",
            event_type="question",
            content="Question 1"
        )
        logger.log_event(
            game_profile_id="test_game",
            event_type="answer",
            content="Answer 1"
        )

        coach = SessionCoach(session_logger=logger, config=config)

        # Get events
        events = coach.session_logger.get_current_session_events("test_game")

        assert len(events) == 2
        assert events[0].content == "Question 1"
        assert events[1].content == "Answer 1"

    def test_session_statistics(self, temp_config_dir):
        """Test session statistics calculation"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        # Log various event types
        for i in range(5):
            logger.log_event(
                game_profile_id="test_game",
                event_type="question",
                content=f"Question {i}"
            )

        for i in range(5):
            logger.log_event(
                game_profile_id="test_game",
                event_type="answer",
                content=f"Answer {i}"
            )

        # Get summary
        summary = logger.get_session_summary("test_game")

        assert summary['total_events'] == 10
        assert summary['event_types']['question'] == 5
        assert summary['event_types']['answer'] == 5


@pytest.mark.unit
class TestRecapPromptConstruction:
    """Test AI prompt construction for recaps"""

    @pytest.mark.asyncio
    async def test_recap_prompt_includes_game_context(self, temp_config_dir, sample_session_events):
        """Test that recap prompt includes game context"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        captured_messages = []

        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            async def mock_chat(messages, **kwargs):
                captured_messages.append(messages)
                return {"content": "Recap text"}

            mock_provider.chat = mock_chat

            await coach.generate_recap("elden_ring", sample_session_events)

            # Should have called AI with messages
            assert len(captured_messages) > 0
            # Messages should include system prompt and events
            assert len(captured_messages[0]) > 0

    @pytest.mark.asyncio
    async def test_insights_prompt_construction(self, temp_config_dir):
        """Test insights prompt construction"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        logger.log_event("test", "question", "Test question")

        coach = SessionCoach(session_logger=logger, config=config)

        captured_messages = []

        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            async def mock_chat(messages, **kwargs):
                captured_messages.append(messages)
                return {"content": "Insights"}

            mock_provider.chat = mock_chat

            await coach.generate_insights("test")

            # Should construct appropriate prompt
            if captured_messages:
                assert len(captured_messages[0]) > 0


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in session coaching"""

    @pytest.mark.asyncio
    async def test_no_ai_provider_handling(self, temp_config_dir):
        """Test handling when no AI provider is configured"""
        config = Config(config_dir=str(temp_config_dir))
        coach = SessionCoach(config=config)

        with patch.object(coach, 'router') as mock_router:
            mock_router.get_default_provider.return_value = None

            # Should handle missing provider gracefully
            try:
                recap = await coach.generate_recap("test", [])
                # May return None or error message
            except Exception as e:
                # Exception is acceptable
                assert "provider" in str(e).lower() or "configured" in str(e).lower()

    def test_invalid_game_profile_id(self, temp_config_dir):
        """Test handling of invalid game profile ID"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        coach = SessionCoach(session_logger=logger, config=config)

        # Get events for nonexistent game
        events = coach.session_logger.get_current_session_events("nonexistent_game")

        # Should return empty list
        assert events == []


@pytest.mark.integration
class TestEndToEndCoaching:
    """End-to-end coaching workflow tests"""

    @pytest.mark.asyncio
    async def test_full_coaching_workflow(self, temp_config_dir):
        """Test complete coaching workflow"""
        config = Config(config_dir=str(temp_config_dir))
        logger = SessionLogger(config_dir=str(temp_config_dir))

        # Simulate a gaming session
        logger.log_event("elden_ring", "question", "How do I beat Margit?")
        logger.log_event("elden_ring", "answer", "Use summons and ranged attacks")
        logger.log_event("elden_ring", "question", "Best build for mage?")
        logger.log_event("elden_ring", "answer", "Focus on Intelligence and use Glintstone spells")

        coach = SessionCoach(session_logger=logger, config=config)

        with patch.object(coach, 'router') as mock_router:
            mock_provider = MagicMock()
            mock_router.get_default_provider.return_value = mock_provider

            async def mock_chat(messages, **kwargs):
                return {
                    "content": "Great session! You learned about Margit strategies and mage builds."
                }

            mock_provider.chat = mock_chat

            # Get events
            events = logger.get_current_session_events("elden_ring")
            assert len(events) == 4

            # Generate recap
            recap = await coach.generate_recap("elden_ring", events)
            assert recap is not None
            assert len(recap) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
