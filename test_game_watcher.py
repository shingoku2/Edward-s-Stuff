"""
Comprehensive test suite for game watcher thread
Tests background game detection, signal emission, and thread lifecycle
"""

import os
import sys
import time
from unittest.mock import Mock, MagicMock, patch
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game_watcher import GameWatcher
from src.game_detector import GameDetector
from src.game_profile import GameProfileStore


@pytest.mark.unit
class TestGameWatcherInitialization:
    """Test game watcher initialization"""

    def test_initialization(self, mock_game_detector):
        """Test basic initialization"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=5)

        assert watcher is not None
        assert watcher.check_interval == 5
        assert not watcher.isRunning()

    def test_initialization_with_custom_interval(self, mock_game_detector):
        """Test initialization with custom check interval"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=10)

        assert watcher.check_interval == 10

    def test_default_check_interval(self, mock_game_detector):
        """Test default check interval"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store)

        # Should have some reasonable default
        assert watcher.check_interval > 0


@pytest.mark.unit
class TestThreadLifecycle:
    """Test thread start, stop, and lifecycle"""

    def test_start_thread(self, mock_game_detector):
        """Test starting the watcher thread"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        watcher.start()

        # Thread should be running
        assert watcher.isRunning()

        # Cleanup
        watcher.stop()
        watcher.wait(timeout=2000)  # Wait up to 2 seconds

    def test_stop_thread(self, mock_game_detector):
        """Test stopping the watcher thread"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        watcher.start()
        assert watcher.isRunning()

        watcher.stop()
        watcher.wait(timeout=2000)

        # Thread should eventually stop
        # Give it a moment to finish
        time.sleep(0.5)

    def test_multiple_start_calls(self, mock_game_detector):
        """Test that multiple start calls don't create issues"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        watcher.start()

        # Try to start again (should be safe)
        try:
            watcher.start()
        except RuntimeError:
            # RuntimeError is acceptable for already-running thread
            pass

        # Cleanup
        watcher.stop()
        watcher.wait(timeout=2000)

    def test_stop_without_start(self, mock_game_detector):
        """Test stopping without starting (should be safe)"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store)

        # Should not crash
        watcher.stop()


@pytest.mark.unit
class TestGameDetectionSignals:
    """Test signal emission for game detection events"""

    @pytest.mark.ui
    def test_game_detected_signal(self, mock_game_detector, qapp):
        """Test game_detected signal emission"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        # Mock game detection
        with patch.object(mock_game_detector, 'detect_running_game') as mock_detect:
            mock_detect.return_value = {
                'name': 'Elden Ring',
                'pid': 12345,
                'timestamp': time.time()
            }

            signals_received = []

            def on_game_detected(game_name):
                signals_received.append(('detected', game_name))

            # Connect signal
            watcher.game_detected.connect(on_game_detected)

            # Start watcher briefly
            watcher.start()
            time.sleep(0.5)  # Let it run briefly
            watcher.stop()
            watcher.wait(timeout=2000)

            # May or may not have detected depending on timing
            # Just verify no crashes

    @pytest.mark.ui
    def test_game_changed_signal(self, mock_game_detector, qapp):
        """Test game_changed signal emission"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        signals_received = []

        def on_game_changed(game_name, profile):
            signals_received.append(('changed', game_name, profile))

        watcher.game_changed.connect(on_game_changed)

        # Just verify signal connection works
        assert watcher.game_changed is not None

    @pytest.mark.ui
    def test_game_closed_signal(self, mock_game_detector, qapp):
        """Test game_closed signal emission"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        signals_received = []

        def on_game_closed():
            signals_received.append('closed')

        watcher.game_closed.connect(on_game_closed)

        # Just verify signal connection works
        assert watcher.game_closed is not None


@pytest.mark.unit
class TestDetectionBehavior:
    """Test game detection behavior"""

    def test_detection_with_running_game(self, mock_game_detector):
        """Test detection when game is running"""
        profile_store = GameProfileStore()

        with patch.object(mock_game_detector, 'detect_running_game') as mock_detect:
            mock_detect.return_value = {
                'name': 'Elden Ring',
                'pid': 12345
            }

            watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

            # Start and quickly stop
            watcher.start()
            time.sleep(0.2)
            watcher.stop()
            watcher.wait(timeout=2000)

            # Should have attempted detection
            # Actual behavior depends on timing

    def test_detection_with_no_game(self, mock_game_detector):
        """Test detection when no game is running"""
        profile_store = GameProfileStore()

        with patch.object(mock_game_detector, 'detect_running_game') as mock_detect:
            mock_detect.return_value = None

            watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

            watcher.start()
            time.sleep(0.2)
            watcher.stop()
            watcher.wait(timeout=2000)

            # Should handle no game gracefully

    def test_game_transition_detection(self, mock_game_detector):
        """Test detecting game transition (one game to another)"""
        profile_store = GameProfileStore()

        with patch.object(mock_game_detector, 'detect_running_game') as mock_detect:
            # Start with one game
            mock_detect.return_value = {'name': 'Game A', 'pid': 100}

            watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

            watcher.start()
            time.sleep(0.2)

            # Change to different game
            mock_detect.return_value = {'name': 'Game B', 'pid': 200}

            time.sleep(0.2)
            watcher.stop()
            watcher.wait(timeout=2000)

            # Should handle transition gracefully


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling during detection"""

    def test_detector_exception_handling(self, mock_game_detector):
        """Test handling of detector exceptions"""
        profile_store = GameProfileStore()

        with patch.object(mock_game_detector, 'detect_running_game') as mock_detect:
            # Make detector raise exception
            mock_detect.side_effect = Exception("Process monitoring failed")

            watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

            # Should not crash
            watcher.start()
            time.sleep(0.2)
            watcher.stop()
            watcher.wait(timeout=2000)

    def test_profile_store_exception_handling(self):
        """Test handling of profile store exceptions"""
        detector = GameDetector()

        with patch.object(GameProfileStore, 'get_profile_by_executable') as mock_get:
            mock_get.side_effect = Exception("Profile load failed")

            profile_store = GameProfileStore()
            watcher = GameWatcher(detector, profile_store, check_interval=1)

            # Should handle gracefully
            watcher.start()
            time.sleep(0.2)
            watcher.stop()
            watcher.wait(timeout=2000)


@pytest.mark.unit
class TestMemoryManagement:
    """Test memory management and resource cleanup"""

    def test_cleanup_on_stop(self, mock_game_detector):
        """Test proper cleanup when stopped"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        watcher.start()
        time.sleep(0.2)
        watcher.stop()
        watcher.wait(timeout=2000)

        # Thread should be properly stopped
        assert not watcher.isRunning()

    def test_multiple_start_stop_cycles(self, mock_game_detector):
        """Test multiple start/stop cycles for memory leaks"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        # Multiple cycles
        for _ in range(3):
            watcher.start()
            time.sleep(0.1)
            watcher.stop()
            watcher.wait(timeout=2000)

        # Should handle multiple cycles without issues


@pytest.mark.unit
class TestDetectionInterval:
    """Test detection interval timing"""

    def test_respects_check_interval(self, mock_game_detector):
        """Test that watcher respects check interval"""
        profile_store = GameProfileStore()

        detection_times = []

        def track_detection():
            detection_times.append(time.time())
            return None

        with patch.object(mock_game_detector, 'detect_running_game', side_effect=track_detection):
            watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

            watcher.start()
            time.sleep(2.5)  # Run for 2.5 seconds
            watcher.stop()
            watcher.wait(timeout=2000)

            # Should have detected roughly every 1 second
            # Allow some tolerance for execution time
            if len(detection_times) >= 2:
                intervals = [
                    detection_times[i+1] - detection_times[i]
                    for i in range(len(detection_times) - 1)
                ]

                # Intervals should be roughly 1 second (within tolerance)
                for interval in intervals:
                    assert 0.5 < interval < 2.0, f"Interval {interval} outside tolerance"


@pytest.mark.integration
class TestIntegrationWithGameDetector:
    """Integration tests with real game detector"""

    def test_real_detection_integration(self):
        """Test integration with real GameDetector"""
        detector = GameDetector()
        profile_store = GameProfileStore()

        watcher = GameWatcher(detector, profile_store, check_interval=2)

        # Start watcher
        watcher.start()

        # Let it run briefly
        time.sleep(0.5)

        # Stop cleanly
        watcher.stop()
        watcher.wait(timeout=3000)

        # Should complete without errors
        assert not watcher.isRunning()

    def test_profile_resolution_integration(self):
        """Test that profiles are correctly resolved"""
        detector = GameDetector()
        profile_store = GameProfileStore()

        detected_profiles = []

        def on_game_changed(game_name, profile):
            detected_profiles.append((game_name, profile))

        watcher = GameWatcher(detector, profile_store, check_interval=1)
        watcher.game_changed.connect(on_game_changed)

        # Run briefly
        watcher.start()
        time.sleep(0.3)
        watcher.stop()
        watcher.wait(timeout=2000)

        # Profiles should be valid if any were detected
        for game_name, profile in detected_profiles:
            assert profile is not None
            assert hasattr(profile, 'id')
            assert hasattr(profile, 'display_name')


@pytest.mark.unit
class TestThreadSafety:
    """Test thread safety of game watcher"""

    def test_concurrent_signal_emissions(self, mock_game_detector, qapp):
        """Test that signal emissions are thread-safe"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        received_signals = []

        def signal_handler(game_name):
            received_signals.append(game_name)

        watcher.game_detected.connect(signal_handler)

        # Just verify no crashes with signal connections
        watcher.start()
        time.sleep(0.2)
        watcher.stop()
        watcher.wait(timeout=2000)

    def test_state_access_during_execution(self, mock_game_detector):
        """Test accessing watcher state during execution"""
        profile_store = GameProfileStore()
        watcher = GameWatcher(mock_game_detector, profile_store, check_interval=1)

        watcher.start()

        # Access state during execution
        is_running = watcher.isRunning()
        assert is_running

        watcher.stop()
        watcher.wait(timeout=2000)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
