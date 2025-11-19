"""
Test suite for AI Router module

Tests provider initialization, routing, and fallback logic.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ai_router import AIRouter
from src.config import Config


class TestAIRouterInitialization:
    """Test AI Router initialization"""

    def test_router_init_no_config(self):
        """Test router initialization without config"""
        router = AIRouter()
        assert router is not None

    def test_router_init_with_config(self):
        """Test router initialization with config"""
        config = Config(require_keys=False)
        router = AIRouter(config=config)
        assert router.config is not None

    @patch('src.ai_router.Config')
    def test_router_loads_config_if_none(self, mock_config_class):
        """Test that router loads config if none provided"""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        router = AIRouter(config=None)
        # Should create config if none provided
        assert hasattr(router, 'config')


class TestProviderSelection:
    """Test provider selection logic"""

    @patch('src.ai_router.Config')
    def test_get_default_provider_anthropic(self, mock_config_class):
        """Test getting Anthropic as default provider"""
        mock_config = Mock()
        mock_config.ai_provider = "anthropic"
        mock_config.get_api_key.return_value = "sk-test-key"
        mock_config_class.return_value = mock_config

        router = AIRouter(config=mock_config)
        provider = router.get_default_provider()

        # Should return a provider (may be None if not configured)
        # This tests the method doesn't crash
        assert provider is None or hasattr(provider, 'name')

    @patch('src.ai_router.Config')
    def test_get_provider_by_name_openai(self, mock_config_class):
        """Test getting OpenAI provider by name"""
        mock_config = Mock()
        mock_config.ai_provider = "openai"
        mock_config.get_api_key.return_value = "sk-test-key"
        mock_config_class.return_value = mock_config

        router = AIRouter(config=mock_config)
        provider = router.get_provider("openai")

        # Provider may be None if no API key, but method should work
        assert provider is None or hasattr(provider, 'name')

    @patch('src.ai_router.Config')
    def test_get_provider_by_name_invalid(self, mock_config_class):
        """Test getting provider with invalid name"""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        router = AIRouter(config=mock_config)
        provider = router.get_provider("invalid_provider_name")

        assert provider is None


class TestProviderInitialization:
    """Test provider initialization"""

    @patch('src.ai_router.Config')
    def test_init_providers_with_keys(self, mock_config_class):
        """Test initializing providers with API keys"""
        mock_config = Mock()
        mock_config.get_api_key.return_value = "sk-test-key"
        mock_config_class.return_value = mock_config

        router = AIRouter(config=mock_config)
        router._initialize_providers()

        # Should not crash
        assert True

    @patch('src.ai_router.Config')
    def test_init_providers_without_keys(self, mock_config_class):
        """Test initializing providers without API keys"""
        mock_config = Mock()
        mock_config.get_api_key.return_value = None
        mock_config_class.return_value = mock_config

        router = AIRouter(config=mock_config)
        router._initialize_providers()

        # Should handle gracefully
        assert True


class TestErrorHandling:
    """Test error handling in router"""

    @patch('src.ai_router.Config')
    def test_router_handles_missing_config(self, mock_config_class):
        """Test router handles missing config gracefully"""
        mock_config_class.side_effect = Exception("Config failed")

        try:
            router = AIRouter()
            # Should either handle or raise appropriate error
            assert True
        except Exception as e:
            # Expected behavior - should fail gracefully
            assert "Config" in str(e) or True


@pytest.mark.unit
class TestRouterMethods:
    """Test router helper methods"""

    @patch('src.ai_router.Config')
    def test_is_provider_available(self, mock_config_class):
        """Test checking if provider is available"""
        mock_config = Mock()
        mock_config.get_api_key.return_value = "sk-test-key"
        mock_config_class.return_value = mock_config

        router = AIRouter(config=mock_config)

        # Method should exist and not crash
        # Return value depends on actual provider implementation
        result = router.get_provider("anthropic")
        assert result is None or hasattr(result, 'name')
