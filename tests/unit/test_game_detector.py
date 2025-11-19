"""
Unit tests for GameDetector module

Tests game process detection, custom game management, and executable matching.
"""
import pytest


@pytest.mark.unit
class TestGameDetector:
    """Test GameDetector module functionality"""

    def test_detector_initialization(self):
        """Test creating a GameDetector instance"""
        from game_detector import GameDetector

        detector = GameDetector()
        assert detector is not None
        assert hasattr(detector, 'common_games')

    def test_known_games_exists(self):
        """Test that KNOWN_GAMES attribute exists (legacy compatibility)"""
        from game_detector import GameDetector

        detector = GameDetector()
        assert hasattr(detector, 'KNOWN_GAMES')
        assert isinstance(detector.KNOWN_GAMES, dict)

    def test_common_games_populated(self):
        """Test that common_games has pre-configured games"""
        from game_detector import GameDetector

        detector = GameDetector()
        assert len(detector.common_games) > 0

    def test_detect_running_game(self):
        """Test detecting currently running game"""
        from game_detector import GameDetector

        detector = GameDetector()
        game = detector.detect_running_game()
        # May be None if no supported game is running
        assert game is None or isinstance(game, dict)

    def test_get_running_games(self):
        """Test getting all running games"""
        from game_detector import GameDetector

        detector = GameDetector()
        games = detector.get_running_games()
        assert isinstance(games, list)

    def test_add_custom_game(self):
        """Test adding a custom game"""
        from game_detector import GameDetector

        detector = GameDetector()
        success = detector.add_custom_game("Test Game", ["test.exe"])
        assert success is True
        assert "Test Game" in detector.common_games

    def test_add_duplicate_game_fails(self):
        """Test that adding duplicate game fails"""
        from game_detector import GameDetector

        detector = GameDetector()
        # First add succeeds
        detector.add_custom_game("Unique Game", ["unique.exe"])
        # Second add with same name fails
        result = detector.add_custom_game("Unique Game", ["different.exe"])
        assert result is False

    def test_add_duplicate_process_fails(self):
        """Test that adding duplicate process fails"""
        from game_detector import GameDetector

        detector = GameDetector()
        detector.add_custom_game("Game 1", ["shared.exe"])
        # Try to use same process for different game
        result = detector.add_custom_game("Game 2", ["shared.exe"])
        assert result is False


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
        """Test checking for nonexistent process"""
        from game_detector import GameDetector

        detector = GameDetector()
        result = detector._is_process_running("nonexistent_xyz_12345.exe")
        assert result is False

    def test_add_custom_game_empty_list(self):
        """Test adding game with empty process list"""
        from game_detector import GameDetector

        detector = GameDetector()
        result = detector.add_custom_game("Empty Game", [])
        # Should succeed - generic game profiles can have empty exe list
        assert result is True

    def test_case_insensitive_matching(self):
        """Test that game matching is case-insensitive"""
        from game_detector import GameDetector

        detector = GameDetector()
        # Add game with lowercase
        detector.add_custom_game("Test Game", ["test.exe"])
        # Try to add with different case - should fail (duplicate)
        result = detector.add_custom_game("TEST GAME", ["other.exe"])
        assert result is False
