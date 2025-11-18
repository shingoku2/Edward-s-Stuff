"""
Test suite for AI Providers

Tests OpenAI, Anthropic, and Google Gemini provider implementations.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from src.providers import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    ProviderError,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderRateLimitError,
    ProviderConnectionError
)


class TestProviderExceptions:
    """Test provider exception hierarchy"""

    def test_provider_error_base(self):
        """Test base ProviderError exception"""
        error = ProviderError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_provider_auth_error(self):
        """Test ProviderAuthError exception"""
        error = ProviderAuthError("Invalid API key")
        assert isinstance(error, ProviderError)
        assert "Invalid API key" in str(error)

    def test_provider_quota_error(self):
        """Test ProviderQuotaError exception"""
        error = ProviderQuotaError("Quota exceeded")
        assert isinstance(error, ProviderError)

    def test_provider_rate_limit_error(self):
        """Test ProviderRateLimitError exception"""
        error = ProviderRateLimitError("Rate limited")
        assert isinstance(error, ProviderError)

    def test_provider_connection_error(self):
        """Test ProviderConnectionError exception"""
        error = ProviderConnectionError("Connection failed")
        assert isinstance(error, ProviderError)


@pytest.mark.unit
class TestOpenAIProvider:
    """Test OpenAI provider"""

    def test_openai_provider_init(self):
        """Test OpenAI provider initialization"""
        provider = OpenAIProvider(api_key="sk-test-key")
        assert provider.name == "openai"
        assert provider.api_key == "sk-test-key"

    def test_openai_provider_is_configured(self):
        """Test checking if provider is configured"""
        provider = OpenAIProvider(api_key="sk-test-key")
        assert provider.is_configured() is True

        provider_no_key = OpenAIProvider(api_key=None)
        assert provider_no_key.is_configured() is False

    def test_openai_provider_init_no_key(self):
        """Test OpenAI provider with no API key"""
        provider = OpenAIProvider(api_key=None)
        assert provider.is_configured() is False

    @pytest.mark.asyncio
    @patch('src.providers.openai.AsyncOpenAI')
    async def test_openai_chat_basic(self, mock_openai_class):
        """Test basic OpenAI chat"""
        # Mock the client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.model = "gpt-4"
        mock_response.usage = None

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="sk-test-key")
        provider.client = mock_client

        messages = [{"role": "user", "content": "Test"}]
        result = await provider.chat(messages)

        assert result["content"] == "Test response"
        assert result["model"] == "gpt-4"


@pytest.mark.unit
class TestAnthropicProvider:
    """Test Anthropic provider"""

    def test_anthropic_provider_init(self):
        """Test Anthropic provider initialization"""
        provider = AnthropicProvider(api_key="sk-ant-test-key")
        assert provider.name == "anthropic"
        assert provider.api_key == "sk-ant-test-key"

    def test_anthropic_provider_is_configured(self):
        """Test checking if Anthropic provider is configured"""
        provider = AnthropicProvider(api_key="sk-ant-test-key")
        assert provider.is_configured() is True

        provider_no_key = AnthropicProvider(api_key=None)
        assert provider_no_key.is_configured() is False

    @pytest.mark.asyncio
    @patch('src.providers.anthropic.AsyncAnthropic')
    async def test_anthropic_chat_basic(self, mock_anthropic_class):
        """Test basic Anthropic chat"""
        # Mock the client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Test response from Claude"
        mock_response.model = "claude-3-sonnet"
        mock_response.usage = None

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key="sk-ant-test-key")
        provider.client = mock_client

        messages = [{"role": "user", "content": "Test"}]
        result = await provider.chat(messages)

        assert result["content"] == "Test response from Claude"
        assert result["model"] == "claude-3-sonnet"


@pytest.mark.unit
class TestGeminiProvider:
    """Test Google Gemini provider"""

    def test_gemini_provider_init(self):
        """Test Gemini provider initialization"""
        provider = GeminiProvider(api_key="test-gemini-key")
        assert provider.name == "gemini"
        assert provider.api_key == "test-gemini-key"

    def test_gemini_provider_is_configured(self):
        """Test checking if Gemini provider is configured"""
        provider = GeminiProvider(api_key="test-key")
        assert provider.is_configured() is True

        provider_no_key = GeminiProvider(api_key=None)
        assert provider_no_key.is_configured() is False


@pytest.mark.unit
class TestProviderCommonBehavior:
    """Test common behavior across all providers"""

    @pytest.mark.parametrize("provider_class,api_key", [
        (OpenAIProvider, "sk-test"),
        (AnthropicProvider, "sk-ant-test"),
        (GeminiProvider, "gemini-test")
    ])
    def test_all_providers_have_name(self, provider_class, api_key):
        """Test all providers have a name attribute"""
        provider = provider_class(api_key=api_key)
        assert hasattr(provider, 'name')
        assert isinstance(provider.name, str)
        assert len(provider.name) > 0

    @pytest.mark.parametrize("provider_class,api_key", [
        (OpenAIProvider, "sk-test"),
        (AnthropicProvider, "sk-ant-test"),
        (GeminiProvider, "gemini-test")
    ])
    def test_all_providers_have_is_configured(self, provider_class, api_key):
        """Test all providers have is_configured method"""
        provider = provider_class(api_key=api_key)
        assert hasattr(provider, 'is_configured')
        assert callable(provider.is_configured)

    @pytest.mark.parametrize("provider_class", [
        OpenAIProvider,
        AnthropicProvider,
        GeminiProvider
    ])
    def test_all_providers_handle_no_api_key(self, provider_class):
        """Test all providers handle missing API key"""
        provider = provider_class(api_key=None)
        assert provider.is_configured() is False
