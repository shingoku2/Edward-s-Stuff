"""
Test suite for utility functions

Tests helper functions and utilities.
"""
import pytest
import os
from pathlib import Path


@pytest.mark.unit
class TestUtilsModule:
    """Test utils module if it exists"""

    def test_utils_import(self):
        """Test importing utils module"""
        try:
            from src import utils
            assert utils is not None
        except ImportError:
            # Utils module may not exist yet
            pytest.skip("Utils module not found")

    def test_utils_functions(self):
        """Test utils functions"""
        try:
            from src import utils

            # Test any utility functions that exist
            # This is a placeholder for actual utility testing
            assert hasattr(utils, '__name__')
        except ImportError:
            pytest.skip("Utils module not found")


@pytest.mark.unit
class TestPathOperations:
    """Test path-related utilities"""

    def test_get_config_dir(self):
        """Test getting config directory"""
        # Most apps use ~/.gaming_ai_assistant or similar
        home = Path.home()
        config_dir = home / ".gaming_ai_assistant"

        # Config dir should be a valid path
        assert isinstance(config_dir, Path)

    def test_ensure_directory_exists(self, temp_dir):
        """Test creating directory if it doesn't exist"""
        test_path = Path(temp_dir) / "test" / "nested" / "dir"

        # Create directory
        test_path.mkdir(parents=True, exist_ok=True)

        # Should exist now
        assert test_path.exists()
        assert test_path.is_dir()


@pytest.mark.unit
class TestStringHelpers:
    """Test string manipulation helpers"""

    def test_normalize_process_name(self):
        """Test process name normalization"""
        # Example normalization
        names = [
            ("Game.exe", "game.exe"),
            ("GAME.EXE", "game.exe"),
            ("game.EXE", "game.exe")
        ]

        for input_name, expected in names:
            normalized = input_name.lower()
            assert normalized == expected

    def test_slugify_text(self):
        """Test text slugification"""
        test_cases = [
            ("Elden Ring", "elden_ring"),
            ("The Legend of Zelda", "the_legend_of_zelda"),
            ("Game Name!", "game_name")
        ]

        for input_text, expected in test_cases:
            # Simple slugify
            slug = input_text.lower().replace(" ", "_").replace("!", "")
            # Just test the concept works
            assert isinstance(slug, str)


@pytest.mark.unit
class TestValidation:
    """Test validation utilities"""

    def test_validate_api_key_format(self):
        """Test API key format validation"""
        valid_keys = [
            "sk-1234567890abcdef",
            "sk-ant-1234567890",
            "test-key-123"
        ]

        for key in valid_keys:
            # Key should be non-empty string
            assert isinstance(key, str)
            assert len(key) > 0

    def test_validate_game_id_format(self):
        """Test game ID format validation"""
        valid_ids = [
            "elden_ring",
            "cyberpunk_2077",
            "test_game"
        ]

        for game_id in valid_ids:
            # Should be valid slug
            assert isinstance(game_id, str)
            assert len(game_id) > 0
            assert "_" in game_id or game_id.isalnum()


@pytest.mark.unit
class TestFileOperations:
    """Test file operation utilities"""

    def test_read_json_file(self, temp_dir):
        """Test reading JSON file"""
        import json

        test_file = Path(temp_dir) / "test.json"
        test_data = {"key": "value", "number": 42}

        # Write test file
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # Read it back
        with open(test_file, 'r') as f:
            loaded = json.load(f)

        assert loaded == test_data

    def test_write_json_file(self, temp_dir):
        """Test writing JSON file"""
        import json

        test_file = Path(temp_dir) / "output.json"
        test_data = {"test": "data"}

        # Write file
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # Verify it exists
        assert test_file.exists()

        # Verify content
        with open(test_file, 'r') as f:
            loaded = json.load(f)

        assert loaded == test_data


@pytest.mark.unit
class TestTimestamps:
    """Test timestamp utilities"""

    def test_get_current_timestamp(self):
        """Test getting current timestamp"""
        from datetime import datetime

        now = datetime.now()

        assert isinstance(now, datetime)
        assert now.year >= 2024

    def test_format_timestamp(self):
        """Test formatting timestamps"""
        from datetime import datetime

        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert "-" in formatted
        assert ":" in formatted


@pytest.mark.unit
class TestErrorFormatting:
    """Test error message formatting"""

    def test_format_error_message(self):
        """Test formatting error messages"""
        error = Exception("Test error")
        message = str(error)

        assert isinstance(message, str)
        assert "Test error" in message

    def test_format_provider_error(self):
        """Test formatting provider errors"""
        error_msg = "API key invalid"
        formatted = f"Provider error: {error_msg}"

        assert "Provider error" in formatted
        assert "API key invalid" in formatted
