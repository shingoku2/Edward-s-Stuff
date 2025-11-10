"""
Configuration Module
Handles application configuration and settings
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration"""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration

        Args:
            env_file: Path to .env file (optional)
        """
        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            # Try to load from default location
            env_path = Path(__file__).parent.parent / '.env'
            if env_path.exists():
                load_dotenv(env_path)

        # AI Configuration
        self.ai_provider = os.getenv('AI_PROVIDER', 'anthropic').lower()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        # Application Settings
        self.overlay_hotkey = os.getenv('OVERLAY_HOTKEY', 'ctrl+shift+g')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))

        # Validate configuration
        self._validate()

    def _validate(self):
        """Validate configuration"""
        # Check if we have at least one API key
        if self.ai_provider == 'openai' and not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env")

        if self.ai_provider == 'anthropic' and not self.anthropic_api_key:
            raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in .env")

        if self.ai_provider not in ['openai', 'anthropic']:
            raise ValueError(f"Invalid AI provider: {self.ai_provider}. Must be 'openai' or 'anthropic'")

    def get_api_key(self) -> str:
        """Get the API key for the selected provider"""
        if self.ai_provider == 'openai':
            return self.openai_api_key
        elif self.ai_provider == 'anthropic':
            return self.anthropic_api_key
        return None

    def __repr__(self):
        """String representation"""
        return f"Config(provider={self.ai_provider}, hotkey={self.overlay_hotkey})"


if __name__ == "__main__":
    # Test configuration
    try:
        config = Config()
        print("Configuration loaded successfully:")
        print(config)
        print(f"API Key present: {'Yes' if config.get_api_key() else 'No'}")
    except Exception as e:
        print(f"Configuration error: {e}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to .env")
        print("3. Set AI_PROVIDER to 'openai' or 'anthropic'")
