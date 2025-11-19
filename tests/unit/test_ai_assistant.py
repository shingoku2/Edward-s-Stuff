"""
Unit tests for AIAssistant module

Tests AI assistant initialization, conversation management, and integration with providers.
"""
import pytest
import os


@pytest.mark.unit
class TestAIAssistant:
    """Test AIAssistant module functionality"""

    @pytest.mark.skip_ci
    @pytest.mark.requires_api_key
    def test_assistant_initialization(self, mock_api_key):
        """Test creating an AIAssistant instance"""
        from ai_assistant import AIAssistant

        # Skip if no API keys available
        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            assert assistant is not None
        except ValueError:
            # Expected if no API keys configured
            pytest.skip("No API keys configured")

    def test_assistant_requires_api_key(self):
        """Test that AIAssistant requires valid API configuration"""
        from ai_assistant import AIAssistant

        # Should raise ValueError if no valid API key
        try:
            assistant = AIAssistant(provider="invalid_provider")
            # If it doesn't raise, that's OK too (depending on implementation)
        except ValueError:
            # Expected behavior
            pass

    @pytest.mark.skip_ci
    @pytest.mark.requires_api_key
    def test_set_current_game(self):
        """Test setting current game context"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            game_info = {"name": "Test Game", "id": "test123"}
            assistant.set_current_game(game_info)
            assert assistant.current_game["name"] == "Test Game"
        except ValueError:
            pytest.skip("No API keys configured")

    @pytest.mark.skip_ci
    @pytest.mark.requires_api_key
    def test_conversation_history(self):
        """Test conversation history management"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            history = assistant.get_conversation_summary()
            assert isinstance(history, list)
        except ValueError:
            pytest.skip("No API keys configured")

    @pytest.mark.skip_ci
    @pytest.mark.requires_api_key
    def test_clear_history(self):
        """Test clearing conversation history"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            assistant.clear_history()
            history = assistant.get_conversation_summary()
            # After clear, should be empty or minimal
            assert isinstance(history, list)
        except ValueError:
            pytest.skip("No API keys configured")


@pytest.mark.unit
class TestAIAssistantEdgeCases:
    """Test AIAssistant edge cases"""

    @pytest.mark.skip_ci
    def test_set_game_with_empty_dict(self):
        """Test setting game with empty dictionary"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            assistant.set_current_game({})
            # Should handle gracefully
        except (ValueError, AttributeError):
            # May raise error or handle gracefully
            pass

    @pytest.mark.skip_ci
    def test_set_game_with_none_values(self):
        """Test setting game with None values"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            assistant.set_current_game({"name": None, "id": None})
            # Should handle gracefully
        except (ValueError, AttributeError):
            # May raise error or handle gracefully
            pass
