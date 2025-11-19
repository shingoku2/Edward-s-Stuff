"""
Game Watcher Module
Monitors active game and emits Qt signals when game changes
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict
from PyQt6.QtCore import QObject, pyqtSignal

from game_detector import GameDetector
from game_profile import GameProfile, get_profile_store

logger = logging.getLogger(__name__)


class GameWatcher(QObject):
    """
    Monitors the active game and emits signals when it changes.

    Signals:
        game_changed: Emitted when active game changes (game_name, profile)
        game_detected: Emitted when any game is detected
        game_closed: Emitted when the active game closes
    """

    # Signals
    game_changed = pyqtSignal(str, object)  # game_name, profile
    game_detected = pyqtSignal(str)  # game_name
    game_closed = pyqtSignal()  # No args

    def __init__(self, check_interval: int = 5):
        """
        Initialize game watcher.

        Args:
            check_interval: How often to check for active game (seconds)
        """
        super().__init__()
        self.detector = GameDetector()
        self.profile_store = get_profile_store()
        self.check_interval = check_interval
        self.active_game: Optional[str] = None
        self.active_game_exe: Optional[str] = None
        self.active_profile: Optional[GameProfile] = None
        self._watching = False
        self._watcher_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.last_known_pid: Optional[int] = None  # Cache PID for non-Windows optimization

    def start_watching(self) -> None:
        """Start monitoring for active game changes"""
        if self._watching:
            logger.warning("Game watcher already running")
            return

        self._watching = True
        self._stop_event.clear()
        self._watcher_thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name="GameWatcherThread"
        )
        self._watcher_thread.start()
        logger.info("Game watcher started")

    def stop_watching(self) -> None:
        """Stop monitoring for game changes"""
        if not self._watching:
            return

        self._watching = False
        self._stop_event.set()

        if self._watcher_thread and self._watcher_thread.is_alive():
            self._watcher_thread.join(timeout=2)

        logger.info("Game watcher stopped")

    def _watch_loop(self) -> None:
        """Main watch loop running in background thread"""
        logger.debug(f"Watch loop started with {self.check_interval}s interval")

        while self._watching and not self._stop_event.is_set():
            try:
                # Get current foreground window process (Windows-specific)
                current_exe = self._get_foreground_executable()

                if current_exe:
                    self._handle_game_active(current_exe)
                else:
                    self._handle_no_game()

            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)

            # Sleep with interruptible waits
            time.sleep(self.check_interval)

        logger.debug("Watch loop ended")

    def _get_foreground_executable(self) -> Optional[str]:
        """
        Get the executable name of the foreground window.

        On Windows: Returns the foreground window's process name.
        On Linux/macOS: Returns any running game process (fallback, not necessarily foreground).

        Returns:
            Executable filename (e.g., "eldenring.exe") or None if no game window
        """
        try:
            import psutil
            import platform

            system = platform.system()

            if system != "Windows":
                # Fallback for Linux/macOS:
                # Just check if any known game process is running (not necessarily foreground)
                # This is "good enough" for single-screen setups.
                logger.debug("Using fallback game detection for non-Windows platform")

                # Optimization: Check if previously detected game is still running
                if self.last_known_pid:
                    try:
                        proc = psutil.Process(self.last_known_pid)
                        if proc.is_running():
                            return proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process died or access denied - clear cache
                        self.last_known_pid = None

                # Fallback: Full scan of all running processes
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        exe_name = proc.info['name']
                        # Check if this process matches any known game
                        profile = self.profile_store.get_profile_by_executable(exe_name)
                        if profile and profile.id != "generic_game":
                            logger.debug(f"Found running game: {exe_name}")
                            # Cache PID for next check
                            self.last_known_pid = proc.info['pid']
                            return exe_name
                    except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                        continue

                return None

            # Windows-specific foreground window detection
            try:
                # Try using ctypes to get foreground window process
                import ctypes
                from ctypes import wintypes

                GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
                GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

                hwnd = GetForegroundWindow()
                if not hwnd:
                    return None

                pid = wintypes.DWORD()
                GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

                if pid.value == 0:
                    return None

                try:
                    proc = psutil.Process(pid.value)
                    # Process might terminate between creation and name() call
                    try:
                        return proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process terminated or access denied
                        return None
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return None

            except Exception as e:
                logger.debug(f"Could not get foreground window: {e}")
                return None

        except Exception as e:
            logger.error(f"Error getting foreground executable: {e}")
            return None

    def _handle_game_active(self, exe_name: str) -> None:
        """
        Handle when a game executable is in foreground.

        Args:
            exe_name: Name of the executable in foreground
        """
        # Check if this is a game we recognize
        profile = self.profile_store.get_profile_by_executable(exe_name)

        # Get the game name from the profile
        game_name = profile.display_name

        # Check if game changed
        if exe_name.lower() != (self.active_game_exe or "").lower():
            logger.info(f"Game changed: {game_name} ({exe_name})")
            self.active_game = game_name
            self.active_game_exe = exe_name
            self.active_profile = profile

            # Emit signals
            self.game_changed.emit(game_name, profile)
            if profile.id != "generic_game":
                self.game_detected.emit(game_name)

    def _handle_no_game(self) -> None:
        """Handle when no game is in foreground (desktop)"""
        if self.active_game is not None:
            logger.info("Game closed or minimized")
            self.active_game = None
            self.active_game_exe = None
            self.active_profile = None
            self.last_known_pid = None  # Clear cached PID
            self.game_closed.emit()

    def get_active_game(self) -> Optional[str]:
        """Get the currently active game name or None"""
        return self.active_game

    def get_active_profile(self) -> Optional[GameProfile]:
        """Get the GameProfile for the currently active game"""
        if self.active_profile is None and self.active_game_exe:
            # Lazy load profile if not already set
            self.active_profile = self.profile_store.get_profile_by_executable(
                self.active_game_exe
            )
        return self.active_profile

    def register_game_changed_callback(self, callback: Callable[[str, GameProfile], None]) -> None:
        """
        Register a callback for game changes (alternative to signals).

        Args:
            callback: Function called with (game_name, profile) when game changes
        """
        self.game_changed.connect(
            lambda game_name, profile: callback(game_name, profile)
        )


# Global game watcher instance
_game_watcher: Optional[GameWatcher] = None


def get_game_watcher(check_interval: int = 5) -> GameWatcher:
    """Get or create the global game watcher instance"""
    global _game_watcher
    if _game_watcher is None:
        _game_watcher = GameWatcher(check_interval=check_interval)
    return _game_watcher
