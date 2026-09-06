"""
Central AI Router

Simplified to use Ollama only for local/remote model inference.
Handles provider instantiation, error handling, and model management.
"""

import logging
from typing import Any, Dict, List, Optional

from omnix.config import Config
from omnix.providers import (
    OllamaProvider,
    ProviderConnectionError,
    ProviderError,
    create_provider,
)

logger = logging.getLogger(__name__)


class AIRouter:
    """Central router for AI provider requests (Ollama-only)"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the AI router.

        Args:
            config: Config instance (if None, creates a new one)
        """
        self.config = config or Config()
        self._provider: Optional[OllamaProvider] = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the Ollama provider"""
        try:
            base_url = self.config.ollama_host
            default_model = self.config.ollama_model

            self._provider = create_provider(
                "ollama", base_url=base_url, default_model=default_model
            )
            logger.info(f"Initialized Ollama provider at {base_url}")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama provider: {e}")

    def get_provider(self, provider_name: Optional[str] = None) -> Optional[OllamaProvider]:
        """
        Get the Ollama provider.

        Args:
            provider_name: Ignored (kept for API compatibility)

        Returns:
            OllamaProvider instance or None if not available
        """
        return self._provider

    def get_default_provider(self) -> Optional[OllamaProvider]:
        """
        Get the default provider (Ollama).

        Returns:
            OllamaProvider instance or None if not available
        """
        return self._provider

    def list_configured_providers(self) -> List[str]:
        """
        Get list of configured providers.

        Returns:
            List containing 'ollama' if configured, empty otherwise
        """
        if self._provider and self._provider.is_configured():
            return ["ollama"]
        return []

    def list_models(self) -> List[str]:
        """
        List available models from Ollama.

        Returns:
            List of model names
        """
        if self._provider:
            return self._provider.list_models()
        return []

    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Send a chat request to Ollama.

        Args:
            messages: Conversation messages with 'role' and 'content'
            provider: Ignored (kept for API compatibility)
            model: Specific model to use (optional)
            **kwargs: Additional parameters

        Returns:
            Response dict with 'content' and provider-specific fields

        Raises:
            ProviderConnectionError: If Ollama is not available
            ProviderError: If the request fails
        """
        if not self._provider:
            raise ProviderConnectionError(
                "Ollama is not configured.\n\n"
                "Please ensure:\n"
                "1. Ollama is installed (https://ollama.com)\n"
                "2. The Ollama daemon is running\n"
                "3. You have at least one model pulled (e.g., 'ollama pull llama3')"
            )

        if not self._provider.is_configured():
            raise ProviderConnectionError(
                "Ollama client is not initialized.\n\n"
                "Please ensure the 'ollama' Python package is installed:\n"
                "pip install ollama"
            )

        try:
            response = self._provider.chat(messages, model=model, **kwargs)
            return response

        except ProviderConnectionError as e:
            raise ProviderConnectionError(
                f"Failed to connect to Ollama: {str(e)}\n\n"
                f"Please ensure Ollama is running at {self.config.ollama_host}"
            )
        except ProviderError as e:
            raise ProviderError(f"Ollama error: {str(e)}")

    def test_provider(self, provider_name: Optional[str] = None) -> tuple[bool, str]:
        """
        Test connection to Ollama.

        Args:
            provider_name: Ignored (kept for API compatibility)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self._provider:
            return False, "Ollama provider not initialized"

        try:
            health = self._provider.test_connection()
            return health.is_healthy, health.message
        except Exception as e:
            return False, f"Test failed: {str(e)}"

    def get_provider_status(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status information for Ollama.

        Args:
            provider_name: Ignored (kept for API compatibility)

        Returns:
            Dict with provider status information
        """
        if not self._provider:
            return {
                "name": "ollama",
                "configured": False,
                "message": "Provider not initialized",
            }

        health = self._provider.test_connection()
        return {
            "name": "ollama",
            "configured": self._provider.is_configured(),
            "healthy": health.is_healthy,
            "message": health.message,
            "error_type": health.error_type,
            "details": health.details or {},
        }

    def set_model(self, model: str) -> None:
        """
        Set the default model for Ollama.

        Args:
            model: Model name (e.g., 'llama3', 'mistral')
        """
        if self._provider:
            self._provider.default_model = model
            self.config.ollama_model = model
            logger.info(f"Updated default model to: {model}")

    def set_host(self, host: str) -> None:
        """
        Set the Ollama host URL and reinitialize the provider.

        Args:
            host: Ollama host URL (e.g., 'http://localhost:11434')
        """
        self.config.ollama_host = host
        self._initialize_provider()
        logger.info(f"Updated Ollama host to: {host}")

    def reload_providers(self) -> None:
        """
        Reload the Ollama provider from the current config.

        This is useful when configuration has been updated.
        """
        logger.info("Reloading Ollama provider from config")
        self._initialize_provider()


# Global router instance
_router: Optional[AIRouter] = None


def get_router(config: Optional[Config] = None) -> AIRouter:
    """
    Get or create the global AI router instance.

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
