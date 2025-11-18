"""
Game Detection Module
Detects running games on the system
"""

import logging
from typing import Optional, Dict
import psutil

from src.types import GameInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameDetector:
    """Detects running games on Windows"""

    #: Legacy mapping of process -> friendly game name used by older test harnesses
    #: and documentation. Populated at instantiation time to maintain backwards
    #: compatibility with scripts that expect ``GameDetector.KNOWN_GAMES`` to
    #: exist.
    DEFAULT_KNOWN_GAMES = {
        "LeagueClientUx.exe": "League of Legends",
        "League of Legends.exe": "League of Legends",
        "VALORANT.exe": "Valorant",
        "valorant.exe": "Valorant",
        "cs2.exe": "Counter-Strike 2",
        "csgo.exe": "Counter-Strike 2",
        "dota2.exe": "Dota 2",
        "Wow.exe": "World of Warcraft",
        "WowClassic.exe": "World of Warcraft",
        "Minecraft.exe": "Minecraft",
        "MinecraftLauncher.exe": "Minecraft",
        "FortniteClient-Win64-Shipping.exe": "Fortnite",
        "TslGame.exe": "PUBG",
        "eldenring.exe": "Elden Ring",
        "DarkSoulsIII.exe": "Dark Souls III",
        "bg3.exe": "Baldur's Gate 3",
        "Cyberpunk2077.exe": "Cyberpunk 2077",
        "GTA5.exe": "GTA V",
        "gtavicecity.exe": "GTA V",
    }

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
        self._refresh_legacy_mappings()

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

    def _refresh_legacy_mappings(self) -> None:
        """Synchronize legacy mapping attributes used by historic tooling."""
        known_games = dict(self.DEFAULT_KNOWN_GAMES)
        for game_name, process_names in self.common_games.items():
            for process_name in process_names:
                known_games.setdefault(process_name, game_name)
        self.KNOWN_GAMES = known_games
        # ``KNOWN_PROCESSES`` is kept as an alias for scripts introduced during the
        # refactor where this attribute name briefly replaced ``KNOWN_GAMES``.
        self.KNOWN_PROCESSES = self.KNOWN_GAMES
        self._rebuild_process_index()

    def _rebuild_process_index(self) -> None:
        """Build a fast lookup of tracked processes to prevent duplicates."""
        process_index = {}
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
            running_games = self._scan_running_games()
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
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info.get('name')
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
            return self._scan_running_games()
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
            proc_info: Dict[str, Optional[str]] = process.as_dict(
                attrs=["pid", "name", "exe"]
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_info = {"pid": process.pid, "name": process.name(), "exe": None}

        exe_path = proc_info.get("exe") or ""
        process_name = proc_info.get("name") or ""
        pid = int(proc_info.get("pid") or process.pid)

        return {
            "name": game_name,
            "exe": exe_path,
            "process_name": process_name,
            "pid": pid,
            "path": os.path.dirname(exe_path) if exe_path else "",
        }

    def add_custom_game(
        self, game_name: Optional[str], process_names: Optional[List[str]]
    ) -> bool:
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
            self._refresh_legacy_mappings()
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
