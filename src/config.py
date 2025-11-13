"""
Configuration Module
Handles application configuration and settings
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

from credential_store import CredentialDecryptionError, CredentialStore, CredentialStoreError

logger = logging.getLogger(__name__)

# Configuration directory
CONFIG_DIR = Path.home() / '.gaming_ai_assistant'
KEYBINDS_FILE = CONFIG_DIR / 'keybinds.json'
MACROS_FILE = CONFIG_DIR / 'macros.json'
THEME_FILE = CONFIG_DIR / 'theme.json'


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
                    logger.info("Loaded .env from: %s", env_path)
                    break

        # Secure credential storage
        self.credential_store = CredentialStore()
        credentials = self._load_secure_credentials()

        # AI Configuration
        self.ai_provider = os.getenv('AI_PROVIDER', 'anthropic').lower()
        self.openai_api_key = credentials.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = credentials.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.gemini_api_key = credentials.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')

        # Session data captured via embedded login
        self.session_tokens: Dict[str, dict] = {}
        self._load_session_token('openai', os.getenv('OPENAI_SESSION_DATA'))
        self._load_session_token('anthropic', os.getenv('ANTHROPIC_SESSION_DATA'))
        self._load_session_token('gemini', os.getenv('GEMINI_SESSION_DATA'))

        # Application Settings
        self.overlay_hotkey = os.getenv('OVERLAY_HOTKEY', 'ctrl+shift+g')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))

        # Overlay Window Settings
        self.overlay_x = int(os.getenv('OVERLAY_X', '100'))
        self.overlay_y = int(os.getenv('OVERLAY_Y', '100'))
        self.overlay_width = int(os.getenv('OVERLAY_WIDTH', '900'))
        self.overlay_height = int(os.getenv('OVERLAY_HEIGHT', '700'))
        self.overlay_minimized = os.getenv('OVERLAY_MINIMIZED', 'false').lower() == 'true'
        self.overlay_opacity = float(os.getenv('OVERLAY_OPACITY', '0.95'))

        # Extended Settings (stored in separate JSON files)
        self.keybinds: Dict = {}
        self.macros: Dict = {}
        self.theme: Dict = {}

        # Load extended settings
        self._load_keybinds()
        self._load_macros()
        self._load_theme()

        # Validate configuration (only if required)
        if require_keys:
            self._validate()

    def _load_session_token(self, provider: str, raw_value: Optional[str]) -> None:
        """Parse stored session information from .env."""
        if not raw_value:
            return

        try:
            parsed = json.loads(raw_value.strip("'\""))
            if isinstance(parsed, dict):
                self.session_tokens[provider] = parsed
        except json.JSONDecodeError:
            self.session_tokens[provider] = {"raw": raw_value}

    def _validate(self):
        """Validate configuration - raises ValueError if invalid"""
        # Check if we have the required API key for the provider
        if self.ai_provider == 'openai' and not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please add it via the Settings dialog.")

        if self.ai_provider == 'anthropic' and not self.anthropic_api_key:
            raise ValueError("Anthropic API key not found. Please add it via the Settings dialog.")

        if self.ai_provider == 'gemini' and not self.gemini_api_key:
            raise ValueError("Gemini API key not found. Please add it via the Settings dialog.")

        if self.ai_provider not in ['openai', 'anthropic', 'gemini']:
            raise ValueError(f"Invalid AI provider: {self.ai_provider}. Must be 'openai', 'anthropic', or 'gemini'")

    def _load_secure_credentials(self) -> dict:
        """Load credentials from the encrypted store with graceful fallbacks."""
        try:
            return self.credential_store.load_credentials()
        except CredentialDecryptionError as exc:
            logger.error("Failed to decrypt stored credentials: %s", exc)
            return {}
        except CredentialStoreError as exc:
            logger.warning("Unable to load credentials from secure store: %s", exc)
            return {}

    def _load_keybinds(self):
        """Load keybinds from JSON file"""
        try:
            if KEYBINDS_FILE.exists():
                with open(KEYBINDS_FILE, 'r', encoding='utf-8') as f:
                    self.keybinds = json.load(f)
                    logger.info(f"Loaded {len(self.keybinds)} keybinds from {KEYBINDS_FILE}")
            else:
                logger.info("No keybinds file found, using defaults")
                self.keybinds = {}
        except Exception as e:
            logger.error(f"Failed to load keybinds: {e}")
            self.keybinds = {}

    def _load_macros(self):
        """Load macros from JSON file"""
        try:
            if MACROS_FILE.exists():
                with open(MACROS_FILE, 'r', encoding='utf-8') as f:
                    self.macros = json.load(f)
                    logger.info(f"Loaded {len(self.macros)} macros from {MACROS_FILE}")
            else:
                logger.info("No macros file found, using defaults")
                self.macros = {}
        except Exception as e:
            logger.error(f"Failed to load macros: {e}")
            self.macros = {}

    def _load_theme(self):
        """Load theme from JSON file"""
        try:
            if THEME_FILE.exists():
                with open(THEME_FILE, 'r', encoding='utf-8') as f:
                    self.theme = json.load(f)
                    logger.info(f"Loaded theme from {THEME_FILE}")
            else:
                logger.info("No theme file found, using defaults")
                self.theme = {}
        except Exception as e:
            logger.error(f"Failed to load theme: {e}")
            self.theme = {}

    def save_keybinds(self, keybinds: Dict) -> bool:
        """
        Save keybinds to JSON file

        Args:
            keybinds: Dictionary of keybind data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure config directory exists
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(KEYBINDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(keybinds, f, indent=2)

            self.keybinds = keybinds
            logger.info(f"Saved {len(keybinds)} keybinds to {KEYBINDS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save keybinds: {e}")
            return False

    def save_macros(self, macros: Dict) -> bool:
        """
        Save macros to JSON file

        Args:
            macros: Dictionary of macro data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure config directory exists
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(MACROS_FILE, 'w', encoding='utf-8') as f:
                json.dump(macros, f, indent=2)

            self.macros = macros
            logger.info(f"Saved {len(macros)} macros to {MACROS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save macros: {e}")
            return False

    def save_theme(self, theme: Dict) -> bool:
        """
        Save theme to JSON file

        Args:
            theme: Dictionary of theme data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure config directory exists
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(THEME_FILE, 'w', encoding='utf-8') as f:
                json.dump(theme, f, indent=2)

            self.theme = theme
            logger.info(f"Saved theme to {THEME_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save theme: {e}")
            return False

    def is_configured(self) -> bool:
        """
        Check if configuration has valid credentials (API keys or session tokens)

        Returns:
            True if at least one API key or session token is configured, False otherwise
        """
        # Check API keys
        has_api_key = bool(
            self.openai_api_key or
            self.anthropic_api_key or
            self.gemini_api_key
        )

        # Check session tokens
        has_session = bool(self.session_tokens.get('openai') or
                          self.session_tokens.get('anthropic') or
                          self.session_tokens.get('gemini'))

        return has_api_key or has_session


    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """
        Get the API key for a specific provider or the currently selected provider.

        Args:
            provider: Provider name ('openai', 'anthropic', 'gemini').
                     If None, uses the current AI_PROVIDER setting.

        Returns:
            API key if found, None otherwise
        """
        target_provider = (provider or self.ai_provider).lower()

        if target_provider == 'openai':
            return self.openai_api_key
        elif target_provider == 'anthropic':
            return self.anthropic_api_key
        elif target_provider == 'gemini':
            return self.gemini_api_key
        return None

    def set_api_key(self, provider: str, api_key: Optional[str]) -> None:
        """
        Set an API key for a provider and persist it to secure storage.

        Args:
            provider: Provider name ('openai', 'anthropic', 'gemini')
            api_key: The API key to store (None to clear)
        """
        provider = provider.lower()

        if api_key:
            # Save to both in-memory and secure storage
            if provider == 'openai':
                self.openai_api_key = api_key
            elif provider == 'anthropic':
                self.anthropic_api_key = api_key
            elif provider == 'gemini':
                self.gemini_api_key = api_key
            else:
                logger.warning(f"Unknown provider: {provider}")
                return

            # Persist to secure credential store
            try:
                self.credential_store.save_credentials({f'{provider.upper()}_API_KEY': api_key})
                logger.info(f"Saved API key for provider: {provider}")
            except Exception as e:
                logger.error(f"Failed to save API key for {provider}: {e}")
        else:
            # Clear the key
            self.clear_api_key(provider)

    def clear_api_key(self, provider: str) -> None:
        """
        Clear an API key for a provider.

        Args:
            provider: Provider name ('openai', 'anthropic', 'gemini')
        """
        provider = provider.lower()

        # Clear from memory
        if provider == 'openai':
            self.openai_api_key = None
        elif provider == 'anthropic':
            self.anthropic_api_key = None
        elif provider == 'gemini':
            self.gemini_api_key = None
        else:
            logger.warning(f"Unknown provider: {provider}")
            return

        # Remove from secure storage
        try:
            self.credential_store.delete(f'{provider.upper()}_API_KEY')
            logger.info(f"Cleared API key for provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to clear API key for {provider}: {e}")

    def get_effective_provider(self) -> str:
        """
        Get the effective provider to use.

        Returns the currently selected provider if it has an API key configured,
        otherwise returns the first available provider with a key.

        Returns:
            Provider name ('openai', 'anthropic', 'gemini')
        """
        # First check if current provider has a key
        if self.has_provider_key(self.ai_provider):
            return self.ai_provider

        # Try other providers in order
        for provider in ['anthropic', 'openai', 'gemini']:
            if self.has_provider_key(provider):
                return provider

        # Fallback to configured provider even if no key
        return self.ai_provider

    def has_provider_key(self, provider: Optional[str] = None) -> bool:
        """
        Check if a provider has valid credentials (API key or session token).

        Args:
            provider: Provider name. If None, checks the current AI_PROVIDER.

        Returns:
            True if the provider has an API key or session token, False otherwise
        """
        target_provider = (provider or self.ai_provider).lower()
        has_api_key = False
        has_session = bool(self.session_tokens.get(target_provider))

        if target_provider == 'openai':
            has_api_key = bool(self.openai_api_key)
        elif target_provider == 'anthropic':
            has_api_key = bool(self.anthropic_api_key)
        elif target_provider == 'gemini':
            has_api_key = bool(self.gemini_api_key)

        return has_api_key or has_session

    @staticmethod
    def save_to_env(provider: str, openai_key: str = '', anthropic_key: str = '', gemini_key: str = '',
                    session_tokens: Optional[Dict[str, dict]] = None,
                    overlay_hotkey: str = 'ctrl+shift+g', check_interval: int = 5,
                    overlay_x: int = None, overlay_y: int = None,
                    overlay_width: int = None, overlay_height: int = None,
                    overlay_minimized: bool = None, overlay_opacity: float = None):
        """
        Save configuration to .env file

        Args:
            provider: AI provider ('openai', 'anthropic', or 'gemini')
            overlay_hotkey: Hotkey for overlay (default: 'ctrl+shift+g')
            check_interval: Game check interval in seconds (default: 5)
            overlay_x: Overlay window X position (optional)
            overlay_y: Overlay window Y position (optional)
            overlay_width: Overlay window width (optional)
            overlay_height: Overlay window height (optional)
            overlay_minimized: Overlay minimized state (optional)
            overlay_opacity: Overlay opacity 0.0-1.0 (optional)
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
        existing_content['OPENAI_API_KEY'] = ''
        existing_content['ANTHROPIC_API_KEY'] = ''
        existing_content['GEMINI_API_KEY'] = ''
        existing_content['OVERLAY_HOTKEY'] = overlay_hotkey
        existing_content['CHECK_INTERVAL'] = str(check_interval)

        session_tokens = session_tokens or {}
        existing_content['OPENAI_SESSION_DATA'] = json.dumps(session_tokens.get('openai', {}))
        existing_content['ANTHROPIC_SESSION_DATA'] = json.dumps(session_tokens.get('anthropic', {}))
        existing_content['GEMINI_SESSION_DATA'] = json.dumps(session_tokens.get('gemini', {}))

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
        if overlay_opacity is not None:
            existing_content['OVERLAY_OPACITY'] = str(overlay_opacity)

        # Write to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Gaming AI Assistant Configuration\n")
            f.write("# This file was generated by the Settings dialog\n\n")

            f.write("# AI Provider Selection\n")
            f.write(f"AI_PROVIDER={existing_content['AI_PROVIDER']}\n\n")

            f.write("# API Keys are stored securely using the encrypted credential store\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("ANTHROPIC_API_KEY=\n")
            f.write("GEMINI_API_KEY=\n\n")

            f.write("# Session Tokens\n")
            f.write(f"OPENAI_SESSION_DATA='{existing_content['OPENAI_SESSION_DATA']}'\n")
            f.write(f"ANTHROPIC_SESSION_DATA='{existing_content['ANTHROPIC_SESSION_DATA']}'\n")
            f.write(f"GEMINI_SESSION_DATA='{existing_content['GEMINI_SESSION_DATA']}'\n\n")

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
                f.write(f"OVERLAY_OPACITY={existing_content.get('OVERLAY_OPACITY', '0.95')}\n")

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
        print("1. Launch the Gaming AI Assistant application.")
        print("2. Open the ⚙️ Settings dialog and enter your API key(s).")
        print("3. Choose your preferred AI provider from the Settings dialog.")
