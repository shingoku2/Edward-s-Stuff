"""
AI Assistant Module
Handles AI queries and maintains conversation context

This module uses the provider abstraction layer and AI router for cleaner separation
of concerns. The AIAssistant focuses on conversation state management and game context,
while delegating actual API calls to the provider layer.
"""

import logging
import os
import threading
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

from src.config import Config
from src.ai_router import get_router, AIRouter
from src.providers import (
    ProviderError,
    ProviderAuthError,
    ProviderQuotaError,
    ProviderRateLimitError,
)
from src.knowledge_integration import (
    get_knowledge_integration,
    KnowledgeIntegration,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Avoid circular imports
if TYPE_CHECKING:
    from game_profile import GameProfile


class AIAssistant:
    """AI-powered gaming assistant with conversation context management"""

    # Maximum conversation history to keep
    MAX_CONVERSATION_MESSAGES = 20

    def __init__(
        self,
        provider: Optional[str] = None,
        config: Optional[Config] = None,
        session_tokens: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize AI Assistant

        Args:
            provider: Provider name ('openai', 'anthropic', 'gemini').
                     If None, uses the configured default.
            config: Config instance (if None, creates a new one)
            session_tokens: Optional session tokens (currently stored but not used)
        """
        self.config = config or Config()
        self.router = get_router(self.config)
        self.provider = provider or self.config.ai_provider
        self.session_tokens = session_tokens or {}
        self.conversation_history = []
        self.current_game = None
        self.current_profile = None
        self.current_model = None
        self._session_refresh_handler: Optional[
            Callable[[str, str, Dict[str, str]], None]
        ] = None

        # Thread safety for conversation history
        self._history_lock = threading.Lock()

        # Initialize knowledge integration
        self.knowledge_integration = get_knowledge_integration()

        logger.info(f"AIAssistant initialized with provider: {self.provider}")

    def register_session_refresh_handler(
        self, handler: Callable[[str, str, Dict[str, str]], None]
    ) -> None:
        """Register callback for session refresh events."""
        self._session_refresh_handler = handler

    def update_session_tokens(self, tokens: Optional[Dict[str, str]]) -> None:
        """Update session tokens."""
        self.session_tokens = tokens or {}
        logger.debug("Session tokens updated")

    def _notify_session_event(
        self, action: str, message: str, extra: Optional[Dict[str, str]] = None
    ) -> None:
        """Notify about session events"""
        if self._session_refresh_handler:
            payload = {"message": message}
            if extra:
                payload.update(extra)
            try:
                self._session_refresh_handler(self.provider, action, payload)
            except Exception as e:
                logger.error("Session refresh handler failed: %s", e, exc_info=True)

    def _format_provider_error(self, error: ProviderError) -> str:
        """Format provider errors into user-friendly messages"""
        if isinstance(error, ProviderAuthError):
            return (
                f"⚠️ {self.provider.title()} API Authentication Error\n\n"
                "Your API key is invalid or missing.\n\n"
                "To fix this:\n"
                "1. Click the ⚙️ Settings button\n"
                "2. Go to AI Providers tab\n"
                "3. Enter or verify your API key\n"
                "4. Click 'Test Connection' to verify\n\n"
                "You can get a new API key from your provider's website."
            )
        elif isinstance(error, ProviderQuotaError):
            return (
                f"⚠️ {self.provider.title()} API Quota Exceeded\n\n"
                "Your API account has run out of credits or exceeded its quota.\n\n"
                "To fix this, check your provider's billing settings and add credits/payment method."
            )
        elif isinstance(error, ProviderRateLimitError):
            return (
                f"⚠️ {self.provider.title()} Rate Limit Reached\n\n"
                "You've sent too many requests in a short time.\n\n"
                "Please wait a moment and try again. Rate limits typically reset within 1-2 minutes."
            )
        else:
            return (
                f"❌ {self.provider.title()} API Error\n\n"
                f"An error occurred: {str(error)}\n\n"
                "Please try again or check your internet connection."
            )

    def set_current_game(self, game_info: Dict[str, str]):
        """Set the current game context"""
        self.current_game = game_info

        with self._history_lock:
            self.conversation_history = []

            # Add system context
            game_name = game_info.get('name', 'Unknown Game')
            self._add_system_context(game_name)

        logger.info(f"Set current game context: {game_name}")

    def set_game_profile(self, profile: "GameProfile", override_provider: bool = True):
        """
        Set a game profile with its custom system prompt and preferences.

        Args:
            profile: GameProfile instance with game-specific AI configuration
            override_provider: If True, switch to profile's preferred provider
        """
        self.current_profile = profile

        # Update model from profile
        self.current_model = profile.default_model

        # Switch provider if profile specifies one and override is enabled
        if override_provider and profile.default_provider != self.provider:
            logger.info(
                f"Switching provider from {self.provider} to {profile.default_provider} "
                f"for profile {profile.id}"
            )
            # Just set the provider name. The router will handle which key/client to use.
            self.provider = profile.default_provider

        # Thread-safe history update
        with self._history_lock:
            self.conversation_history = []

            # Add profile's system prompt as context
            self.conversation_history.append({
                "role": "system",
                "content": profile.system_prompt
            })

        logger.info(f"Set game profile: {profile.display_name} (id={profile.id})")

    def clear_game_profile(self):
        """Clear the current game profile and reset to global default provider"""
        self.current_profile = None
        self.current_model = None

        with self._history_lock:
            self.conversation_history = []

        # Reset provider to global default
        # This prevents the provider from staying "stuck" on a game-specific provider
        # after the game is closed
        if self.provider != self.config.ai_provider:
            logger.info(f"Resetting provider from {self.provider} to global default {self.config.ai_provider}")
            self.provider = self.config.ai_provider

        logger.info("Cleared game profile and reverted to default provider")

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

            # Limit system messages to prevent unbounded growth (keep most recent 3)
            if len(system_messages) > 3:
                system_messages = system_messages[-3:]

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

            # Add knowledge pack context if available
            knowledge_context = None
            if self.current_profile:
                game_profile_id = self.current_profile.id
                extra_settings = self.current_profile.extra_settings

                # Check if knowledge packs should be used
                if self.knowledge_integration.should_use_knowledge_packs(game_profile_id, extra_settings):
                    knowledge_context = self.knowledge_integration.get_knowledge_context(
                        game_profile_id=game_profile_id,
                        question=question,
                        extra_settings=extra_settings
                    )

            # Add knowledge context if available
            if knowledge_context:
                user_message = f"{knowledge_context}\n{user_message}"

            # Add web scraping context if available
            if game_context:
                user_message = f"{user_message}\n\nAdditional context from game resources:\n{game_context}"

            # Thread-safe history modification
            with self._history_lock:
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })

                # Trim history if needed
                self._trim_conversation_history()

            # Get response using the AI router
            # (This is the slow network part, keep it OUTSIDE the lock to allow other reads)
            try:
                response = self.router.chat(
                    self.conversation_history,
                    provider=self.provider,
                    max_tokens=1000,
                    temperature=0.7
                )

                # Extract content from response
                if isinstance(response, dict):
                    content = response.get("content", "")
                else:
                    content = str(response)

                # Add response to history only if it's not an error
                if not content.startswith(('⚠️', '❌')):
                    with self._history_lock:
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": content
                        })

                # Log conversation to session logger
                if self.current_profile:
                    self.knowledge_integration.log_conversation(
                        game_profile_id=self.current_profile.id,
                        question=question,
                        answer=content
                    )

                return content

            except ProviderError as e:
                error_msg = self._format_provider_error(e)
                logger.error(f"Provider error: {e}", exc_info=True)
                return error_msg

        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\nAn unexpected error occurred:\n{str(e)}\n\nPlease try again or contact support if the issue persists."
            logger.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return error_msg

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

        with self._history_lock:
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
