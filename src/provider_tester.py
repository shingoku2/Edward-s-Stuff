"""
Provider Connection Testing Module
Tests API connectivity for OpenAI, Anthropic, and Gemini providers
"""

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class ProviderTester:
    """Test API connectivity for AI providers"""

    DEFAULT_TIMEOUT = 15

    @staticmethod
    def test_openai(api_key: str, base_url: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT) -> Tuple[bool, str]:
        """
        Test OpenAI API connection

        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL for OpenAI-compatible APIs

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not api_key or not api_key.strip():
            return False, "API key is required"

        try:
            import openai

            # Initialize client with custom base URL if provided
            if base_url and base_url.strip():
                client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
            else:
                client = openai.OpenAI(api_key=api_key, timeout=timeout)

            # Try to list models - lightweight test
            try:
                models = client.models.list(timeout=timeout)
                model_count = len(list(models))
                logger.info(f"OpenAI connection test successful - {model_count} models available")
                return True, f"✅ Connected successfully!\n\nFound {model_count} available models."
            except Exception as e:
                # If models.list() fails, try a minimal chat completion
                logger.info("models.list() failed, trying chat completion test")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5,
                    timeout=timeout,
                )
                logger.info("OpenAI connection test successful via chat completion")
                return True, "✅ Connected successfully!\n\nAPI key is valid and working."

        except ImportError:
            error_msg = "OpenAI library not installed. Please install it with:\npip install openai"
            logger.error(error_msg)
            return False, f"❌ Library Missing\n\n{error_msg}"

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"OpenAI connection test failed: {e}")

            # Parse error and provide user-friendly message
            if 'api key' in error_str or '401' in error_str or 'unauthorized' in error_str:
                return False, "❌ Authentication Failed\n\nYour API key is invalid or has been revoked.\n\nPlease check that you've entered the correct key (should start with 'sk-')."
            elif 'quota' in error_str or 'insufficient_quota' in error_str:
                return False, "⚠️ Quota Exceeded\n\nYour OpenAI account has exceeded its quota or has no credits.\n\nPlease add a payment method at:\nhttps://platform.openai.com/account/billing"
            elif 'rate' in error_str and 'limit' in error_str:
                return False, "⚠️ Rate Limit\n\nToo many requests. Please wait a moment and try again."
            elif 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
                return False, f"❌ Connection Error\n\nCould not reach OpenAI servers.\n\nPlease check your internet connection."
            else:
                return False, f"❌ Connection Failed\n\n{str(e)}\n\nPlease check your API key and try again."

    @staticmethod
    def test_anthropic(api_key: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[bool, str]:
        """
        Test Anthropic API connection

        Args:
            api_key: Anthropic API key

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not api_key or not api_key.strip():
            return False, "API key is required"

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key, timeout=timeout)

            # Make a minimal API call to test connectivity
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
                timeout=timeout,
            )

            logger.info("Anthropic connection test successful")
            return True, "✅ Connected successfully!\n\nAPI key is valid and working."

        except ImportError:
            error_msg = "Anthropic library not installed. Please install it with:\npip install anthropic"
            logger.error(error_msg)
            return False, f"❌ Library Missing\n\n{error_msg}"

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Anthropic connection test failed: {e}")

            # Parse error and provide user-friendly message
            if 'api key' in error_str or '401' in error_str or 'unauthorized' in error_str or 'authentication' in error_str:
                return False, "❌ Authentication Failed\n\nYour API key is invalid or has been revoked.\n\nPlease check that you've entered the correct key (should start with 'sk-ant-')."
            elif 'rate' in error_str and 'limit' in error_str:
                return False, "⚠️ Rate Limit\n\nToo many requests. Please wait a moment and try again."
            elif 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
                return False, f"❌ Connection Error\n\nCould not reach Anthropic servers.\n\nPlease check your internet connection."
            else:
                return False, f"❌ Connection Failed\n\n{str(e)}\n\nPlease check your API key and try again."

    @staticmethod
    def test_gemini(api_key: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[bool, str]:
        """
        Test Google Gemini API connection

        Args:
            api_key: Gemini API key

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not api_key or not api_key.strip():
            return False, "API key is required"

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key, client_options={"timeout": timeout})
            model = genai.GenerativeModel('gemini-pro')

            # Make a minimal API call to test connectivity
            response = model.generate_content(
                "Hi",
                generation_config={'max_output_tokens': 10},
                request_options={"timeout": timeout},
            )

            logger.info("Gemini connection test successful")
            return True, "✅ Connected successfully!\n\nAPI key is valid and working."

        except ImportError:
            error_msg = "Google Generative AI library not installed. Please install it with:\npip install google-generativeai"
            logger.error(error_msg)
            return False, f"❌ Library Missing\n\n{error_msg}"

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Gemini connection test failed: {e}")

            # Parse error and provide user-friendly message
            if 'api key' in error_str or '401' in error_str or 'unauthorized' in error_str or 'authentication' in error_str or 'invalid' in error_str:
                return False, "❌ Authentication Failed\n\nYour API key is invalid or has been revoked.\n\nPlease check that you've entered the correct key (should start with 'AIza')."
            elif 'quota' in error_str or 'resource_exhausted' in error_str:
                return False, "⚠️ Quota Exceeded\n\nYour Gemini API quota has been exceeded.\n\nPlease check your quota limits in Google Cloud Console."
            elif 'rate' in error_str and 'limit' in error_str:
                return False, "⚠️ Rate Limit\n\nToo many requests. Please wait a moment and try again."
            elif 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
                return False, f"❌ Connection Error\n\nCould not reach Google servers.\n\nPlease check your internet connection."
            else:
                return False, f"❌ Connection Failed\n\n{str(e)}\n\nPlease check your API key and try again."
