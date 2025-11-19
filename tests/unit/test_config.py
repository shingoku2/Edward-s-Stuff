"""
Unit tests for Config module

Tests configuration management, API key handling, and persistence.
"""
import pytest
import os
from pathlib import Path


@pytest.mark.unit
class TestConfig:
    """Test Config module functionality"""

    def test_config_initialization(self, clean_config_dir):
        """Test creating a Config instance"""
        from config import Config

        config = Config(require_keys=False)
        assert config is not None
        assert hasattr(config, 'ai_provider')

    def test_config_ai_provider_default(self, clean_config_dir):
        """Test default AI provider setting"""
        from config import Config

        config = Config(require_keys=False)
        provider = config.ai_provider
        assert provider in ["anthropic", "openai", "gemini"]

    def test_config_has_provider_key(self, clean_config_dir):
        """Test checking if provider has key configured"""
        from config import Config

        config = Config(require_keys=False)
        # May or may not have keys - just test the method works
        result = config.has_provider_key()
        assert isinstance(result, bool)

    def test_config_overlay_settings(self, clean_config_dir):
        """Test overlay window settings exist"""
        from config import Config

        config = Config(require_keys=False)
        assert hasattr(config, 'overlay_x')
        assert hasattr(config, 'overlay_y')
        assert hasattr(config, 'overlay_width')
        assert hasattr(config, 'overlay_height')

    def test_config_get_effective_provider(self, clean_config_dir):
        """Test getting effective provider"""
        from config import Config

        config = Config(require_keys=False)
        effective = config.get_effective_provider()
        assert effective is None or effective in ["anthropic", "openai", "gemini"]

    def test_config_persistence(self, clean_config_dir, temp_dir):
        """Test saving and loading configuration"""
        from config import Config

        config_path = Path(temp_dir) / "test_config.json"
        config = Config(config_path=str(config_path), require_keys=False)

        # Set a test value
        config.overlay_width = 999
        config.save()

        # Load in new instance
        config2 = Config(config_path=str(config_path), require_keys=False)
        assert config2.overlay_width == 999


@pytest.mark.unit
class TestConfigEdgeCases:
    """Test Config edge cases and error handling"""

    def test_config_with_custom_path(self, temp_dir):
        """Test Config with custom config path"""
        from config import Config

        config_path = Path(temp_dir) / "custom_config.json"
        config = Config(config_path=str(config_path), require_keys=False)
        assert config is not None

    def test_config_get_with_default(self, clean_config_dir):
        """Test Config.get() with default value"""
        from config import Config

        config = Config(require_keys=False)
        value = config.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_config_update_multiple_values(self, clean_config_dir):
        """Test updating multiple values at once"""
        from config import Config

        config = Config(require_keys=False)
        config.update({"test1": "value1", "test2": "value2"})
        assert config.get("test1") == "value1"
        assert config.get("test2") == "value2"

    def test_config_reset_to_defaults(self, clean_config_dir):
        """Test resetting configuration to defaults"""
        from config import Config

        config = Config(require_keys=False)
        config.set("ai_provider", "test_provider")
        config.reset_to_defaults()
        assert config.get("ai_provider") == "anthropic"
