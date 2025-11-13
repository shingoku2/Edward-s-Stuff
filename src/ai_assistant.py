"""
AI Assistant Module
Handles AI queries using OpenAI or Anthropic APIs
"""

import os
import logging
from typing import Callable, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAssistant:
    """AI-powered gaming assistant"""

    # Maximum conversation history to keep
    MAX_CONVERSATION_MESSAGES = 20

    def __init__(
        self,
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        session_tokens: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize AI Assistant

        Args:
            provider: 'openai', 'anthropic', or 'gemini'
            api_key: API key for the chosen provider
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.session_tokens = session_tokens or {}
        self.conversation_history = []
        self.current_game = None
        self.client = None
        self._active_auth_mode = "api_key"
        self._active_auth_token: Optional[str] = None
        self._session_refresh_handler: Optional[
            Callable[[str, str, Dict[str, str]], None]
        ] = None

        self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment"""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        return None

    def _get_auth_token(self) -> Tuple[Optional[str], str]:
        """Select the preferred credential for the current provider."""

        # Note: Session tokens (cookies) are stored but NOT used for SDK authentication
        # The AI provider SDKs (OpenAI, Anthropic, Gemini) require actual API keys,
        # not browser cookies. Session login is only to help users access their API keys page.

        # Only use API keys - cookies don't work with the official SDKs
        if self.api_key:
            return self.api_key, "api_key"

        return None, ""

    def register_session_refresh_handler(
        self, handler: Callable[[str, str, Dict[str, str]], None]
    ) -> None:
        """Register callback for session refresh events."""

        self._session_refresh_handler = handler

    def update_session_tokens(self, tokens: Optional[Dict[str, str]]) -> None:
        """Update session tokens and reinitialize client."""

        self.session_tokens = tokens or {}
        self._initialize_client(force=True)

    def _notify_session_event(
        self, action: str, message: str, extra: Optional[Dict[str, str]] = None
    ) -> None:
        if self._session_refresh_handler:
            payload = {"message": message}
            if extra:
                payload.update(extra)
            try:
                self._session_refresh_handler(self.provider, action, payload)
            except Exception as e:  # noqa: BLE001
                logger.error("Session refresh handler failed: %s", e, exc_info=True)

    def _initialize_client(self, force: bool = False):
        """Initialize the AI client"""
        if self.client is not None and not force:
            return

        auth_token, auth_mode = self._get_auth_token()
        if not auth_token:
            raise ValueError(
                f"No credentials provided for {self.provider}."
            )

        self._active_auth_mode = auth_mode
        self._active_auth_token = auth_token

        try:
            if self.provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=auth_token)
                logger.info("OpenAI client initialized")
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=auth_token)
                logger.info("Anthropic client initialized")
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=auth_token)
                self.client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized")
            else:
                raise ValueError(f"Unknown provider: {self.provider}. Must be 'openai', 'anthropic', or 'gemini'")
        except ImportError as e:
            raise ImportError(f"Required library not installed: {e}")
        except Exception as e:
            logger.error(f"Error initializing AI client: {e}", exc_info=True)
            raise

    def _handle_auth_failure(self, error: Exception) -> (bool, Optional[str]):
        """Handle authentication errors and decide on retry strategy."""

        error_str = str(error).lower()
        auth_indicators = [
            "401",
            "unauthorized",
            "forbidden",
            "token",
            "expired",
            "authentication",
            "invalid key",
            "invalid api key",
        ]

        if not any(indicator in error_str for indicator in auth_indicators):
            return False, None

        # API key authentication failed
        message = (
            f"⚠️ {self.provider.title()} API key is invalid or expired.\n\n"
            "Please check your API key in Settings:\n"
            "1. Click the ⚙️ Settings button\n"
            "2. Verify your API key is correct\n"
            "3. If needed, generate a new API key from your provider's website"
        )
        self._notify_session_event(
            "reauth_required",
            message,
            {"reason": "auth_failure"},
        )
        return False, message

    def _execute_with_auth_retry(self, call_fn, error_formatter):
        try:
            return call_fn()
        except Exception as error:  # noqa: BLE001
            retry, message = self._handle_auth_failure(error)
            if retry:
                try:
                    return call_fn()
                except Exception as retry_error:  # noqa: BLE001
                    logger.error(
                        "Retry after auth fallback failed: %s", retry_error, exc_info=True
                    )
                    return error_formatter(retry_error)

            if message:
                return message

            return error_formatter(error)

    def set_current_game(self, game_info: Dict[str, str]):
        """Set the current game context"""
        self.current_game = game_info
        self.conversation_history = []

        # Add system context
        game_name = game_info.get('name', 'Unknown Game')
        self._add_system_context(game_name)
        logger.info(f"Set current game context: {game_name}")

    def _add_system_context(self, game_name: str):
        """Add system context about the current game"""
        system_message = f"""You are a specialized gaming assistant ONLY for {game_name}.

CRITICAL RULES:
- You ONLY answer questions about {game_name}
- You MUST refuse to answer any questions not related to {game_name}
- Do NOT engage in general conversation, chitchat, or off-topic discussions
- Do NOT answer questions about other games, programming, life advice, or any non-game topics
- If asked something unrelated to {game_name}, politely remind the user you only help with {game_name}

What you CAN help with for {game_name}:
- Game strategies and tips
- Character/weapon/item builds
- Quest walkthroughs and missions
- Game mechanics and systems
- Controls and gameplay techniques
- Lore and story questions
- Where to find items, NPCs, or locations

Be concise, accurate, and helpful. Stay strictly focused on {game_name} only."""

        self.conversation_history.append({
            "role": "system",
            "content": system_message
        })

    def _trim_conversation_history(self):
        """Trim conversation history to prevent token limit issues"""
        # Keep system message + last N messages
        if len(self.conversation_history) > self.MAX_CONVERSATION_MESSAGES:
            system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
            recent_messages = [msg for msg in self.conversation_history if msg["role"] != "system"]

            # Keep system message and most recent messages
            recent_messages = recent_messages[-(self.MAX_CONVERSATION_MESSAGES - len(system_messages)):]
            self.conversation_history = system_messages + recent_messages

            logger.info(f"Trimmed conversation history to {len(self.conversation_history)} messages")

    def ask_question(self, question: str, game_context: Optional[str] = None) -> str:
        """
        Ask a question about the current game

        Args:
            question: User's question
            game_context: Optional additional context from web scraping

        Returns:
            AI's response
        """
        if not question or not question.strip():
            return "Please provide a question."

        # Check if a game is currently set
        if not self.current_game:
            return "🎮 No game detected!\n\nPlease start a game to get assistance. I'm here to help you with gaming questions once you're playing."

        try:
            # Build the user message
            user_message = question.strip()

            if game_context:
                user_message = f"{user_message}\n\nAdditional context from game resources:\n{game_context}"

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Trim history if needed
            self._trim_conversation_history()

            # Get response based on provider
            if self.provider == "openai":
                response = self._ask_openai()
            elif self.provider == "anthropic":
                response = self._ask_anthropic()
            elif self.provider == "gemini":
                response = self._ask_gemini()
            else:
                response = "Error: Invalid AI provider"

            # Check if response is an error message (starts with warning/error emoji)
            # If so, don't add to conversation history
            if not response.startswith(('⚠️', '❌')):
                # Add response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

            return response

        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\nAn unexpected error occurred:\n{str(e)}\n\nPlease try again or contact support if the issue persists."
            logger.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return error_msg

    def _ask_openai(self) -> str:
        """Get response from OpenAI"""
        def call():
            messages = []
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            if not messages:
                raise ValueError("No messages in conversation history")

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content

        def format_error(e: Exception) -> str:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            error_str = str(e).lower()

            if 'insufficient_quota' in error_str or 'quota' in error_str:
                return ("⚠️ OpenAI API Quota Exceeded\n\n"
                       "Your OpenAI account has run out of credits or exceeded its quota.\n\n"
                       "To fix this:\n"
                       "1. Visit https://platform.openai.com/account/billing\n"
                       "2. Add a payment method or purchase credits\n"
                       "3. Check your usage limits and billing details\n\n"
                       "Alternatively, you can switch to a different AI provider in Settings.")

            if 'rate' in error_str and ('limit' in error_str or '429' in error_str):
                return ("⚠️ OpenAI Rate Limit Reached\n\n"
                       "You've sent too many requests in a short time.\n\n"
                       "Please wait a moment and try again. Rate limits typically reset within 1-2 minutes.\n\n"
                       "If this persists, consider upgrading your OpenAI plan for higher rate limits.")

            if 'authentication' in error_str or 'api key' in error_str or '401' in error_str:
                return ("⚠️ OpenAI Authentication Error\n\n"
                       "Your API key appears to be invalid or missing.\n\n"
                       "Please check your Settings and ensure you've entered a valid OpenAI API key (starts with 'sk-').")

            return f"❌ OpenAI API Error\n\nAn error occurred while contacting OpenAI:\n{str(e)}\n\nPlease try again or check your internet connection."

        return self._execute_with_auth_retry(call, format_error)

    def _ask_anthropic(self) -> str:
        """Get response from Anthropic (Claude)"""
        def call():
            system_msg = ""
            messages = []

            for msg in self.conversation_history:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            if not messages:
                messages = [{
                    "role": "user",
                    "content": "Hello! I just started playing. What can you help me with?"
                }]
                logger.warning("No user messages in history, using default greeting")

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system=system_msg,
                messages=messages
            )

            return response.content[0].text

        def format_error(e: Exception) -> str:
            logger.error(f"Anthropic API error: {e}", exc_info=True)
            error_str = str(e).lower()

            if 'authentication' in error_str or 'api key' in error_str or '401' in error_str:
                return ("⚠️ Anthropic Authentication Error\n\n"
                       "Your API key appears to be invalid or missing.\n\n"
                       "Please check your Settings and ensure you've entered a valid Anthropic API key (starts with 'sk-ant-').")

            if 'rate' in error_str and ('limit' in error_str or '429' in error_str):
                return ("⚠️ Anthropic Rate Limit Reached\n\n"
                       "You've sent too many requests in a short time.\n\n"
                       "Please wait a moment and try again.")

            return f"❌ Anthropic API Error\n\nAn error occurred while contacting Anthropic:\n{str(e)}\n\nPlease try again or check your internet connection."

        return self._execute_with_auth_retry(call, format_error)

    def _ask_gemini(self) -> str:
        """Get response from Google Gemini"""
        def call():
            system_msg = ""
            conversation_text = ""

            for msg in self.conversation_history:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                elif msg["role"] == "user":
                    conversation_text += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    conversation_text += f"Assistant: {msg['content']}\n\n"

            full_prompt = f"{system_msg}\n\n{conversation_text}Assistant:"

            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 1000,
                }
            )

            return response.text

        def format_error(e: Exception) -> str:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            error_str = str(e).lower()

            if 'authentication' in error_str or 'api key' in error_str or '401' in error_str:
                return ("⚠️ Gemini Authentication Error\n\n"
                       "Your API key appears to be invalid or missing.\n\n"
                       "Please check your Settings and ensure you've entered a valid Gemini API key (starts with 'AIza').")

            if 'rate' in error_str and ('limit' in error_str or '429' in error_str):
                return ("⚠️ Gemini Rate Limit Reached\n\n"
                       "You've sent too many requests in a short time.\n\n"
                       "Please wait a moment and try again.")

            if 'quota' in error_str or 'resource_exhausted' in error_str:
                return ("⚠️ Gemini API Quota Exceeded\n\n"
                       "Your Gemini API quota has been exceeded.\n\n"
                       "Please check your Google Cloud Console for quota limits and usage.")

            return f"❌ Gemini API Error\n\nAn error occurred while contacting Gemini:\n{str(e)}\n\nPlease try again or check your internet connection."

        return self._execute_with_auth_retry(call, format_error)

    def get_game_overview(self, game_name: str) -> str:
        """Get a general overview of the game"""
        question = f"Give me a brief overview of {game_name}, including its genre, main gameplay mechanics, and key tips for beginners."
        return self.ask_question(question)

    def get_tips_and_strategies(self, specific_topic: Optional[str] = None) -> str:
        """Get tips and strategies for the current game"""
        if not self.current_game:
            return "🎮 No game detected!\n\nPlease start a game to get tips and strategies. I'm here to help you once you're playing."

        game_name = self.current_game.get('name', 'the current game')

        if specific_topic:
            question = f"Give me tips and strategies for {specific_topic} in {game_name}."
        else:
            question = f"Give me some general tips and strategies for playing {game_name} effectively."

        return self.ask_question(question)

    def clear_history(self):
        """Clear conversation history"""
        game_name = self.current_game.get('name', 'Unknown Game') if self.current_game else 'Unknown Game'
        self.conversation_history = []
        self._add_system_context(game_name)
        logger.info("Conversation history cleared")

    def get_conversation_summary(self) -> List[Dict[str, str]]:
        """Get conversation history without system messages"""
        return [msg for msg in self.conversation_history if msg["role"] != "system"]


if __name__ == "__main__":
    # Test the AI assistant
    import sys

    # Test with environment variables
    provider = os.getenv("AI_PROVIDER", "anthropic")

    try:
        assistant = AIAssistant(provider=provider)

        # Set a test game
        assistant.set_current_game({"name": "League of Legends"})

        # Ask a test question
        print("Testing AI Assistant...")
        print("\nQuestion: What are some tips for playing ADC?")

        response = assistant.ask_question("What are some tips for playing ADC?")
        print(f"\nResponse:\n{response}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to .env")
        print("3. Set AI_PROVIDER in .env")
