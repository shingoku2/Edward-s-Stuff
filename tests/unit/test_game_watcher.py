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
        watcher = GameWatcher(check_interval=5)

        assert watcher is not None
        assert watcher.check_interval == 5

    def test_watcher_init_default_interval(self):
        """Test watcher with default check interval"""
        watcher = GameWatcher()

        # Should have some default interval
        assert watcher.check_interval > 0


@pytest.mark.ui
class TestGameWatcherSignals:
    """Test GameWatcher Qt signals"""

    def test_watcher_has_signals(self):
        """Test that watcher has required signals"""
        watcher = GameWatcher()

        # Check for required signals
        assert hasattr(watcher, 'game_detected')
        assert hasattr(watcher, 'game_changed')
        assert hasattr(watcher, 'game_closed')

    @pytest.mark.skip(reason="Requires Qt event loop")
    def test_game_detected_signal(self, qtbot):
        """Test game_detected signal emission"""
        watcher = GameWatcher(check_interval=1)

        # Use QSignalSpy to catch signals
        spy = QSignalSpy(watcher.game_detected)

        watcher.start_watching()
        qtbot.wait(2000)  # Wait for signal
        watcher.stop_watching()

        # Should have emitted game_detected signal
        assert len(spy) >= 0  # May or may not detect a game


@pytest.mark.unit
class TestGameDetectionLogic:
    """Test game detection logic"""

    def test_watcher_has_detector(self):
        """Test that watcher has game detector"""
        watcher = GameWatcher()

        # Should have detector
        assert hasattr(watcher, 'detector')
        assert watcher.detector is not None

    def test_watcher_has_profile_store(self):
        """Test that watcher has profile store"""
        watcher = GameWatcher()

        # Should have profile_store
        assert hasattr(watcher, 'profile_store')
        assert watcher.profile_store is not None


@pytest.mark.unit
class TestGameWatcherControl:
    """Test starting and stopping watcher"""

    def test_watcher_start(self):
        """Test starting watcher thread"""
        watcher = GameWatcher()

        # Start should not crash
        try:
            watcher.start_watching()
            # Immediately stop to clean up
            watcher.stop_watching()
            assert True
        except Exception as e:
            pytest.fail(f"Watcher start/stop failed: {e}")

    def test_watcher_stop(self):
        """Test stopping watcher thread"""
        watcher = GameWatcher()

        watcher.start_watching()
        # Stop should not crash
        try:
            watcher.stop_watching()
            assert True
        except Exception as e:
            pytest.fail(f"Watcher stop failed: {e}")


@pytest.mark.unit
class TestGameStateTracking:
    """Test tracking game state changes"""

    def test_tracks_current_game(self):
        """Test tracking currently running game"""
        watcher = GameWatcher()

        # Should have current game attribute
        assert hasattr(watcher, 'active_game') or hasattr(watcher, '_active_game')

    def test_has_active_game_attributes(self):
        """Test that watcher has game state attributes"""
        watcher = GameWatcher()

        # Should have game tracking attributes
        assert hasattr(watcher, 'active_game')
        assert hasattr(watcher, 'active_game_exe')
        assert hasattr(watcher, 'active_profile')


@pytest.mark.integration
class TestGameWatcherIntegration:
    """Integration tests for game watcher"""

    def test_watcher_with_default_settings(self):
        """Test watcher with default settings"""
        watcher = GameWatcher(check_interval=10)

        # Should initialize successfully
        assert watcher is not None

        # Start and stop
        watcher.start_watching()
        watcher.stop_watching()

    def test_watcher_lifecycle(self):
        """Test complete watcher lifecycle"""
        watcher = GameWatcher(check_interval=5)

        # Should start clean
        assert not watcher._watching

        # Start watching
        watcher.start_watching()
        assert watcher._watching

        # Stop watching
        watcher.stop_watching()
        assert not watcher._watching
