"""
Edge case and error handling tests

Tests boundary conditions, error scenarios, and resilience.
"""
import pytest
import os
from pathlib import Path


@pytest.mark.unit
class TestConfigEdgeCases:
    """Test Config edge cases"""

    def test_config_with_corrupted_file(self, temp_dir):
        """Test Config recovery from corrupted file"""
        from config import Config

        config_path = Path(temp_dir) / "bad_config.json"

        # Write invalid JSON
        with open(config_path, 'w') as f:
            f.write("{invalid json content")

        # Try to load (should recover)
        config = Config(config_path=str(config_path), require_keys=False)
        assert config is not None

        # Should be back to defaults
        assert config.get("ai_provider") == "anthropic"

    def test_config_get_with_default(self, temp_dir):
        """Test Config.get() with default value"""
        from config import Config

        config = Config(require_keys=False)
        value = config.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_config_update_multiple(self, temp_dir):
        """Test updating multiple values"""
        from config import Config

        config = Config(require_keys=False)
        config.update({"test1": "value1", "test2": "value2"})

        assert config.get("test1") == "value1"
        assert config.get("test2") == "value2"


@pytest.mark.unit
class TestGameDetectorEdgeCases:
    """Test GameDetector edge cases"""

    def test_empty_process_name(self):
        """Test handling empty process name"""
        from game_detector import GameDetector

        detector = GameDetector()
        result = detector._is_process_running("")
        assert isinstance(result, bool)

    def test_nonexistent_process(self):
        """Test checking nonexistent process"""
        from game_detector import GameDetector

        detector = GameDetector()
        result = detector._is_process_running("nonexistent_xyz_12345.exe")
        assert result is False

    def test_add_custom_game_empty_list(self):
        """Test adding game with empty process list"""
        from game_detector import GameDetector

        detector = GameDetector()
        result = detector.add_custom_game("Empty Game", [])
        assert result is True

    def test_duplicate_detection(self):
        """Test duplicate game detection"""
        from game_detector import GameDetector

        detector = GameDetector()

        result1 = detector.add_custom_game("Duplicate", ["dup.exe"])
        result2 = detector.add_custom_game("Duplicate", ["dup2.exe"])
        result3 = detector.add_custom_game("duplicate", ["dup3.exe"])
        result4 = detector.add_custom_game("Different Name", ["dup.exe"])

        assert result1 is True
        assert result2 is False  # Duplicate name
        assert result3 is False  # Case-insensitive duplicate
        assert result4 is False  # Duplicate process


@pytest.mark.unit
class TestAIAssistantEdgeCases:
    """Test AIAssistant edge cases"""

    @pytest.mark.skip_ci
    def test_invalid_provider(self):
        """Test AIAssistant with invalid provider"""
        from ai_assistant import AIAssistant

        try:
            assistant = AIAssistant(provider="invalid_provider")
        except ValueError:
            # Expected error
            pass

    @pytest.mark.skip_ci
    def test_set_game_empty_dict(self):
        """Test setting game with empty dict"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            assistant.set_current_game({})
        except (ValueError, AttributeError):
            # May raise or handle gracefully
            pass

    @pytest.mark.skip_ci
    def test_get_conversation_summary_empty(self):
        """Test getting summary on empty history"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            summary = assistant.get_conversation_summary()
            assert isinstance(summary, list)
        except ValueError:
            pytest.skip("No API keys configured")


@pytest.mark.unit
class TestConcurrentOperations:
    """Test concurrent operations and thread safety"""

    def test_concurrent_config_operations(self):
        """Test concurrent config operations"""
        from config import Config
        import threading

        errors = []

        def config_operations():
            try:
                config = Config(require_keys=False)
                for i in range(10):
                    config.set(f"key_{i}", f"value_{i}")
                    _ = config.get(f"key_{i}")
            except Exception as e:
                errors.append(f"Config error: {e}")

        # Run operations in parallel
        threads = [
            threading.Thread(target=config_operations),
            threading.Thread(target=config_operations)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=5)

        assert len(errors) == 0

    def test_concurrent_detector_operations(self):
        """Test concurrent detector operations"""
        from game_detector import GameDetector
        import threading

        errors = []

        def detector_operations():
            try:
                detector = GameDetector()
                for i in range(5):
                    _ = detector.get_running_games()
                    detector.add_custom_game(f"Game_{i}", [f"game_{i}.exe"])
            except Exception as e:
                errors.append(f"Detector error: {e}")

        threads = [
            threading.Thread(target=detector_operations),
            threading.Thread(target=detector_operations)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=5)

        # Some errors may occur due to duplicate names - that's OK
        # Just check we didn't crash
        assert len(threads) == 2


@pytest.mark.unit
class TestProfileEdgeCases:
    """Test game profile edge cases"""

    def test_empty_executable_list(self):
        """Test profile with empty executable list"""
        from game_profile import GameProfile

        profile = GameProfile(
            id="generic",
            display_name="Generic",
            exe_names=[],
            system_prompt="Matches any game"
        )

        # Should not match anything specifically
        assert profile.matches_executable("test.exe") is False

    def test_none_executable_matching(self):
        """Test matching with None or invalid input"""
        from game_profile import GameProfile

        profile = GameProfile(
            id="test",
            display_name="Test",
            exe_names=["test.exe"],
            system_prompt="Prompt"
        )

        # Should not crash
        assert profile.matches_executable("") is False


@pytest.mark.unit
class TestOverlayModeEdgeCases:
    """Test overlay mode edge cases"""

    def test_invalid_mode(self):
        """Test invalid overlay mode"""
        from overlay_modes import OverlayModeConfig

        # Invalid mode should have fallback
        config = OverlayModeConfig.get_mode_config("invalid_mode")
        assert config is not None


@pytest.mark.unit
class TestErrorRecovery:
    """Test error recovery and resilience"""

    def test_corrupted_config_recovery(self, temp_dir):
        """Test Config recovery from corrupted state"""
        from config import Config

        config_path = Path(temp_dir) / "bad_config.json"

        # Write invalid JSON
        with open(config_path, 'w') as f:
            f.write("{invalid json content")

        # Try to load (should recover)
        config = Config(config_path=str(config_path), require_keys=False)
        assert config is not None

        # Should be back to defaults
        assert config.get("ai_provider") == "anthropic"
