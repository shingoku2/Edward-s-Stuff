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

    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None, ollama_endpoint: str = "http://localhost:11434"):
        """
        Initialize AI Assistant

        Args:
            provider: 'openai', 'anthropic', 'gemini', or 'ollama'
            api_key: API key for the chosen provider (not needed for ollama)
            ollama_endpoint: Ollama endpoint URL (default: http://localhost:11434)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.ollama_endpoint = ollama_endpoint
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
        elif self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        elif self.provider == "ollama":
            return None  # Ollama doesn't need API key
        return None

    def _initialize_client(self):
        """Initialize the AI client"""
        # Ollama doesn't require API key
        if not self.api_key and self.provider != "ollama":
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
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized")
            elif self.provider == "ollama":
                # Ollama uses REST API - no package needed!
                # We'll use requests library which is commonly available
                try:
                    import requests
                except ImportError:
                    raise ImportError(
                        "requests package not installed. Install it with:\n"
                        "pip install requests\n\n"
                        "Note: Ollama support uses REST API, no ollama package needed!"
                    )

                # Store endpoint for API calls
                self.ollama_endpoint = self.ollama_endpoint.rstrip('/')
                logger.info(f"Ollama configured for REST API (endpoint: {self.ollama_endpoint})")

                # Test connection (optional, but helpful)
                # Try both Open WebUI and native Ollama endpoints
                try:
                    # Try OpenAI-compatible endpoint first (Open WebUI)
                    response = requests.get(f"{self.ollama_endpoint}/v1/models", timeout=2)
                    if response.status_code == 200:
                        logger.info("Open WebUI connection test successful (OpenAI-compatible API)")
                    else:
                        # Try native Ollama endpoint
                        response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=2)
                        if response.status_code == 200:
                            logger.info("Native Ollama connection test successful")
                        else:
                            logger.warning(f"Ollama endpoint returned status {response.status_code}")
                except Exception as e:
                    logger.warning(f"Could not connect to Ollama endpoint: {e}")
                    logger.info("Will attempt to use anyway - ensure Ollama/Open WebUI is running")

                # Don't set self.client for ollama, we'll use requests directly
                self.client = None
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
            elif self.provider == "ollama":
                response = self._ask_ollama()
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

    def _ask_gemini(self) -> str:
        """Get response from Google Gemini"""
        try:
            # Build conversation context for Gemini
            # Gemini uses a different format - we'll pass the full conversation
            system_msg = ""
            conversation_text = ""

            for msg in self.conversation_history:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                elif msg["role"] == "user":
                    conversation_text += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    conversation_text += f"Assistant: {msg['content']}\n\n"

            # Combine system message with conversation
            full_prompt = f"{system_msg}\n\n{conversation_text}Assistant:"

            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 1000,
                }
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise Exception(f"Gemini API error: {str(e)}")

    def _ask_ollama(self) -> str:
        """Get response from Ollama (local LLM) via REST API"""
        try:
            import requests

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
                messages = [{
                    "role": "user",
                    "content": "Hello! I just started playing. What can you help me with?"
                }]
                logger.warning("No user messages in history, using default greeting")

            # Add system message as first message if present
            if system_msg:
                messages = [{"role": "system", "content": system_msg}] + messages

            # Try Open WebUI's OpenAI-compatible API first (most common for Open WebUI)
            # This uses the /v1/chat/completions endpoint
            openai_api_url = f"{self.ollama_endpoint}/v1/chat/completions"

            openai_payload = {
                "model": "llama2",  # Default model, can be made configurable
                "messages": messages,
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 1000,
            }

            logger.debug(f"Trying OpenAI-compatible API at {openai_api_url}")
            try:
                response = requests.post(openai_api_url, json=openai_payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                elif response.status_code in [404, 405]:
                    # OpenAI-compatible endpoint not found or method not allowed
                    # Try native Ollama API instead
                    logger.info(f"OpenAI-compatible endpoint returned {response.status_code}, trying native Ollama API")
                else:
                    response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [404, 405]:
                    # Endpoint structure doesn't match OpenAI format, try native Ollama
                    logger.info(f"OpenAI-compatible endpoint returned {e.response.status_code}, trying native Ollama API")
                else:
                    raise

            # Fall back to native Ollama API
            # This uses the /api/chat endpoint
            native_api_url = f"{self.ollama_endpoint}/api/chat"

            native_payload = {
                "model": "llama2",  # Default model, can be made configurable
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000,
                }
            }

            logger.debug(f"Calling native Ollama API at {native_api_url}")
            response = requests.post(native_api_url, json=native_payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result['message']['content']

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            raise Exception(
                f"Cannot connect to Ollama at {self.ollama_endpoint}\n\n"
                "Troubleshooting:\n"
                "• WSL: Run 'ollama serve' in WSL terminal\n"
                "• Open WebUI: Ensure it's running (default: http://localhost:8080)\n"
                "• Native Ollama: Check endpoint in settings (default: http://localhost:11434)\n"
                "• WSL2 users: Should auto-forward to localhost\n"
                "• Update endpoint in Settings to match your setup"
            )
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama request timeout: {e}")
            raise Exception("Ollama request timed out. The model may be loading or the server is slow.")
        except Exception as e:
            logger.error(f"Ollama API error: {e}", exc_info=True)
            raise Exception(f"Ollama API error: {str(e)}")

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
