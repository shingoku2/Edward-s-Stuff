"""
Game Detection Module
Detects running games on the system with performance optimizations
"""

import logging
import os
import threading
import time
from typing import Dict, List, Optional, Set, Tuple

import psutil  # type: ignore[import-untyped]

from omnix.type_definitions import GameInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameDetector:
    """Detects running games on Windows with performance optimizations"""

    # Cache settings
    _CACHE_DURATION = 2.0  # Cache results for 2 seconds
    _MAX_CACHE_SIZE = 100  # Maximum cached entries
    _BACKGROUND_SCAN_INTERVAL = 5.0  # Background scan every 5 seconds

    def __init__(self):
        """Initialize game detector with common game process names"""
        self.common_games = {
            "League of Legends": ["LeagueClientUx.exe", "League of Legends.exe"],
            "Valorant": ["VALORANT.exe", "valorant.exe"],
            "Counter-Strike 2": ["cs2.exe", "csgo.exe"],
            "Dota 2": ["dota2.exe"],
            "World of Warcraft": ["Wow.exe", "WowClassic.exe"],
            "Minecraft": ["Minecraft.exe", "MinecraftLauncher.exe"],
            "Fortnite": ["FortniteClient-Win64-Shipping.exe"],
            "PUBG": ["TslGame.exe"],
            "Elden Ring": ["eldenring.exe"],
            "Dark Souls III": ["DarkSoulsIII.exe"],
            "Baldur's Gate 3": ["bg3.exe"],
            "Cyberpunk 2077": ["Cyberpunk2077.exe"],
            "GTA V": ["GTA5.exe", "gtavicecity.exe"],
        }
        self._rebuild_process_index()

        # Performance optimizations
        self._scan_cache: Dict[str, Tuple[float, List[GameInfo]]] = {}
        self._last_cache_time = 0.0
        self._cache_lock = threading.RLock()
        self._running_processes_cache: Set[str] = set()
        self._last_process_scan = 0.0
        self._background_thread: Optional[threading.Thread] = None
        self._stop_background_scan = False

        # Start background scanning for better performance
        self._start_background_scan()

    @staticmethod
    def _normalize_game_key(game_name: Optional[str]) -> str:
        """Normalize game identifiers for duplicate checks."""
        if game_name is None:
            return ""
        return str(game_name).casefold()

    @staticmethod
    def _normalize_process_name(process_name: str) -> str:
        """Normalize process names for duplicate detection."""
        if not process_name:
            return ""
        return str(process_name).casefold()

    def _get_file_version_info(self, path: str) -> str:
        """Get file version information from executable (Windows only)."""
        if not path or not os.path.exists(path):
            return ""

        try:
            # Try using pywin32
            import win32api  # type: ignore[import-untyped]

            info = win32api.GetFileVersionInfo(path, "\\")
            ms = info["FileVersionMS"]
            ls = info["FileVersionLS"]
            return f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
        except (ImportError, Exception):
            return ""

    def _rebuild_process_index(self) -> None:
        """Build a fast lookup of tracked processes to prevent duplicates."""
        process_index: Dict[str, str] = {}
        for game_name, process_names in self.common_games.items():
            if not process_names:
                continue
            for process_name in process_names:
                normalized = self._normalize_process_name(process_name)
                if not normalized:
                    continue
                process_index.setdefault(normalized, game_name)
        self._process_index = process_index

    def detect_running_game(self) -> Optional[GameInfo]:
        """Detect if any known game is currently running."""
        try:
            running_games = self._optimized_scan_running_games()
            if running_games:
                detected_game = running_games[0]
                logger.info(
                    "Game detected: %s (pid=%s)",
                    detected_game["name"],
                    detected_game.get("pid"),
                )
                return detected_game
            return None

        except Exception as e:
            logger.error(f"Error detecting game: {e}", exc_info=True)
            return None

    def _is_process_running(self, process_name: str) -> bool:
        """
        Check if a process is currently running

        Args:
            process_name: Name of the process to check

        Returns:
            True if process is running, False otherwise
        """
        try:
            if not process_name:
                return False
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    name = proc.info.get("name")
                    if name and name.lower() == process_name.lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False

        except Exception as e:
            logger.error(f"Error checking process: {e}", exc_info=True)
            return False

    def _get_current_time(self) -> str:
        """Get current time as string"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_running_games(self) -> List[GameInfo]:
        """Get all running games from the common games list."""
        try:
            return self._optimized_scan_running_games()
        except Exception as e:
            logger.error(f"Error getting running games: {e}", exc_info=True)
            return []

    def _scan_running_games(self) -> List[GameInfo]:
        """Scan running processes and return matching games with metadata."""
        running_games: List[GameInfo] = []
        seen_games: Set[str] = set()

        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                process_name = proc.info.get("name") or ""
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

            normalized_name = self._normalize_process_name(process_name)
            if not normalized_name:
                continue

            game_name = self._process_index.get(normalized_name)
            if not game_name or game_name in seen_games:
                continue

            running_games.append(self._build_game_info(proc, game_name))
            seen_games.add(game_name)

        return running_games

    def _build_game_info(self, process: psutil.Process, game_name: str) -> GameInfo:
        """Build a structured game info object for a detected process."""
        try:
            proc_info: Dict[str, Optional[str]] = process.as_dict(attrs=["pid", "name", "exe"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_info = {"pid": process.pid, "name": process.name(), "exe": None}

        exe_path = proc_info.get("exe") or ""
        process_name = proc_info.get("name") or ""
        pid = int(proc_info.get("pid") or process.pid)

        version = ""
        if exe_path:
            version = self._get_file_version_info(exe_path)

        return {
            "name": game_name,
            "exe": exe_path,
            "process_name": process_name,
            "pid": pid,
            "path": os.path.dirname(exe_path) if exe_path else "",
            "version": version,
        }

    def _start_background_scan(self) -> None:
        """Start background scanning thread for better performance"""
        if self._background_thread is not None:
            return

        def background_scanner():
            """Background thread that periodically scans for game processes"""
            while not self._stop_background_scan:
                try:
                    self._update_process_cache()
                    time.sleep(self._BACKGROUND_SCAN_INTERVAL)
                except Exception as e:
                    logger.error(f"Background scan error: {e}", exc_info=True)
                    time.sleep(1)  # Brief pause on error

        self._background_thread = threading.Thread(
            target=background_scanner, daemon=True, name="GameDetector-BackgroundScan"
        )
        self._background_thread.start()
        logger.debug("Started background game detection scanning")

    def _update_process_cache(self) -> None:
        """Update the cached set of running processes"""
        try:
            current_time = time.time()

            # Only update if enough time has passed since last scan
            if current_time - self._last_process_scan < 1.0:  # 1 second minimum
                return

            new_processes = set()

            # Optimized process scanning - only get name and pid
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    proc_name = proc.info.get("name")
                    if proc_name:
                        new_processes.add(proc_name.lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            with self._cache_lock:
                self._running_processes_cache = new_processes
                self._last_process_scan = current_time

        except Exception as e:
            logger.error(f"Error updating process cache: {e}", exc_info=True)

    def _get_cached_result(self) -> Optional[List[GameInfo]]:
        """Get cached scan result if still valid"""
        current_time = time.time()

        with self._cache_lock:
            if self._scan_cache and current_time - self._last_cache_time < self._CACHE_DURATION:
                cache_key = self._get_cache_key()
                if cache_key in self._scan_cache:
                    cached_time, cached_result = self._scan_cache[cache_key]
                    if current_time - cached_time < self._CACHE_DURATION:
                        logger.debug("Using cached game detection result")
                        return cached_result

        return None

    def _cache_result(self, result: List[GameInfo]) -> None:
        """Cache the scan result"""
        current_time = time.time()

        with self._cache_lock:
            # Limit cache size
            if len(self._scan_cache) >= self._MAX_CACHE_SIZE:
                # Remove oldest entry
                oldest_key = min(self._scan_cache.keys(), key=lambda k: self._scan_cache[k][0])
                del self._scan_cache[oldest_key]

            cache_key = self._get_cache_key()
            self._scan_cache[cache_key] = (current_time, result)
            self._last_cache_time = current_time

    def _get_cache_key(self) -> str:
        """Generate cache key based on current game list and system state"""
        try:
            # Include game list hash and process count for cache invalidation
            # Use frozenset of keys since dict values (lists) aren't hashable
            games_hash = hash(frozenset(self.common_games.keys()))
            process_count = len(self._running_processes_cache)
            return f"{games_hash}:{process_count}"
        except Exception:
            # Fallback to simple key
            return "default"

    def _optimized_scan_running_games(self) -> List[GameInfo]:
        """Optimized version of _scan_running_games using cache"""
        # Check cache first
        cached_result = self._get_cached_result()
        if cached_result is not None:
            return cached_result

        # Update process cache if needed
        current_time = time.time()
        if current_time - self._last_process_scan > 2.0:  # 2 seconds
            self._update_process_cache()

        running_games: List[GameInfo] = []
        seen_games: Set[str] = set()

        # Use cached process list if available
        with self._cache_lock:
            current_processes = self._running_processes_cache.copy()

        # Fast lookup using cached processes
        for process_name in current_processes:
            game_name = self._process_index.get(process_name)
            if not game_name or game_name in seen_games:
                continue

            seen_games.add(game_name)

            # Get detailed process info only when we have a match
            try:
                for proc in psutil.process_iter(["pid", "name", "exe"]):
                    try:
                        proc_name = proc.info.get("name")
                        if proc_name and proc_name.lower() == process_name:
                            running_games.append(self._build_game_info(proc, game_name))
                            break  # Found the process, no need to continue
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                logger.error(f"Error getting process info for {game_name}: {e}", exc_info=True)
                continue

        # Cache the result
        self._cache_result(running_games)
        return running_games

    def stop_background_scan(self) -> None:
        """Stop the background scanning thread"""
        self._stop_background_scan = True
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=2.0)
        logger.debug("Stopped background game detection scanning")

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_background_scan()

    def add_custom_game(self, game_name: str, process_names: Optional[List[str]] = None) -> bool:
        """
        Add a custom game to the detection list

        Args:
            game_name: Name of the game
            process_names: List of process names to detect

        Returns:
            True if added successfully
        """
        try:
            normalized_new_name = self._normalize_game_key(game_name)
            existing_names = {
                self._normalize_game_key(existing_name)
                for existing_name in self.common_games.keys()
            }

            if normalized_new_name in existing_names:
                logger.warning(f"Game {game_name} already exists")
                return False

            process_names = list(process_names or [])
            unique_processes = []
            seen_processes = set()
            duplicate_incoming = False

            for process_name in process_names:
                normalized_process = self._normalize_process_name(process_name)
                if not normalized_process:
                    continue
                if normalized_process in seen_processes:
                    duplicate_incoming = True
                    continue
                seen_processes.add(normalized_process)
                if hasattr(self, "_process_index") and normalized_process in self._process_index:
                    duplicate_incoming = True
                    continue
                unique_processes.append(process_name)

            if not unique_processes and process_names:
                logger.warning(
                    "No unique process names provided; duplicate tracking prevented for %s",
                    game_name,
                )
                return False

            self.common_games[game_name] = unique_processes
            self._rebuild_process_index()
            if duplicate_incoming:
                logger.info(
                    "Added custom game %s with filtered process list to avoid duplicates",
                    game_name,
                )
            else:
                logger.info(f"Added custom game: {game_name}")
            return True

        except Exception as e:
            logger.error(f"Error adding custom game: {e}", exc_info=True)
            return False


if __name__ == "__main__":
    detector = GameDetector()
    game = detector.detect_running_game()

    if game:
        print(f"Game detected: {game['name']}")
    else:
        print("No game detected")
