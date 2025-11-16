"""
AI Provider Abstraction Layer

Defines a consistent interface for interacting with different AI providers
(OpenAI, Anthropic, Gemini) with a clean abstraction that hides provider-specific details.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ProviderHealth:
    """Health status of a provider"""
    is_healthy: bool
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

    async def chat(
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

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL (for OpenAI-compatible APIs)
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
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
        except ImportError:
            logger.warning("OpenAI library not installed")

    def is_configured(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key) and self.client is not None

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

        model = model or "gpt-3.5-turbo"

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "stop_reason": response.choices[0].finish_reason,
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

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Anthropic client"""
        try:
            import anthropic
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            logger.warning("Anthropic library not installed")

    def is_configured(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key) and self.client is not None

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
                model="claude-3-5-sonnet-20241022",
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
            model: Model name (default: claude-3-5-sonnet-20241022)
            **kwargs: Additional parameters (max_tokens, etc.)

        Returns:
            Response dict with 'content' and 'model' keys
        """
        if not self.is_configured():
            raise ProviderAuthError("Anthropic API key not configured")

        model = model or "claude-3-5-sonnet-20241022"
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

            return {
                "content": response.content[0].text,
                "model": response.model,
                "stop_reason": response.stop_reason,
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

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini provider

        Args:
            api_key: Google AI API key
        """
        self.api_key = api_key
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai
        except ImportError:
            logger.warning("google-generativeai library not installed")

    def is_configured(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key) and self.client is not None

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
            model = self.client.GenerativeModel("gemini-1.5-pro")
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

        model_name = model or "gemini-1.5-pro"

        try:
            model = self.client.GenerativeModel(model_name)

            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                gemini_messages.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })

            response = model.generate_content(
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

            if "authentication" in error_str or "api key" in error_str:
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
