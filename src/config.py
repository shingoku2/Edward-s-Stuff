"""
Configuration Module
Handles application configuration and settings
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration"""

    def __init__(self, env_file: Optional[str] = None, require_keys: bool = False):
        """
        Initialize configuration

        Args:
            env_file: Path to .env file (optional)
            require_keys: If True, raise error if API keys are missing (default: False)
        """
        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file, override=True)  # Override existing env vars
        else:
            # Try multiple locations for .env file
            # This handles both development and PyInstaller bundled scenarios
            possible_paths = [
                Path('.env'),  # Current working directory
                Path(__file__).parent.parent / '.env',  # Relative to this file
                Path(sys.executable).parent / '.env',  # Next to executable
            ]

            # For PyInstaller, also check sys._MEIPASS
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                bundle_dir = Path(sys.executable).parent
                possible_paths.insert(0, bundle_dir / '.env')

            for env_path in possible_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=True)  # Override existing env vars
                    # Log which file was loaded
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Loaded .env from: {env_path}")
                    break

        # AI Configuration
        self.ai_provider = os.getenv('AI_PROVIDER', 'anthropic').lower()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')

        # Application Settings
        self.overlay_hotkey = os.getenv('OVERLAY_HOTKEY', 'ctrl+shift+g')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))

        # Overlay Window Settings
        self.overlay_x = int(os.getenv('OVERLAY_X', '100'))
        self.overlay_y = int(os.getenv('OVERLAY_Y', '100'))
        self.overlay_width = int(os.getenv('OVERLAY_WIDTH', '900'))
        self.overlay_height = int(os.getenv('OVERLAY_HEIGHT', '700'))
        self.overlay_minimized = os.getenv('OVERLAY_MINIMIZED', 'false').lower() == 'true'

        # Validate configuration (only if required)
        if require_keys:
            self._validate()

    def _validate(self):
        """Validate configuration - raises ValueError if invalid"""
        # Check if we have the required API key for the provider
        if self.ai_provider == 'openai' and not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env")

        if self.ai_provider == 'anthropic' and not self.anthropic_api_key:
            raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in .env")

        if self.ai_provider == 'gemini' and not self.gemini_api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env")

        if self.ai_provider not in ['openai', 'anthropic', 'gemini']:
            raise ValueError(f"Invalid AI provider: {self.ai_provider}. Must be 'openai', 'anthropic', or 'gemini'")

    def is_configured(self) -> bool:
        """
        Check if configuration has valid API keys

        Returns:
            True if at least one API key is configured, False otherwise
        """
        return bool(
            self.openai_api_key or
            self.anthropic_api_key or
            self.gemini_api_key
        )

    def has_provider_key(self) -> bool:
        """
        Check if the selected provider has a valid API key

        Returns:
            True if current provider has an API key, False otherwise
        """
        if self.ai_provider == 'openai':
            return bool(self.openai_api_key)
        elif self.ai_provider == 'anthropic':
            return bool(self.anthropic_api_key)
        elif self.ai_provider == 'gemini':
            return bool(self.gemini_api_key)
        return False

    def get_api_key(self) -> str:
        """Get the API key for the selected provider"""
        if self.ai_provider == 'openai':
            return self.openai_api_key
        elif self.ai_provider == 'anthropic':
            return self.anthropic_api_key
        elif self.ai_provider == 'gemini':
            return self.gemini_api_key
        return None

    @staticmethod
    def save_to_env(provider: str, openai_key: str, anthropic_key: str, gemini_key: str = '',
                    overlay_hotkey: str = 'ctrl+shift+g', check_interval: int = 5,
                    overlay_x: int = None, overlay_y: int = None,
                    overlay_width: int = None, overlay_height: int = None,
                    overlay_minimized: bool = None):
        """
        Save configuration to .env file

        Args:
            provider: AI provider ('openai', 'anthropic', or 'gemini')
            openai_key: OpenAI API key
            anthropic_key: Anthropic API key
            gemini_key: Gemini API key (optional)
            overlay_hotkey: Hotkey for overlay (default: 'ctrl+shift+g')
            check_interval: Game check interval in seconds (default: 5)
            overlay_x: Overlay window X position (optional)
            overlay_y: Overlay window Y position (optional)
            overlay_width: Overlay window width (optional)
            overlay_height: Overlay window height (optional)
            overlay_minimized: Overlay minimized state (optional)
        """
        # Determine .env file location
        # Try multiple locations, prioritizing the most appropriate one
        possible_paths = [
            Path('.env'),  # Current working directory
            Path(__file__).parent.parent / '.env',  # Relative to this file (project root)
            Path(sys.executable).parent / '.env',  # Next to executable (for bundled app)
        ]

        # For PyInstaller bundles, use directory next to executable
        if getattr(sys, 'frozen', False):
            env_path = Path(sys.executable).parent / '.env'
        else:
            # In development, use project root
            env_path = Path(__file__).parent.parent / '.env'

        # Read existing .env file if it exists
        existing_content = {}
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_content[key.strip()] = value.strip()

        # Update with new values
        existing_content['AI_PROVIDER'] = provider
        existing_content['OPENAI_API_KEY'] = openai_key
        existing_content['ANTHROPIC_API_KEY'] = anthropic_key
        existing_content['GEMINI_API_KEY'] = gemini_key
        existing_content['OVERLAY_HOTKEY'] = overlay_hotkey
        existing_content['CHECK_INTERVAL'] = str(check_interval)

        # Update overlay settings if provided
        if overlay_x is not None:
            existing_content['OVERLAY_X'] = str(overlay_x)
        if overlay_y is not None:
            existing_content['OVERLAY_Y'] = str(overlay_y)
        if overlay_width is not None:
            existing_content['OVERLAY_WIDTH'] = str(overlay_width)
        if overlay_height is not None:
            existing_content['OVERLAY_HEIGHT'] = str(overlay_height)
        if overlay_minimized is not None:
            existing_content['OVERLAY_MINIMIZED'] = str(overlay_minimized).lower()

        # Write to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Gaming AI Assistant Configuration\n")
            f.write("# This file was generated by the Settings dialog\n\n")

            f.write("# AI Provider Selection\n")
            f.write(f"AI_PROVIDER={existing_content['AI_PROVIDER']}\n\n")

            f.write("# API Keys\n")
            f.write(f"OPENAI_API_KEY={existing_content['OPENAI_API_KEY']}\n")
            f.write(f"ANTHROPIC_API_KEY={existing_content['ANTHROPIC_API_KEY']}\n")
            f.write(f"GEMINI_API_KEY={existing_content['GEMINI_API_KEY']}\n\n")

            f.write("# Application Settings\n")
            f.write(f"OVERLAY_HOTKEY={existing_content['OVERLAY_HOTKEY']}\n")
            f.write(f"CHECK_INTERVAL={existing_content['CHECK_INTERVAL']}\n\n")

            # Write overlay settings if they exist
            if 'OVERLAY_X' in existing_content:
                f.write("# Overlay Window Settings\n")
                f.write(f"OVERLAY_X={existing_content.get('OVERLAY_X', '100')}\n")
                f.write(f"OVERLAY_Y={existing_content.get('OVERLAY_Y', '100')}\n")
                f.write(f"OVERLAY_WIDTH={existing_content.get('OVERLAY_WIDTH', '900')}\n")
                f.write(f"OVERLAY_HEIGHT={existing_content.get('OVERLAY_HEIGHT', '700')}\n")
                f.write(f"OVERLAY_MINIMIZED={existing_content.get('OVERLAY_MINIMIZED', 'false')}\n")

        return env_path

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
