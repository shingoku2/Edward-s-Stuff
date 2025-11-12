"""
Game Detection Module
Detects running games on the system
"""

import os
import logging
from typing import Optional, Dict
import subprocess
import psutil

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
        "javaw.exe": "Minecraft",
        "Minecraft.exe": "Minecraft",
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
            "Minecraft": ["javaw.exe", "Minecraft.exe"],
            "Fortnite": ["FortniteClient-Win64-Shipping.exe"],
            "PUBG": ["TslGame.exe"],
            "Elden Ring": ["eldenring.exe"],
            "Dark Souls III": ["DarkSoulsIII.exe"],
            "Baldur's Gate 3": ["bg3.exe"],
            "Cyberpunk 2077": ["Cyberpunk2077.exe"],
            "GTA V": ["GTA5.exe", "gtavicecity.exe"],
        }
        self._refresh_legacy_mappings()

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

    def detect_running_game(self) -> Optional[Dict[str, str]]:
        """
        Detect if any known game is currently running

        Returns:
            Dictionary with game info if found, None otherwise
        """
        try:
            for game_name, process_names in self.common_games.items():
                for process_name in process_names:
                    if self._is_process_running(process_name):
                        logger.info(f"Game detected: {game_name}")
                        return {
                            "name": game_name,
                            "process": process_name,
                            "detected_at": str(self._get_current_time())
                        }
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

    def get_running_games(self) -> list:
        """
        Get all running games from the common games list

        Returns:
            List of running games
        """
        running_games = []
        try:
            for game_name, process_names in self.common_games.items():
                for process_name in process_names:
                    if self._is_process_running(process_name):
                        running_games.append({
                            "name": game_name,
                            "process": process_name
                        })
                        break
            return running_games

        except Exception as e:
            logger.error(f"Error getting running games: {e}", exc_info=True)
            return []

    def add_custom_game(self, game_name: str, process_names: list) -> bool:
        """
        Add a custom game to the detection list

        Args:
            game_name: Name of the game
            process_names: List of process names to detect

        Returns:
            True if added successfully
        """
        try:
            if game_name not in self.common_games:
                self.common_games[game_name] = process_names
                self._refresh_legacy_mappings()
                logger.info(f"Added custom game: {game_name}")
                return True
            else:
                logger.warning(f"Game {game_name} already exists")
                return False

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
