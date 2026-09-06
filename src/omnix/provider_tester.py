"""
Provider Connection Testing Module
Tests connectivity to Ollama
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class ProviderTester:
    """Test connectivity to Ollama"""

    DEFAULT_TIMEOUT = 15

    @staticmethod
    def test_ollama(
        base_url: str = "http://localhost:11434", timeout: float = DEFAULT_TIMEOUT
    ) -> Tuple[bool, str]:
        """
        Test Ollama connectivity.

        Args:
            base_url: Ollama host URL
            timeout: Connection timeout in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            import ollama

            client = ollama.Client(host=base_url)
            models_response = client.list()
            models = models_response.get("models", [])
            model_count = len(models)

            if model_count == 0:
                return True, (
                    "✅ Connected to Ollama!\n\n"
                    "No models installed yet. Pull a model with:\n"
                    "ollama pull llama3"
                )

            model_names = [m.get("name", "unknown") for m in models[:5]]
            model_list = ", ".join(model_names)
            if model_count > 5:
                model_list += f", ... (+{model_count - 5} more)"

            return True, (
                f"✅ Connected to Ollama!\n\n" f"Found {model_count} model(s):\n{model_list}"
            )

        except ImportError:
            error_msg = (
                "❌ Ollama library not installed.\n\n" "Install it with:\n" "pip install ollama"
            )
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Ollama connection test failed: {e}")

            if "connection" in error_str or "refused" in error_str:
                return False, (
                    "❌ Cannot connect to Ollama\n\n"
                    f"Failed to reach {base_url}\n\n"
                    "Please ensure:\n"
                    "1. Ollama is installed (https://ollama.com)\n"
                    "2. The Ollama daemon is running\n"
                    "3. The host URL is correct"
                )
            elif "timeout" in error_str:
                return False, (
                    "❌ Connection Timeout\n\n"
                    f"Ollama at {base_url} did not respond in time.\n\n"
                    "Please check if Ollama is running and accessible."
                )
            else:
                return False, f"❌ Connection Failed\n\n{str(e)}"
