"""
Test suite for Config module

Tests configuration loading, saving, and defaults.
"""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from omnix.config import Config


@pytest.mark.unit
class TestConfig:
    """Test Config functionality"""

    def test_config_initialization(self, temp_config_dir):
        """Test config initialization"""
        config = Config(config_dir=str(temp_config_dir))
        assert config is not None
        assert config.config_dir == str(temp_config_dir)

    def test_config_ai_provider_default(self, temp_config_dir, monkeypatch):
        """Test default AI provider is set"""
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        config = Config(config_dir=str(temp_config_dir))
        # Defaults to ollama
        assert config.ai_provider == "ollama"

    def test_config_has_provider_key(self, temp_config_dir):
        """Test has_provider_key check"""
        config = Config(config_dir=str(temp_config_dir))

        # Ollama always has "key" (it doesn't need one)
        assert config.has_provider_key("ollama") is True

    def test_config_overlay_settings(self, temp_config_dir):
        """Test overlay settings"""
        config = Config(config_dir=str(temp_config_dir))

        # Check defaults
        assert config.overlay_width == 900
        assert config.overlay_height == 700
        assert config.overlay_opacity == 0.95

    def test_config_get_effective_provider(self, temp_config_dir):
        """Test getting effective provider"""
        config = Config(config_dir=str(temp_config_dir))
        assert config.get_effective_provider() == "ollama"

    def test_config_persistence(self, temp_config_dir, temp_dir):
        """Test saving and loading configuration"""
        from omnix.config import Config

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
        from omnix.config import Config

        config_path = Path(temp_dir) / "custom_config.json"
        config = Config(config_path=str(config_path), require_keys=False)
        assert config is not None

    def test_config_get_with_default(self, temp_config_dir):
        """Test Config.get() with default value"""
        from omnix.config import Config

        config = Config(require_keys=False)
        value = config.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_config_update_multiple_values(self, temp_config_dir):
        """Test updating multiple values at once"""
        from omnix.config import Config

        config = Config(require_keys=False)
        config.update({"test1": "value1", "test2": "value2"})
        assert config.get("test1") == "value1"
        assert config.get("test2") == "value2"

    def test_config_reset_to_defaults(self, temp_config_dir):
        """Test resetting configuration to defaults"""
        from omnix.config import Config

        config = Config(require_keys=False)
        config.set("ai_provider", "test_provider")
        config.reset_to_defaults()
        assert config.get("ai_provider") == "ollama"
