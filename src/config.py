"""
Configuration Module
Handles loading and managing configuration
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        "ai_provider": "anthropic",
        "openai_api_key": "",
        "anthropic_api_key": "",
        "gemini_api_key": "",
        "ollama_endpoint": "http://localhost:11434",
        "open_webui_api_key": "",
        "overlay_width": 400,
        "overlay_height": 300,
        "overlay_opacity": 0.9,
        "overlay_font_size": 10,
        "overlay_hotkey": "Ctrl+Shift+O",
        "check_interval": 5,
        "auto_launch": False,
        "log_level": "INFO"
    }

    def __init__(self, config_path: Optional[str] = None, require_keys: bool = True):
        """
        Initialize configuration

        Args:
            config_path: Path to config file (optional)
            require_keys: Whether to enforce API keys at construction time (compatibility)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load_config()
        # Optionally merge from environment variables if present
        try:
            # Lazy import to avoid hard dependency
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass
        # Overlay simple env overrides when available
        self.config["ai_provider"] = os.getenv("AI_PROVIDER", self.config.get("ai_provider"))
        self.config["openai_api_key"] = os.getenv("OPENAI_API_KEY", self.config.get("openai_api_key"))
        self.config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY", self.config.get("anthropic_api_key"))
        self.config["gemini_api_key"] = os.getenv("GEMINI_API_KEY", self.config.get("gemini_api_key"))
        self.config["ollama_endpoint"] = os.getenv("OLLAMA_ENDPOINT", self.config.get("ollama_endpoint"))
        self.config["open_webui_api_key"] = os.getenv("OPEN_WEBUI_API_KEY", self.config.get("open_webui_api_key"))

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        if os.name == 'nt':  # Windows
            config_dir = os.path.expandvars(r'%APPDATA%\GamingAIAssistant')
        else:  # Unix/Linux
            config_dir = os.path.expanduser('~/.config/gaming-ai-assistant')

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')

    def load_config(self) -> bool:
        """
        Load configuration from file

        Returns:
            True if loaded successfully
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle missing keys
                    self.config.update(loaded_config)
                logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                logger.info("No existing config file found, using defaults")
                self.save_config()
                return False

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            return False
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            self.config = self.DEFAULT_CONFIG.copy()
            return False

    def save_config(self) -> bool:
        """
        Save configuration to file

        Returns:
            True if saved successfully
        """
        try:
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

            logger.info(f"Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}", exc_info=True)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value

    # Provide attribute-style access for known keys used throughout the app
    def __getattr__(self, name: str):
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"Config has no attribute '{name}'")

    def is_configured(self) -> bool:
        """Return True if the selected provider has necessary credentials (or is ollama)."""
        provider = (self.config.get("ai_provider") or "").lower()
        if provider == "ollama":
            return True
        if provider == "openai":
            return bool(self.config.get("openai_api_key"))
        if provider == "anthropic":
            return bool(self.config.get("anthropic_api_key"))
        if provider == "gemini":
            return bool(self.config.get("gemini_api_key"))
        return False

    def has_provider_key(self) -> bool:
        """Alias used by main.py/GUI to check if a provider key is available."""
        return self.is_configured()

    def get_api_key(self) -> Optional[str]:
        """Return API key for current provider if applicable."""
        provider = (self.config.get("ai_provider") or "").lower()
        if provider == "openai":
            return self.config.get("openai_api_key")
        if provider == "anthropic":
            return self.config.get("anthropic_api_key")
        if provider == "gemini":
            return self.config.get("gemini_api_key")
        # Ollama doesn't need an API key
        return None

    @classmethod
    def save_to_env(
        cls,
        provider: str,
        openai_key: str,
        anthropic_key: str,
        gemini_key: str,
        ollama_endpoint: str,
        open_webui_api_key: str,
        *,
        overlay_hotkey: str,
        overlay_width: int,
        overlay_height: int,
        overlay_opacity: float,
        overlay_font_size: int,
        check_interval: int = 5,
        env_path: Optional[str] = None,
    ) -> None:
        """Persist settings to .env and config.json for GUI usage.

        This keeps compatibility with pre-existing build scripts that rely on .env
        and also updates the JSON config used at runtime.
        """
        # Compute .env path (next to current working directory executable/script)
        env_path = env_path or os.path.join(os.getcwd(), ".env")

        # Load existing .env
        env_data: Dict[str, str] = {}
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            env_data[k.strip()] = v.strip()
            except Exception:
                # Ignore malformed existing env
                pass

        # Update values
        env_data.update({
            "AI_PROVIDER": provider,
            "OPENAI_API_KEY": openai_key or "",
            "ANTHROPIC_API_KEY": anthropic_key or "",
            "GEMINI_API_KEY": gemini_key or "",
            "OLLAMA_ENDPOINT": ollama_endpoint or "",
            "OPEN_WEBUI_API_KEY": open_webui_api_key or "",
            "OVERLAY_HOTKEY": overlay_hotkey or "Ctrl+Shift+O",
            "OVERLAY_WIDTH": str(overlay_width),
            "OVERLAY_HEIGHT": str(overlay_height),
            "OVERLAY_OPACITY": str(overlay_opacity),
            "OVERLAY_FONT_SIZE": str(overlay_font_size),
            "CHECK_INTERVAL": str(check_interval),
        })

        # Write .env
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                for k in sorted(env_data.keys()):
                    f.write(f"{k}={env_data[k]}\n")
            logger.info(f".env saved to {env_path}")
        except Exception as e:
            logger.warning(f"Failed to save .env: {e}")

        # Update JSON config
        cfg = cls()
        cfg.update({
            "ai_provider": provider,
            "openai_api_key": openai_key or "",
            "anthropic_api_key": anthropic_key or "",
            "gemini_api_key": gemini_key or "",
            "ollama_endpoint": ollama_endpoint or cfg.get("ollama_endpoint"),
            "open_webui_api_key": open_webui_api_key or "",
            "overlay_hotkey": overlay_hotkey or cfg.get("overlay_hotkey"),
            "overlay_width": overlay_width,
            "overlay_height": overlay_height,
            "overlay_opacity": overlay_opacity,
            "overlay_font_size": overlay_font_size,
            "check_interval": check_interval,
        })
        cfg.save_config()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with dictionary

        Args:
            config_dict: Dictionary with configuration updates
        """
        self.config.update(config_dict)

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate that required API keys are set

        Returns:
            Dictionary with validation results
        """
        provider = self.get("ai_provider", "anthropic").lower()

        validation = {
            "provider_set": provider in ["openai", "anthropic", "gemini", "ollama"],
            "openai_key_set": bool(self.get("openai_api_key")),
            "anthropic_key_set": bool(self.get("anthropic_api_key")),
            "gemini_key_set": bool(self.get("gemini_api_key")),
        }

        # Validate based on selected provider
        if provider == "openai":
            validation["provider_valid"] = validation["openai_key_set"]
        elif provider == "anthropic":
            validation["provider_valid"] = validation["anthropic_key_set"]
        elif provider == "gemini":
            validation["provider_valid"] = validation["gemini_key_set"]
        elif provider == "ollama":
            validation["provider_valid"] = True  # Ollama doesn't require API key
        else:
            validation["provider_valid"] = False

        return validation

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        logger.info("Configuration reset to defaults")

    def __repr__(self) -> str:
        """String representation of config"""
        return f"Config(path={self.config_path}, keys={list(self.config.keys())})"


if __name__ == "__main__":
    config = Config()

    print("Current configuration:")
    for key, value in config.get_all().items():
        # Hide API keys for security
        if "key" in key.lower() or "token" in key.lower():
            value = "***hidden***" if value else "not set"
        print(f"  {key}: {value}")

    print("\nValidation:")
    validation = config.validate_api_keys()
    for check, result in validation.items():
        print(f"  {check}: {result}")
