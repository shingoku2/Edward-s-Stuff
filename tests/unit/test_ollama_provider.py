from unittest.mock import MagicMock, patch

import pytest

from omnix.providers import LLMProvider, OllamaProvider


@pytest.fixture
def mock_ollama_client():
    with patch("ollama.Client") as mock:
        yield mock


def test_ollama_provider_implementation(mock_ollama_client):
    """Verify OllamaProvider implements LLMProvider correctly."""
    provider = OllamaProvider(base_url="http://localhost:11434", default_model="llama3")
    assert isinstance(provider, LLMProvider)

    # Mock chat response
    mock_client_instance = mock_ollama_client.return_value
    mock_client_instance.chat.return_value = {
        "message": {"content": "Hello from Ollama"},
        "model": "llama3",
        "done_reason": "stop",
        "usage": {},
    }

    response = provider.generate_response(system_prompt="sys", user_prompt="hello")
    assert response == "Hello from Ollama"
    mock_client_instance.chat.assert_called_once()


def test_ollama_provider_health_check_success(mock_ollama_client):
    """Verify health_check returns True when Ollama is reachable."""
    provider = OllamaProvider()
    mock_client_instance = mock_ollama_client.return_value
    mock_client_instance.list.return_value = {"models": [{"name": "llama3"}]}

    assert provider.health_check() is True


def test_ollama_provider_health_check_failure(mock_ollama_client):
    """Verify health_check returns False when Ollama is unreachable."""
    provider = OllamaProvider()
    mock_client_instance = mock_ollama_client.return_value
    mock_client_instance.list.side_effect = Exception("Connection failed")

    assert provider.health_check() is False
