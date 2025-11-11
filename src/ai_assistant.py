"""
AI Assistant Module
Handles AI queries using OpenAI or Anthropic APIs
"""

import os
import logging
from typing import Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAssistant:
    """AI-powered gaming assistant"""

    # Maximum conversation history to keep
    MAX_CONVERSATION_MESSAGES = 20

    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        """
        Initialize AI Assistant

        Args:
            provider: 'openai' or 'anthropic'
            api_key: API key for the chosen provider
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.conversation_history = []
        self.current_game = None
        self.client = None

        self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment"""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return None

    def _initialize_client(self):
        """Initialize the AI client"""
        if not self.api_key:
            raise ValueError(f"No API key provided for {self.provider}")

        try:
            if self.provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized")
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized")
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
        except ImportError as e:
            raise ImportError(f"Required library not installed: {e}")
        except Exception as e:
            logger.error(f"Error initializing AI client: {e}", exc_info=True)
            raise

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
        system_message = f"""You are a helpful gaming assistant specializing in {game_name}.
Your role is to provide:
- Game strategies and tips
- Character/weapon builds
- Quest walkthroughs
- Game mechanics explanations
- Real-time advice during gameplay

Be concise, accurate, and helpful. If you don't know something specific about the game,
say so and provide general gaming advice or suggest where to find the information."""

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
            else:
                response = "Error: Invalid AI provider"

            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })

            return response

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    def _ask_openai(self) -> str:
        """Get response from OpenAI"""
        try:
            # Convert history to OpenAI format
            messages = []
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # Ensure we have messages
            if not messages:
                raise ValueError("No messages in conversation history")

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Updated model name
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            raise Exception(f"OpenAI API error: {str(e)}")

    def _ask_anthropic(self) -> str:
        """Get response from Anthropic (Claude)"""
        try:
            # Separate system message from conversation
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

            # Ensure we have messages
            if not messages:
                # If no messages yet, create a default one
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

        except Exception as e:
            logger.error(f"Anthropic API error: {e}", exc_info=True)
            raise Exception(f"Anthropic API error: {str(e)}")

    def get_game_overview(self, game_name: str) -> str:
        """Get a general overview of the game"""
        question = f"Give me a brief overview of {game_name}, including its genre, main gameplay mechanics, and key tips for beginners."
        return self.ask_question(question)

    def get_tips_and_strategies(self, specific_topic: Optional[str] = None) -> str:
        """Get tips and strategies for the current game"""
        if not self.current_game:
            return "No game currently detected."

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
