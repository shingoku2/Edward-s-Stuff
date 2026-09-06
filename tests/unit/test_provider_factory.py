import pytest

from omnix.providers import MockProvider, OllamaProvider, OpenAIProvider, get_provider


def test_get_provider_ollama():
    """Verify factory returns OllamaProvider for 'ollama'."""
    config = {"AI_PROVIDER": "ollama", "OLLAMA_BASE_URL": "http://localhost:11434"}
    provider = get_provider(config)
    assert isinstance(provider, OllamaProvider)


def test_get_provider_openai():
    """Verify factory returns OpenAIProvider for 'openai_compatible'."""
    config = {
        "AI_PROVIDER": "openai_compatible",
        "AI_BASE_URL": "http://localhost:1234/v1",
        "AI_MODEL": "test-model",
    }
    provider = get_provider(config)
    assert isinstance(provider, OpenAIProvider)


def test_get_provider_mock():
    """Verify factory returns MockProvider for 'mock'."""
    config = {"AI_PROVIDER": "mock"}
    provider = get_provider(config)
    assert isinstance(provider, MockProvider)


def test_get_provider_invalid():
    """Verify factory raises ValueError for unknown provider."""
    config = {"AI_PROVIDER": "invalid"}
    with pytest.raises(ValueError, match="Unknown provider: invalid"):
        get_provider(config)
