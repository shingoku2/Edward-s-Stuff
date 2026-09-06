"""
AI Provider Abstraction Layer

Simplified to use Ollama only for local/remote model inference.
No API keys required - just point to your Ollama instance.
"""

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import requests

# Ensure imports using either ``providers`` or ``omnix.providers`` resolve to the
# same module instance so exception classes remain identical across import
# styles.
_current_module = sys.modules[__name__]

if __name__ == "omnix.providers":
    sys.modules["providers"] = _current_module
elif __name__ == "providers":
    sys.modules["omnix.providers"] = _current_module
else:
    sys.modules.setdefault("providers", _current_module)
    sys.modules.setdefault("omnix.providers", _current_module)

logger = logging.getLogger(__name__)


class AwaitableDict(dict):
    """Dictionary that can be awaited for async test compatibility."""

    def __await__(self):
        async def _wrapper():
            return self

        return _wrapper().__await__()


@dataclass
class ProviderHealth:
    """Health status of a provider"""

    is_healthy: bool
    message: str
    error_type: Optional[str] = None  # 'connection', etc.
    details: Optional[Dict[str, Any]] = None

    @property
    def healthy(self) -> bool:
        """Backward-compatible alias used by tests."""
        return self.is_healthy


class ProviderError(Exception):
    """Base exception for provider-related errors"""

    pass


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to provider"""

    pass


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify connection to the provider."""
        pass


class MockProvider(LLMProvider):
    """Mock provider for testing purposes."""

    def __init__(self, response_text: str = "Mock response"):
        self.response_text = response_text

    def generate_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        return self.response_text

    def health_check(self) -> bool:
        return True


class AIProvider(Protocol):
    """Protocol defining the interface all AI providers must implement"""

    name: str

    def is_configured(self) -> bool:
        """Check if provider has valid configuration"""
        ...

    def test_connection(self) -> ProviderHealth:
        """Test connection to the provider with a lightweight call"""
        ...

    def chat(
        self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a chat message to the provider

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model name to override default
            **kwargs: Additional provider-specific parameters

        Returns:
            Response dict with 'content' and provider-specific fields
        """
        ...


class OllamaProvider(LLMProvider):
    """
    Ollama provider implementation (local or remote).

    Ollama runs models locally without requiring API keys.
    Can also connect to remote Ollama instances.
    """

    name = "ollama"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        """
        Initialize Ollama provider.

        Args:
            api_key: Optional API key (for secured Ollama endpoints)
            base_url: Ollama host URL (default: http://localhost:11434)
            default_model: Default model to use (default: llama3)
        """
        self.api_key = api_key  # Included for API-compatibility; typically not required.
        self.base_url = base_url or "http://localhost:11434"
        self.default_model = default_model or "llama3"
        self.client: Any = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Ollama client."""
        try:
            import ollama

            self.client = ollama.Client(host=self.base_url)
        except ImportError:
            logger.warning("Ollama library not installed. Install with: pip install ollama")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama client: {e}")

    def is_configured(self) -> bool:
        """Ollama is configured if a client is available (no key required)."""
        return self.client is not None

    def generate_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: The system instructions
            user_prompt: The user's query
            context: Additional context to prepend to the user prompt

        Returns:
            The generated response string
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\n{user_prompt}" if context else user_prompt},
        ]
        response = self.chat(messages)
        return response.get("content", "")

    def health_check(self) -> bool:
        """Verify connection to the provider."""
        try:
            return self.test_connection().is_healthy
        except Exception:
            return False

    def test_connection(self) -> ProviderHealth:
        """Test connectivity to the Ollama daemon."""
        if not self.is_configured():
            return ProviderHealth(
                is_healthy=False,
                message="Ollama client not initialized - ensure the 'ollama' package is installed",
                error_type="connection",
            )

        if self.client is None:
            raise ProviderConnectionError("Client not initialized")

        try:
            models = self.client.list().get("models", [])
            model_names = [m.get("name", "unknown") for m in models]

            if models:
                return ProviderHealth(
                    is_healthy=True,
                    message=f"✅ Connected to Ollama. {len(models)} models available.",
                    details={"models": model_names},
                )

            return ProviderHealth(
                is_healthy=True,
                message="✅ Connected to Ollama but no models are installed.\n\nPull a model with: ollama pull llama3",
            )
        except Exception as exc:
            return ProviderHealth(
                is_healthy=False,
                message=f"❌ Failed to reach Ollama at {self.base_url}: {exc}",
                error_type="connection",
                details={"original_error": str(exc)},
            )

    def list_models(self) -> List[str]:
        """List available models from Ollama."""
        if not self.is_configured():
            return []

        if self.client is None:
            raise ProviderConnectionError("Client not initialized")

        try:
            models = self.client.list().get("models", [])
            return [m.get("name", "") for m in models if m.get("name")]
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
            return []

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> AwaitableDict:
        """
        Send a chat request to Ollama.

        Args:
            messages: Conversation messages with 'role' and 'content'
            model: Model name (default: uses default_model)
            **kwargs: Additional parameters passed to Ollama

        Returns:
            Response dict with 'content', 'model', 'stop_reason', and 'usage'
        """
        if not self.is_configured():
            raise ProviderConnectionError("Ollama client not initialized or unreachable")

        if self.client is None:
            raise ProviderConnectionError("Client not initialized")

        model_name = model or self.default_model

        options = kwargs.pop("options", {}) or {}
        if not isinstance(options, dict):
            options = {"value": options}

        # Map common chat parameters to Ollama options
        if (max_tokens := kwargs.pop("max_tokens", None)) is not None:
            options.setdefault("num_predict", max_tokens)
        if (temperature := kwargs.pop("temperature", None)) is not None:
            options.setdefault("temperature", temperature)
        for opt_key in ("top_p", "top_k", "presence_penalty", "frequency_penalty", "stop"):
            if (value := kwargs.pop(opt_key, None)) is not None:
                options.setdefault(opt_key, value)

        client_kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
        }

        if options:
            client_kwargs["options"] = options

        for key in ("format", "stream", "keep_alive"):
            if (value := kwargs.pop(key, None)) is not None:
                client_kwargs[key] = value

        if kwargs:
            logger.debug(f"Ignoring unsupported Ollama chat kwargs: {list(kwargs.keys())}")

        try:
            response = self.client.chat(**client_kwargs)
            message = response.get("message", {})
            return AwaitableDict(
                {
                    "content": message.get("content", ""),
                    "model": response.get("model", model_name),
                    "stop_reason": response.get("done_reason"),
                    "usage": response.get("usage"),
                }
            )
        except Exception as exc:
            error_str = str(exc).lower()

            if "connection" in error_str or "failed to connect" in error_str:
                raise ProviderConnectionError(f"Ollama connection failed: {exc}")
            if "not found" in error_str:
                raise ProviderError(
                    f"Model '{model_name}' not found. " f"Pull it with: ollama pull {model_name}"
                )
            raise ProviderError(f"Ollama error: {exc}")


class OpenAIProvider(LLMProvider):
    """
    OpenAI-compatible provider implementation (LM Studio, AnythingLLM, etc.).
    """

    name = "openai_compatible"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        """
        Initialize OpenAI-compatible provider.

        Args:
            api_key: Optional API key
            base_url: API host URL (default: http://localhost:1234/v1)
            default_model: Default model to use
        """
        self.api_key = api_key or "not-needed"
        self.base_url = base_url or "http://localhost:1234/v1"
        self.default_model = default_model or "local-model"

    def generate_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        """
        Generate a response using OpenAI-compatible chat completions.
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"{context}\n\n{user_prompt}" if context else user_prompt,
                },
            ],
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI-compatible provider error: {e}")
            raise ProviderError(f"API request failed: {e}")

    def health_check(self) -> bool:
        """
        Verify connection to the provider by listing models.
        """
        url = f"{self.base_url.rstrip('/')}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False


def get_provider_class(provider_name: str) -> type:
    """
    Get the provider class for a given provider name.

    Args:
        provider_name: Provider name (only 'ollama' is supported)

    Returns:
        The provider class

    Raises:
        ValueError: If provider name is unknown
    """
    provider_name = provider_name.lower()

    if provider_name == "ollama":
        return OllamaProvider
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Only 'ollama' is supported.")


def create_provider(
    provider_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs: Any
) -> OllamaProvider:
    """
    Factory function to create a provider instance.

    Args:
        provider_name: Provider name (only 'ollama' is supported)
        api_key: Optional API key (for secured endpoints)
        base_url: Ollama host URL
        **kwargs: Additional provider-specific arguments

    Returns:
        Instantiated OllamaProvider object
    """
    provider_class = get_provider_class(provider_name)
    init_kwargs = {"api_key": api_key}
    if base_url:
        init_kwargs["base_url"] = base_url

    return provider_class(**init_kwargs, **kwargs)


def get_provider(config: Dict[str, Any]) -> LLMProvider:
    """
    Factory function to get the correct LLM provider based on configuration.

    Args:
        config: Configuration dictionary (e.g., from Config object or env)

    Returns:
        An instance of an LLMProvider

    Raises:
        ValueError: If provider type is unknown
    """
    provider_type = config.get("AI_PROVIDER", "ollama").lower()

    if provider_type == "ollama":
        return OllamaProvider(
            base_url=config.get("OLLAMA_BASE_URL"), default_model=config.get("OLLAMA_MODEL")
        )
    elif provider_type == "openai_compatible":
        return OpenAIProvider(
            api_key=config.get("AI_API_KEY"),
            base_url=config.get("AI_BASE_URL"),
            default_model=config.get("AI_MODEL"),
        )
    elif provider_type == "mock":
        return MockProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_type}")
