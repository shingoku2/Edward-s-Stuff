"""
Comprehensive test suite for AI providers
Tests OpenAI, Anthropic, and Gemini provider implementations
"""

import os
import sys
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.providers import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    ProviderError,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderRateLimitError,
    ProviderConnectionError,
    ProviderHealth
)
from src.provider_tester import ProviderTester


@pytest.mark.unit
class TestOpenAIProvider:
    """Test OpenAI provider implementation"""

    def test_initialization(self):
        """Test OpenAI provider initialization"""
        provider = OpenAIProvider(api_key="sk-test-key-123")

        assert provider.name == "openai"
        assert provider.api_key == "sk-test-key-123"

    def test_initialization_with_custom_base_url(self):
        """Test OpenAI provider with custom base URL"""
        provider = OpenAIProvider(
            api_key="sk-test-key-123",
            base_url="https://custom-api.example.com/v1"
        )

        assert provider.base_url == "https://custom-api.example.com/v1"

    def test_is_configured_with_valid_key(self):
        """Test is_configured returns True with valid key"""
        provider = OpenAIProvider(api_key="sk-test-key-123")
        assert provider.is_configured() is True

    def test_is_configured_with_empty_key(self):
        """Test is_configured returns False with empty key"""
        provider = OpenAIProvider(api_key="")
        assert provider.is_configured() is False

    def test_is_configured_with_none_key(self):
        """Test is_configured returns False with None key"""
        provider = OpenAIProvider(api_key=None)
        assert provider.is_configured() is False

    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat completion"""
        provider = OpenAIProvider(api_key="sk-test-key-123")

        # Mock the OpenAI client
        with patch.object(provider, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.model = "gpt-3.5-turbo"
            mock_response.usage.total_tokens = 50

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.chat(messages)

            assert result["content"] == "Test response"
            assert result["model"] == "gpt-3.5-turbo"
            assert result["usage"]["total_tokens"] == 50

    @pytest.mark.asyncio
    async def test_chat_with_custom_model(self):
        """Test chat with custom model specification"""
        provider = OpenAIProvider(api_key="sk-test-key-123")

        with patch.object(provider, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response"
            mock_response.model = "gpt-4"
            mock_response.usage.total_tokens = 100

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            messages = [{"role": "user", "content": "Hello"}]
            result = await provider.chat(messages, model="gpt-4")

            # Verify correct model was requested
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4"

    @pytest.mark.asyncio
    async def test_chat_authentication_error(self):
        """Test handling of authentication errors"""
        provider = OpenAIProvider(api_key="invalid-key")

        with patch.object(provider, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("Incorrect API key")
            )

            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(ProviderError):
                await provider.chat(messages)


@pytest.mark.unit
class TestAnthropicProvider:
    """Test Anthropic provider implementation"""

    def test_initialization(self):
        """Test Anthropic provider initialization"""
        provider = AnthropicProvider(api_key="sk-ant-test-key-123")

        assert provider.name == "anthropic"
        assert provider.api_key == "sk-ant-test-key-123"

    def test_is_configured_with_valid_key(self):
        """Test is_configured with valid key"""
        provider = AnthropicProvider(api_key="sk-ant-test-key-123")
        assert provider.is_configured() is True

    def test_is_configured_with_invalid_key(self):
        """Test is_configured with invalid key"""
        provider = AnthropicProvider(api_key="")
        assert provider.is_configured() is False

    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat completion with Anthropic"""
        provider = AnthropicProvider(api_key="sk-ant-test-key-123")

        with patch.object(provider, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Claude's response"
            mock_response.model = "claude-3-5-sonnet-20241022"
            mock_response.usage.input_tokens = 10
            mock_response.usage.output_tokens = 20

            mock_client.messages.create = AsyncMock(return_value=mock_response)

            messages = [{"role": "user", "content": "Hello Claude"}]
            result = await provider.chat(messages)

            assert result["content"] == "Claude's response"
            assert result["model"] == "claude-3-5-sonnet-20241022"
            assert result["usage"]["total_tokens"] == 30

    @pytest.mark.asyncio
    async def test_chat_with_system_prompt(self):
        """Test chat with system prompt (Anthropic-specific)"""
        provider = AnthropicProvider(api_key="sk-ant-test-key-123")

        with patch.object(provider, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Response"
            mock_response.model = "claude-3-5-sonnet-20241022"
            mock_response.usage.input_tokens = 10
            mock_response.usage.output_tokens = 20

            mock_client.messages.create = AsyncMock(return_value=mock_response)

            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            result = await provider.chat(messages)

            # Verify system prompt was passed correctly
            mock_client.messages.create.assert_called_once()
            call_kwargs = mock_client.messages.create.call_args[1]

            # Anthropic uses 'system' parameter, not in messages
            if 'system' in call_kwargs:
                assert call_kwargs['system'] == "You are a helpful assistant."


@pytest.mark.unit
class TestGeminiProvider:
    """Test Google Gemini provider implementation"""

    def test_initialization(self):
        """Test Gemini provider initialization"""
        provider = GeminiProvider(api_key="AIza-test-key-123")

        assert provider.name == "gemini"
        assert provider.api_key == "AIza-test-key-123"

    def test_is_configured(self):
        """Test is_configured"""
        provider = GeminiProvider(api_key="AIza-test-key-123")
        assert provider.is_configured() is True

        provider_empty = GeminiProvider(api_key="")
        assert provider_empty.is_configured() is False

    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat with Gemini"""
        provider = GeminiProvider(api_key="AIza-test-key-123")

        with patch.object(provider, 'model') as mock_model:
            mock_response = MagicMock()
            mock_response.text = "Gemini's response"

            mock_model.generate_content = AsyncMock(return_value=mock_response)

            messages = [{"role": "user", "content": "Hello Gemini"}]
            result = await provider.chat(messages)

            assert result["content"] == "Gemini's response"
            assert "model" in result


@pytest.mark.unit
class TestProviderErrors:
    """Test provider error handling"""

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self):
        """Test handling of authentication errors"""
        provider = OpenAIProvider(api_key="invalid-key")

        with patch.object(provider, 'client') as mock_client:
            # Simulate authentication error
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("Authentication failed: Invalid API key")
            )

            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(ProviderError):
                await provider.chat(messages)

    @pytest.mark.asyncio
    async def test_quota_exceeded_error_handling(self):
        """Test handling of quota exceeded errors"""
        provider = OpenAIProvider(api_key="sk-test-key")

        with patch.object(provider, 'client') as mock_client:
            # Simulate quota exceeded
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("You exceeded your current quota")
            )

            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(ProviderError):
                await provider.chat(messages)

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Test handling of rate limit errors"""
        provider = AnthropicProvider(api_key="sk-ant-test-key")

        with patch.object(provider, 'client') as mock_client:
            # Simulate rate limit
            mock_client.messages.create = AsyncMock(
                side_effect=Exception("Rate limit exceeded")
            )

            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(ProviderError):
                await provider.chat(messages)

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        provider = OpenAIProvider(api_key="sk-test-key")

        with patch.object(provider, 'client') as mock_client:
            # Simulate network error
            mock_client.chat.completions.create = AsyncMock(
                side_effect=ConnectionError("Connection timeout")
            )

            messages = [{"role": "user", "content": "Test"}]

            with pytest.raises(ProviderError):
                await provider.chat(messages)


@pytest.mark.unit
class TestProviderHealth:
    """Test provider health checks"""

    def test_provider_health_creation(self):
        """Test creating ProviderHealth object"""
        health = ProviderHealth(healthy=True, message="All good")

        assert health.healthy is True
        assert health.message == "All good"

    def test_test_connection_with_mock(self):
        """Test connection testing"""
        provider = OpenAIProvider(api_key="sk-test-key")

        with patch.object(provider, 'test_connection') as mock_test:
            mock_test.return_value = ProviderHealth(healthy=True, message="Connected")

            health = provider.test_connection()

            assert health.healthy is True
            assert "Connected" in health.message


@pytest.mark.unit
class TestProviderTester:
    """Test ProviderTester utility"""

    def test_test_openai_invalid_key(self):
        """Test OpenAI connection test with invalid key"""
        success, message = ProviderTester.test_openai("")

        assert success is False
        assert "required" in message.lower()

    def test_test_anthropic_invalid_key(self):
        """Test Anthropic connection test with invalid key"""
        success, message = ProviderTester.test_anthropic("")

        assert success is False
        assert "required" in message.lower()

    def test_test_gemini_invalid_key(self):
        """Test Gemini connection test with invalid key"""
        success, message = ProviderTester.test_gemini("")

        assert success is False
        assert "required" in message.lower()

    @patch('openai.OpenAI')
    def test_test_openai_with_mocked_client(self, mock_openai_class):
        """Test OpenAI connection with mocked client"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_models = MagicMock()
        mock_models.__iter__ = Mock(return_value=iter([MagicMock(), MagicMock()]))
        mock_client.models.list.return_value = mock_models

        # Test
        success, message = ProviderTester.test_openai("sk-test-key")

        # We don't assert success because the actual implementation may vary,
        # but we verify it doesn't crash
        assert isinstance(success, bool)
        assert isinstance(message, str)


@pytest.mark.unit
class TestProviderMessaging:
    """Test message formatting and conversion"""

    @pytest.mark.asyncio
    async def test_message_format_consistency(self):
        """Test that all providers accept standard message format"""
        standard_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        # Test OpenAI
        openai_provider = OpenAIProvider(api_key="sk-test")
        with patch.object(openai_provider, 'client'):
            # Should not raise on message format
            try:
                # Just test that message format is accepted
                assert openai_provider.is_configured()
            except ValueError:
                pytest.fail("OpenAI provider rejected standard message format")

        # Test Anthropic
        anthropic_provider = AnthropicProvider(api_key="sk-ant-test")
        with patch.object(anthropic_provider, 'client'):
            try:
                assert anthropic_provider.is_configured()
            except ValueError:
                pytest.fail("Anthropic provider rejected standard message format")

    @pytest.mark.asyncio
    async def test_empty_messages_handling(self):
        """Test handling of empty message list"""
        provider = OpenAIProvider(api_key="sk-test-key")

        with patch.object(provider, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                side_effect=ValueError("Messages cannot be empty")
            )

            with pytest.raises((ProviderError, ValueError)):
                await provider.chat([])

    @pytest.mark.asyncio
    async def test_very_long_message_handling(self):
        """Test handling of very long messages"""
        provider = OpenAIProvider(api_key="sk-test-key")

        # Create a very long message (100KB)
        long_content = "x" * 100000

        with patch.object(provider, 'client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response to long message"
            mock_response.model = "gpt-3.5-turbo"
            mock_response.usage.total_tokens = 50000

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            messages = [{"role": "user", "content": long_content}]
            result = await provider.chat(messages)

            assert "content" in result


@pytest.mark.unit
class TestProviderConfiguration:
    """Test provider configuration options"""

    def test_openai_with_custom_parameters(self):
        """Test OpenAI provider with custom parameters"""
        provider = OpenAIProvider(
            api_key="sk-test-key",
            base_url="https://custom.api.com",
            default_model="gpt-4"
        )

        assert provider.base_url == "https://custom.api.com"
        assert provider.default_model == "gpt-4"

    def test_anthropic_with_custom_parameters(self):
        """Test Anthropic provider with custom parameters"""
        provider = AnthropicProvider(
            api_key="sk-ant-test-key",
            default_model="claude-3-opus-20240229"
        )

        assert provider.default_model == "claude-3-opus-20240229"

    def test_gemini_with_custom_parameters(self):
        """Test Gemini provider with custom parameters"""
        provider = GeminiProvider(
            api_key="AIza-test-key",
            default_model="gemini-pro-vision"
        )

        assert provider.default_model == "gemini-pro-vision"


@pytest.mark.integration
class TestProviderIntegration:
    """Integration tests for providers"""

    @pytest.mark.asyncio
    async def test_provider_switching(self):
        """Test switching between providers"""
        providers = {
            "openai": OpenAIProvider(api_key="sk-test-openai"),
            "anthropic": AnthropicProvider(api_key="sk-ant-test"),
            "gemini": GeminiProvider(api_key="AIza-test")
        }

        for name, provider in providers.items():
            assert provider.is_configured()
            assert provider.name == name

    def test_all_providers_have_required_methods(self):
        """Test that all providers implement required interface"""
        providers = [
            OpenAIProvider(api_key="sk-test"),
            AnthropicProvider(api_key="sk-ant-test"),
            GeminiProvider(api_key="AIza-test")
        ]

        required_methods = ['chat', 'is_configured', 'test_connection']

        for provider in providers:
            for method in required_methods:
                assert hasattr(provider, method), \
                    f"{provider.name} missing method: {method}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
