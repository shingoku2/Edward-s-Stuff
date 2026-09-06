from unittest.mock import MagicMock

import pytest

from omnix.ai_assistant import AIAssistant
from omnix.providers import LLMProvider


def test_ai_assistant_uses_injected_provider():
    """Verify AIAssistant uses the injected LLMProvider."""
    mock_provider = MagicMock(spec=LLMProvider)
    mock_provider.generate_response.return_value = "Mocked AI Response"

    # Initialize assistant with the mock provider
    assistant = AIAssistant(provider=mock_provider)

    # Setup game context
    assistant.set_current_game({"name": "Test Game"})

    # Ask a question
    response = assistant.ask_question("What is the best weapon?")

    assert response == "Mocked AI Response"
    mock_provider.generate_response.assert_called_once()
