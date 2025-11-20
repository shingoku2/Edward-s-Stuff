"""
AI Provider Abstraction Layer

Defines a consistent interface for interacting with different AI providers
(OpenAI, Anthropic, Gemini) with a clean abstraction that hides provider-specific details.
"""

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple

# Ensure imports using either ``providers`` or ``src.providers`` resolve to the
# same module instance so exception classes remain identical across import
# styles. This avoids mismatched exception types when code follows the
# recommended ``from src.module import`` pattern but tests or legacy modules
# import without the package prefix.
_current_module = sys.modules[__name__]

if __name__ == "src.providers":
    # Preferred import path is loaded first; guarantee the legacy alias points
    # to the same module object.
    sys.modules["providers"] = _current_module
elif __name__ == "providers":
    # Legacy import path is loaded first; register the namespaced alias to
    # prevent Python from creating a second module instance when
    # ``import src.providers`` occurs later.
    sys.modules["src.providers"] = _current_module
else:  # Defensive fallback for unexpected import names
    sys.modules.setdefault("providers", _current_module)
    sys.modules.setdefault("src.providers", _current_module)

logger = logging.getLogger(__name__)


@dataclass
class ProviderHealth:
    """Health status of a provider"""
    healthy: bool
    message: str
    error_type: Optional[str] = None  # 'auth', 'quota', 'rate_limit', 'connection', etc.
    details: Optional[Dict[str, Any]] = None


class ProviderError(Exception):
    """Base exception for provider-related errors"""
    pass


class ProviderAuthError(ProviderError):
    """Raised when API key is invalid or missing"""
    pass


class ProviderQuotaError(ProviderError):
    """Raised when quota is exceeded"""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when rate limit is exceeded"""
    pass


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to provider"""
    pass


class AIProvider(Protocol):
    """Protocol defining the interface all AI providers must implement"""

    name: str

    def is_configured(self) -> bool:
        """Check if provider has valid API key/credentials configured"""
        ...

    def test_connection(self) -> ProviderHealth:
        """Test connection to the provider with a lightweight call"""
        ...

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any
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


class OpenAIProvider:
    """OpenAI GPT provider implementation"""

    name = "openai"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL (for OpenAI-compatible APIs)
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.default_model = default_model or "gpt-3.5-turbo"
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI client"""
        try:
            import openai
            if self.api_key:
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
        except Exception:
            logger.warning("OpenAI library not installed or failed to initialize")

    def is_configured(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key)

    def test_connection(self) -> ProviderHealth:
        """Test OpenAI API connection"""
        if not self.is_configured():
            return ProviderHealth(
                is_healthy=False,
                message="OpenAI API key not configured",
                error_type="auth"
            )

        try:
            # Try to list models (lightweight test)
            try:
                models = list(self.client.models.list())
                count = len(models)
                return ProviderHealth(
                    is_healthy=True,
                    message=f"✅ Connected! Found {count} available models.",
                )
            except Exception:
                # Fallback: try a minimal chat completion
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                return ProviderHealth(
                    is_healthy=True,
                    message="✅ Connected! API key is valid and working."
                )

        except Exception as e:
            error_str = str(e).lower()

            if "insufficient_quota" in error_str or "quota" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Quota Exceeded - Please check your OpenAI billing",
                    error_type="quota",
                    details={"original_error": str(e)}
                )
            elif "rate" in error_str or "429" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Rate Limited - Please try again later",
                    error_type="rate_limit"
                )
            elif "authentication" in error_str or "api key" in error_str or "401" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Authentication Failed - Invalid API key",
                    error_type="auth"
                )
            else:
                return ProviderHealth(
                    is_healthy=False,
                    message=f"❌ Connection Failed - {str(e)}",
                    error_type="connection"
                )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a chat request to OpenAI

        Args:
            messages: Conversation messages
            model: Model name (default: gpt-3.5-turbo)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Response dict with 'content' and 'model' keys
        """
        if not self.is_configured():
            raise ProviderAuthError("OpenAI API key not configured")

        model = model or getattr(self, 'default_model', "gpt-3.5-turbo")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            usage = None
            try:
                usage = {"total_tokens": getattr(response.usage, 'total_tokens', None)}
            except Exception:
                usage = {"total_tokens": None}

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "stop_reason": response.choices[0].finish_reason,
                "usage": usage,
            }
        except Exception as e:
            error_str = str(e).lower()

            if "insufficient_quota" in error_str or "quota" in error_str:
                raise ProviderQuotaError(f"OpenAI quota exceeded: {str(e)}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"OpenAI rate limited: {str(e)}")
            elif "authentication" in error_str or "api key" in error_str:
                raise ProviderAuthError(f"OpenAI authentication failed: {str(e)}")
            else:
                raise ProviderError(f"OpenAI API error: {str(e)}")


class AnthropicProvider:
    """Anthropic Claude provider implementation"""

    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key
        self.default_model = default_model or "claude-3-5-sonnet-20240620"
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Anthropic client"""
        try:
            import anthropic
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception:
            logger.warning("Anthropic library not installed or failed to initialize")

    def is_configured(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key)

    def test_connection(self) -> ProviderHealth:
        """Test Anthropic API connection"""
        if not self.is_configured():
            return ProviderHealth(
                is_healthy=False,
                message="Anthropic API key not configured",
                error_type="auth"
            )

        try:
            # Try a minimal message creation
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=5,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return ProviderHealth(
                is_healthy=True,
                message="✅ Connected! API key is valid and working."
            )

        except Exception as e:
            error_str = str(e).lower()

            if "authentication" in error_str or "api key" in error_str or "401" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Authentication Failed - Invalid API key",
                    error_type="auth"
                )
            elif "rate" in error_str or "429" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Rate Limited - Please try again later",
                    error_type="rate_limit"
                )
            else:
                return ProviderHealth(
                    is_healthy=False,
                    message=f"❌ Connection Failed - {str(e)}",
                    error_type="connection"
                )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a chat request to Anthropic

        Args:
            messages: Conversation messages
            model: Model name (default: claude-3-5-sonnet-20240620)
            **kwargs: Additional parameters (max_tokens, etc.)

        Returns:
            Response dict with 'content' and 'model' keys
        """
        if not self.is_configured():
            raise ProviderAuthError("Anthropic API key not configured")

        model = model or getattr(self, 'default_model', "claude-3-5-sonnet-20240620")
        max_tokens = kwargs.pop("max_tokens", 1024)

        # Extract system messages - Anthropic requires them as a separate parameter
        system_messages = [msg["content"] for msg in messages if msg["role"] == "system"]
        user_messages = [msg for msg in messages if msg["role"] != "system"]

        # Combine system messages if there are multiple
        system_prompt = "\n\n".join(system_messages) if system_messages else None

        try:
            # Create the API call with system parameter if we have system messages
            api_params = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": user_messages,
                **kwargs
            }

            if system_prompt:
                api_params["system"] = system_prompt

            response = self.client.messages.create(**api_params)

            # Compute usage totals if available
            total_tokens = None
            try:
                input_tokens = getattr(response.usage, 'input_tokens', 0) or 0
                output_tokens = getattr(response.usage, 'output_tokens', 0) or 0
                total_tokens = input_tokens + output_tokens
            except Exception:
                total_tokens = None

            return {
                "content": response.content[0].text,
                "model": response.model,
                "stop_reason": response.stop_reason,
                "usage": {"total_tokens": total_tokens},
            }
        except Exception as e:
            error_str = str(e).lower()

            if "authentication" in error_str or "api key" in error_str:
                raise ProviderAuthError(f"Anthropic authentication failed: {str(e)}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"Anthropic rate limited: {str(e)}")
            else:
                raise ProviderError(f"Anthropic API error: {str(e)}")


class GeminiProvider:
    """Google Gemini provider implementation"""

    name = "gemini"

    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialize Gemini provider

        Args:
            api_key: Google AI API key
        """
        self.api_key = api_key
        self.default_model = default_model or "gemini-pro"
        self.client = None
        self._genai = None
        self.model = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self._genai = genai
                self.client = genai.GenerativeModel(self.default_model)
        except Exception:
            logger.warning("google-generativeai library not installed or failed to initialize")

    def is_configured(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key)

    def test_connection(self) -> ProviderHealth:
        """Test Gemini API connection"""
        if not self.is_configured():
            return ProviderHealth(
                is_healthy=False,
                message="Gemini API key not configured",
                error_type="auth"
            )

        try:
            # Try a minimal content generation
            model = self.client or self._genai.GenerativeModel(self.default_model)
            response = model.generate_content("Hi", stream=False)
            return ProviderHealth(
                is_healthy=True,
                message="✅ Connected! API key is valid and working."
            )

        except Exception as e:
            error_str = str(e).lower()

            if "authentication" in error_str or "api key" in error_str or "401" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Authentication Failed - Invalid API key",
                    error_type="auth"
                )
            elif "resource_exhausted" in error_str or "quota" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Quota Exceeded - Please check your Gemini quota",
                    error_type="quota"
                )
            elif "rate" in error_str or "429" in error_str:
                return ProviderHealth(
                    is_healthy=False,
                    message="❌ Rate Limited - Please try again later",
                    error_type="rate_limit"
                )
            else:
                return ProviderHealth(
                    is_healthy=False,
                    message=f"❌ Connection Failed - {str(e)}",
                    error_type="connection"
                )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Send a chat request to Gemini

        Args:
            messages: Conversation messages
            model: Model name (default: gemini-1.5-pro)
            **kwargs: Additional parameters

        Returns:
            Response dict with 'content' and 'model' keys
        """
        if not self.is_configured():
            raise ProviderAuthError("Gemini API key not configured")

        model_name = model or self.default_model

        try:
            # Prefer an explicitly set `model` (tests patch this), otherwise use client/genai
            if getattr(self, 'model', None) is not None:
                model_client = self.model
            elif model_name == self.default_model and self.client:
                model_client = self.client
            else:
                if self._genai is None:
                    raise ProviderError("Gemini client not initialized")
                model_client = self._genai.GenerativeModel(model_name)

            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                gemini_messages.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })

            response = model_client.generate_content(
                gemini_messages,
                stream=False,
                **kwargs
            )

            return {
                "content": response.text,
                "model": model_name,
                "stop_reason": response.candidates[0].finish_reason if response.candidates else None,
            }
        except Exception as e:
            error_str = str(e).lower()

            if "authentication" in error_str or "api key" in error_str or "401" in error_str:
                raise ProviderAuthError(f"Gemini authentication failed: {str(e)}")
            elif "resource_exhausted" in error_str or "quota" in error_str:
                raise ProviderQuotaError(f"Gemini quota exceeded: {str(e)}")
            elif "rate" in error_str or "429" in error_str:
                raise ProviderRateLimitError(f"Gemini rate limited: {str(e)}")
            else:
                raise ProviderError(f"Gemini API error: {str(e)}")


def get_provider_class(provider_name: str) -> type:
    """
    Get the provider class for a given provider name

    Args:
        provider_name: 'openai', 'anthropic', or 'gemini'

    Returns:
        The provider class

    Raises:
        ValueError: If provider name is unknown
    """
    provider_name = provider_name.lower()

    if provider_name == "openai":
        return OpenAIProvider
    elif provider_name == "anthropic":
        return AnthropicProvider
    elif provider_name == "gemini":
        return GeminiProvider
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def create_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    **kwargs: Any
) -> Any:
    """
    Factory function to create a provider instance

    Args:
        provider_name: 'openai', 'anthropic', or 'gemini'
        api_key: API key for the provider
        **kwargs: Additional provider-specific arguments

    Returns:
        Instantiated provider object
    """
    provider_class = get_provider_class(provider_name)
    return provider_class(api_key=api_key, **kwargs)
