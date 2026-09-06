from unittest.mock import MagicMock, patch

import pytest

from omnix.providers import LLMProvider, OpenAIProvider


def test_openai_provider_implementation():
    """Verify OpenAIProvider implements LLMProvider correctly."""
    provider = OpenAIProvider(
        api_key="sk-test", base_url="http://localhost:1234/v1", default_model="gpt-3.5-turbo"
    )
    assert isinstance(provider, LLMProvider)


@patch("requests.post")
def test_openai_provider_generate_response(mock_post):
    """Verify generate_response sends correct request and parses response."""
    provider = OpenAIProvider(
        api_key="sk-test", base_url="http://localhost:1234/v1", default_model="test-model"
    )

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response from OpenAI"}}]
    }
    mock_post.return_value = mock_response

    response = provider.generate_response(system_prompt="sys", user_prompt="hello")
    assert response == "Response from OpenAI"

    # Verify request payload
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["model"] == "test-model"
    assert kwargs["json"]["messages"][0]["role"] == "system"
    assert kwargs["json"]["messages"][1]["role"] == "user"


@patch("requests.get")
def test_openai_provider_health_check_success(mock_get):
    """Verify health_check returns True when API is reachable."""
    provider = OpenAIProvider(base_url="http://localhost:1234/v1")

    # Mock models endpoint
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    assert provider.health_check() is True


@patch("requests.get")
def test_openai_provider_health_check_failure(mock_get):
    """Verify health_check returns False when API is unreachable."""
    provider = OpenAIProvider(base_url="http://localhost:1234/v1")
    mock_get.side_effect = Exception("Connection error")

    assert provider.health_check() is False
