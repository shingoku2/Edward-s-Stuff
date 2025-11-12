"""
AI Assistant Module
Handles AI queries using OpenAI or Anthropic APIs
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAssistant:
    """AI-powered gaming assistant"""

    MAX_CONVERSATION_MESSAGES = 20

    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None,
                 ollama_endpoint: str = "http://localhost:11434",
                 open_webui_api_key: Optional[str] = None):
        """
        Initialize AI Assistant

        Args:
            provider: 'openai', 'anthropic', 'gemini', or 'ollama'
            api_key: API key for the chosen provider
            ollama_endpoint: Ollama endpoint URL
            open_webui_api_key: API key for Open WebUI authentication
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.ollama_endpoint = ollama_endpoint
        self.open_webui_api_key = open_webui_api_key or os.getenv("OPEN_WEBUI_API_KEY")
        self.conversation_history = []
        self.current_game = None
        self.client = None
        self.default_ollama_model = "llama2"

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
            return None
        return None

    def _initialize_client(self):
        """Initialize the AI client"""
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
                logger.info(f"Ollama client configured at {self.ollama_endpoint}")
                
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

        game_name = game_info.get('name', 'Unknown Game')
        self._add_system_context(game_name)
        logger.info(f"Set current game context: {game_name}")

    def _add_system_context(self, game_name: str):
        """Add system context about the current game"""
        system_message = f"""You are a specialized gaming assistant for {game_name}.

Help with:
- Game strategies and tips
- Character/weapon/item builds
- Quest walkthroughs and missions
- Game mechanics and systems
- Controls and gameplay techniques
- Lore and story questions
- Where to find items, NPCs, or locations

Be concise, accurate, and helpful. Stay focused on {game_name}."""

        self.conversation_history.append({
            "role": "system",
            "content": system_message
        })

    def _trim_conversation_history(self):
        """Trim conversation history to prevent token limit issues"""
        if len(self.conversation_history) > self.MAX_CONVERSATION_MESSAGES:
            system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
            recent_messages = [msg for msg in self.conversation_history if msg["role"] != "system"]

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

        if not self.current_game:
            return "🎮 No game detected! Please start a game to get assistance."

        try:
            user_message = question.strip()

            if game_context:
                user_message = f"{question}\n\nContext: {game_context}"

            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            self._trim_conversation_history()

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
            messages = [{"role": msg["role"], "content": msg["content"]} for msg in self.conversation_history]

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "No response received from OpenAI"

        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            raise

    def _ask_anthropic(self) -> str:
        """Get response from Anthropic (Claude)"""
        try:
            system_msg = ""
            messages = []

            for msg in self.conversation_history:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    messages.append({"role": msg["role"], "content": msg["content"]})

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=system_msg,
                messages=messages
            )

            if response.content and len(response.content) > 0:
                return response.content[0].text
            return "No response received from Anthropic"

        except Exception as e:
            logger.error(f"Anthropic API error: {e}", exc_info=True)
            raise

    def _ask_gemini(self) -> str:
        """Get response from Google Gemini"""
        try:
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])
            response = self.client.generate_content(conversation_text)
            
            if response.text:
                return response.text
            return "No response received from Gemini"

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise

    def _ask_ollama(self) -> str:
        """Get response from Ollama (local LLM)"""
        try:
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])

            headers = {}
            if self.open_webui_api_key:
                headers["Authorization"] = f"Bearer {self.open_webui_api_key}"

            # Try native Ollama endpoint first
            url_native = f"{self.ollama_endpoint.rstrip('/')}/api/generate"
            payload_native = {
                "model": self.default_ollama_model,
                "prompt": conversation_text,
                "stream": False,
            }

            try:
                resp = requests.post(url_native, json=payload_native, headers=headers, timeout=30)
                if resp.status_code == 404 or resp.status_code == 401:
                    raise requests.HTTPError(f"Status {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and "response" in data:
                    return data["response"]
            except Exception:
                # Fallback: OpenAI-compatible API (Open WebUI)
                url_openai = f"{self.ollama_endpoint.rstrip('/')}/v1/chat/completions"
                messages = []
                system_msg = None
                for m in self.conversation_history:
                    if m["role"] == "system":
                        system_msg = m["content"]
                    else:
                        messages.append({"role": m["role"], "content": m["content"]})
                if system_msg:
                    messages.insert(0, {"role": "system", "content": system_msg})

                payload_openai = {
                    "model": self.default_ollama_model,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                }
                # Ensure Content-Type
                headers_fallback = {**headers, "Content-Type": "application/json"}
                resp2 = requests.post(url_openai, json=payload_openai, headers=headers_fallback, timeout=30)
                resp2.raise_for_status()
                data2 = resp2.json()
                # Parse OpenAI-style
                if isinstance(data2, dict):
                    choices = data2.get("choices")
                    if choices and isinstance(choices, list):
                        msg = choices[0].get("message") if choices[0] else None
                        if msg and isinstance(msg, dict):
                            content = msg.get("content")
                            if isinstance(content, str):
                                return content
                return "No response received from Ollama/Open WebUI"

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama connection error: {e}")
            raise Exception("Cannot connect to Ollama. Make sure it's running at " + self.ollama_endpoint)
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama timeout: {e}")
            raise Exception("Ollama request timed out")
        except Exception as e:
            logger.error(f"Ollama error: {e}", exc_info=True)
            raise

    def get_game_overview(self, game_name: str) -> str:
        """Get a general overview of the game"""
        question = f"Give me a brief overview of {game_name}, including genre, mechanics, and beginner tips."
        return self.ask_question(question)

    def get_tips_and_strategies(self, specific_topic: Optional[str] = None) -> str:
        """Get tips and strategies for the current game"""
        if not self.current_game:
            return "No game currently detected."

        game_name = self.current_game.get('name', 'the current game')

        if specific_topic:
            question = f"Give me tips and strategies for {specific_topic} in {game_name}."
        else:
            question = f"Give me some general tips for playing {game_name} effectively."

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
    provider = os.getenv("AI_PROVIDER", "anthropic")

    try:
        assistant = AIAssistant(provider=provider)
        assistant.set_current_game({"name": "League of Legends"})

        print("Testing AI Assistant...")
        print("\nQuestion: What are some tips for playing ADC?")

        response = assistant.ask_question("What are some tips for playing ADC?")
        print(f"\nResponse:\n{response}")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"Error: {e}")
