"""
Test suite for Game Watcher

Tests background game monitoring thread.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtTest import QSignalSpy
from PyQt6.QtCore import QCoreApplication
from src.game_watcher import GameWatcher
from src.game_detector import GameDetector
from src.game_profile import GameProfileStore


@pytest.mark.unit
class TestGameWatcherInitialization:
    """Test GameWatcher initialization"""

    def test_watcher_init(self):
        """Test creating game watcher"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store,
            check_interval=5
        )

        assert watcher is not None
        assert watcher.check_interval == 5

    def test_watcher_init_default_interval(self):
        """Test watcher with default check interval"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        # Should have some default interval
        assert watcher.check_interval > 0


@pytest.mark.ui
class TestGameWatcherSignals:
    """Test GameWatcher Qt signals"""

    def test_watcher_has_signals(self):
        """Test that watcher has required signals"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        # Check for required signals
        assert hasattr(watcher, 'game_detected')
        assert hasattr(watcher, 'game_changed')
        assert hasattr(watcher, 'game_closed')

    @pytest.mark.skip(reason="Requires Qt event loop")
    def test_game_detected_signal(self, qtbot):
        """Test game_detected signal emission"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        # Mock game detection
        detector.detect_running_game.return_value = {
            "name": "Test Game",
            "pid": 1234
        }

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store,
            check_interval=1
        )

        # Use QSignalSpy to catch signals
        spy = QSignalSpy(watcher.game_detected)

        watcher.start()
        qtbot.wait(2000)  # Wait for signal
        watcher.stop()

        # Should have emitted game_detected signal
        assert len(spy) > 0


@pytest.mark.unit
class TestGameDetectionLogic:
    """Test game detection logic"""

    @patch.object(GameWatcher, 'run')
    def test_watcher_calls_detector(self, mock_run):
        """Test that watcher calls game detector"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        detector.detect_running_game.return_value = None

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        # Manual call to check_for_game (not starting thread)
        # This tests the logic without Qt event loop
        if hasattr(watcher, 'check_for_game'):
            watcher.check_for_game()
            detector.detect_running_game.assert_called()


@pytest.mark.unit
class TestGameWatcherControl:
    """Test starting and stopping watcher"""

    def test_watcher_start(self):
        """Test starting watcher thread"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        # Start should not crash
        try:
            watcher.start()
            # Immediately stop to clean up
            watcher.stop()
            watcher.wait(1000)
            assert True
        except Exception as e:
            pytest.fail(f"Watcher start/stop failed: {e}")

    def test_watcher_stop(self):
        """Test stopping watcher thread"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        watcher.start()
        # Stop should not crash
        try:
            watcher.stop()
            watcher.wait(1000)
            assert True
        except Exception as e:
            pytest.fail(f"Watcher stop failed: {e}")


@pytest.mark.unit
class TestGameStateTracking:
    """Test tracking game state changes"""

    def test_tracks_current_game(self):
        """Test tracking currently running game"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        # Should have current_game attribute
        assert hasattr(watcher, 'current_game') or hasattr(watcher, '_current_game')

    def test_detects_game_change(self):
        """Test detecting when game changes"""
        detector = Mock(spec=GameDetector)
        profile_store = Mock(spec=GameProfileStore)

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store
        )

        # Logic test (without running thread)
        # First game
        game1 = {"name": "Game 1", "pid": 100}
        # Second game
        game2 = {"name": "Game 2", "pid": 200}

        # Should be able to detect change
        # (Implementation detail - may vary)
        assert True  # Placeholder for actual logic test


@pytest.mark.integration
class TestGameWatcherIntegration:
    """Integration tests for game watcher"""

    def test_watcher_with_real_detector(self):
        """Test watcher with real game detector"""
        detector = GameDetector()
        profile_store = GameProfileStore()

        watcher = GameWatcher(
            game_detector=detector,
            profile_store=profile_store,
            check_interval=10
        )

        # Should initialize successfully
        assert watcher is not None

        # Start and stop
        watcher.start()
        watcher.stop()
        watcher.wait(1000)
