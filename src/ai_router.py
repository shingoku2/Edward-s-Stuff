"""
Central AI Router

High-level abstraction for routing chat requests to the appropriate AI provider.
Handles provider instantiation, error handling, and fallback logic.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from config import Config
from providers import (
    AIProvider,
    AnthropicProvider,
    create_provider,
    ProviderAuthError,
    ProviderError,
    ProviderQuotaError,
    ProviderRateLimitError,
)

logger = logging.getLogger(__name__)


class AIRouter:
    """Central router for AI provider requests"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the AI router

        Args:
            config: Config instance (if None, creates a new one)
        """
        self.config = config or Config()
        self._providers: Dict[str, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers with their API keys"""
        for provider_name in ["openai", "anthropic", "gemini"]:
            api_key = self.config.get_api_key(provider_name)
            if api_key:
                try:
                    self._providers[provider_name] = create_provider(
                        provider_name,
                        api_key=api_key
                    )
                    logger.debug(f"Initialized provider: {provider_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize {provider_name}: {e}")

    def get_default_provider(self) -> Optional[Any]:
        """
        Get the default AI provider

        Returns the configured provider if it has an API key, otherwise returns
        the first available provider with a key.

        Returns:
            Provider instance or None if no providers are configured
        """
        # Try to get the effective provider from config
        effective_provider_name = self.config.get_effective_provider()

        if effective_provider_name in self._providers:
            return self._providers[effective_provider_name]

        # Fallback to first available provider
        for provider_name, provider in self._providers.items():
            if provider.is_configured():
                logger.debug(f"Using fallback provider: {provider_name}")
                return provider

        return None

    def get_provider(self, provider_name: str) -> Optional[Any]:
        """
        Get a specific provider by name

        Args:
            provider_name: 'openai', 'anthropic', or 'gemini'

        Returns:
            Provider instance or None if not available
        """
        return self._providers.get(provider_name.lower())

    def list_configured_providers(self) -> List[str]:
        """
        Get list of configured providers

        Returns:
            List of provider names that are configured with API keys
        """
        return list(self._providers.keys())

    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a chat request to the appropriate AI provider

        Args:
            messages: Conversation messages with 'role' and 'content'
            provider: Specific provider to use (default: uses effective provider)
            model: Specific model to use (provider-specific)
            **kwargs: Additional provider-specific parameters

        Returns:
            Response dict with 'content' and provider-specific fields

        Raises:
            ProviderAuthError: If no API key is configured
            ProviderError: If the provider request fails
        """
        # Determine which provider to use
        if provider:
            target_provider = self.get_provider(provider)
            if not target_provider:
                raise ProviderAuthError(
                    f"Provider '{provider}' is not configured. "
                    f"Available: {', '.join(self.list_configured_providers())}"
                )
        else:
            target_provider = self.get_default_provider()
            if not target_provider:
                raise ProviderAuthError(
                    "No AI provider is configured. "
                    "Please configure at least one provider via Settings > AI Providers."
                )

        try:
            # Send the request
            response = target_provider.chat(messages, model=model, **kwargs)
            return response

        except ProviderAuthError as e:
            raise ProviderAuthError(
                f"Authentication failed with {target_provider.name}: {str(e)}\n"
                f"Please check your API key in Settings > AI Providers."
            )
        except ProviderQuotaError as e:
            raise ProviderQuotaError(
                f"Quota exceeded for {target_provider.name}: {str(e)}\n"
                f"Please check your account settings for {target_provider.name}."
            )
        except ProviderRateLimitError as e:
            raise ProviderRateLimitError(
                f"Rate limited by {target_provider.name}: {str(e)}\n"
                f"Please try again in a moment."
            )
        except ProviderError as e:
            raise ProviderError(
                f"Request failed with {target_provider.name}: {str(e)}"
            )

    def test_provider(self, provider_name: str) -> tuple[bool, str]:
        """
        Test connection to a provider

        Args:
            provider_name: 'openai', 'anthropic', or 'gemini'

        Returns:
            Tuple of (success: bool, message: str)
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return False, f"Provider '{provider_name}' is not configured"

        try:
            health = provider.test_connection()
            return health.is_healthy, health.message
        except Exception as e:
            return False, f"Test failed: {str(e)}"

    def set_api_key(self, provider_name: str, api_key: str) -> bool:
        """
        Set or update an API key for a provider

        Args:
            provider_name: 'openai', 'anthropic', or 'gemini'
            api_key: The API key to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Save to config
            self.config.set_api_key(provider_name, api_key)

            # Reinitialize the provider with the new key
            self._providers[provider_name.lower()] = create_provider(
                provider_name,
                api_key=api_key
            )
            logger.info(f"Updated API key for provider: {provider_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to set API key for {provider_name}: {e}")
            return False

    def clear_api_key(self, provider_name: str) -> bool:
        """
        Clear an API key for a provider

        Args:
            provider_name: 'openai', 'anthropic', or 'gemini'

        Returns:
            True if successful, False otherwise
        """
        try:
            self.config.clear_api_key(provider_name)
            provider_name_lower = provider_name.lower()
            if provider_name_lower in self._providers:
                del self._providers[provider_name_lower]
            logger.info(f"Cleared API key for provider: {provider_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear API key for {provider_name}: {e}")
            return False

    def get_provider_status(self, provider_name: str) -> Dict[str, Any]:
        """
        Get status information for a provider

        Args:
            provider_name: 'openai', 'anthropic', or 'gemini'

        Returns:
            Dict with provider status information
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {
                "name": provider_name,
                "configured": False,
                "message": f"Provider not configured"
            }

        health = provider.test_connection()
        return {
            "name": provider_name,
            "configured": provider.is_configured(),
            "healthy": health.is_healthy,
            "message": health.message,
            "error_type": health.error_type,
            "details": health.details or {}
        }


# Global router instance
_router: Optional[AIRouter] = None


def get_router(config: Optional[Config] = None) -> AIRouter:
    """
    Get or create the global AI router instance

    Args:
        config: Optional Config instance to use

    Returns:
        The global AIRouter instance
    """
    global _router
    if _router is None:
        _router = AIRouter(config=config)
    return _router


def reset_router():
    """Reset the global router instance (useful for testing)"""
    global _router
    _router = None
