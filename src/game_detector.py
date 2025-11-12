"""
Game Detector Module
Detects currently running games and identifies them
"""

import psutil
import re
import json
import os
import logging
from typing import Optional, Dict, List
from pathlib import Path, PureWindowsPath

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameDetector:
    """Detects and identifies currently running games"""

    # Common game executables and platforms
    KNOWN_GAMES = {
        # Popular Games
        "league of legends.exe": "League of Legends",
        "valorant.exe": "VALORANT",
        "valorant-win64-shipping.exe": "VALORANT",
        "overwatch.exe": "Overwatch",
        "dota2.exe": "Dota 2",
        "csgo.exe": "Counter-Strike: Global Offensive",
        "cs2.exe": "Counter-Strike 2",
        "fortnite.exe": "Fortnite",
        "fortnitelauncher.exe": "Fortnite",
        "rocketleague.exe": "Rocket League",
        "apexlegends.exe": "Apex Legends",
        "r5apex.exe": "Apex Legends",

        # RPG/Adventure
        "eldenring.exe": "Elden Ring",
        "darksouls3.exe": "Dark Souls 3",
        "witcher3.exe": "The Witcher 3",
        "skyrimse.exe": "Skyrim Special Edition",
        "fallout4.exe": "Fallout 4",
        "cyberpunk2077.exe": "Cyberpunk 2077",

        # Strategy
        "civilization6.exe": "Civilization VI",
        "ck3.exe": "Crusader Kings 3",
        "stellaris.exe": "Stellaris",
        "totalwar.exe": "Total War",

        # MMO
        "wow.exe": "World of Warcraft",
        "ffxiv_dx11.exe": "Final Fantasy XIV",
        "gw2-64.exe": "Guild Wars 2",
        "elderscrollsonline.exe": "Elder Scrolls Online",

        # Minecraft
        "minecraft.exe": "Minecraft",
        "minecraftlauncher.exe": "Minecraft",

        # Battle Royale
        "pubg.exe": "PUBG",
        "cod.exe": "Call of Duty",
        "warzone.exe": "Call of Duty: Warzone",

        # Others
        "gta5.exe": "Grand Theft Auto V",
        "rdr2.exe": "Red Dead Redemption 2",
        "destiny2.exe": "Destiny 2",
        "halo.exe": "Halo",
        "palworld-win64-shipping.exe": "Palworld",
        "helldivers2.exe": "Helldivers 2",
    }

    # Game launchers to ignore
    LAUNCHERS = {
        "steam.exe", "epicgameslauncher.exe", "origin.exe",
        "uplay.exe", "battlenet.exe", "riotclientservices.exe",
        "launcher.exe", "launchpad.exe"
    }

    def __init__(self, cache_file: str = "game_cache.json"):
        self.cache_file = cache_file
        self.current_game = None
        self.game_info_cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load game information cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in cache file: {e}")
                return {}
            except Exception as e:
                logger.error(f"Error loading cache: {e}", exc_info=True)
                return {}
        return {}

    def _save_cache(self):
        """Save game information cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.game_info_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}", exc_info=True)

    def detect_running_game(self) -> Optional[Dict[str, str]]:
        """
        Detect currently running game
        Returns: Dictionary with game info or None
        """
        running_processes = []

        try:
            for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()

                    # Skip launchers
                    if proc_name in self.LAUNCHERS:
                        continue

                    # Check if it's a known game
                    if proc_name in self.KNOWN_GAMES:
                        game_name = self.KNOWN_GAMES[proc_name]
                        self.current_game = {
                            'name': game_name,
                            'process': proc_name,
                            'exe': proc.info.get('exe', ''),
                        }
                        return self.current_game

                    # Check for potential games (executables with common game patterns)
                    if proc_name.endswith('.exe') and self._looks_like_game(proc):
                        running_processes.append(proc)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # If no known game found, try to identify from running processes
            if running_processes:
                game = self._identify_unknown_game(running_processes[0])
                if game:
                    self.current_game = game
                    return game

        except psutil.Error as e:
            logger.error(f"PSUtil error detecting game: {e}")
        except Exception as e:
            logger.error(f"Error detecting game: {e}", exc_info=True)

        return None

    def _looks_like_game(self, proc) -> bool:
        """Heuristic to identify if a process might be a game"""
        try:
            proc_name = proc.info['name'].lower()

            # Skip system processes and common non-game applications
            skip_keywords = [
                'windows', 'microsoft', 'system32', 'svchost', 'explorer',
                'chrome', 'firefox', 'edge', 'discord', 'spotify', 'slack',
                'code', 'visual', 'pycharm', 'intellij', 'eclipse', 'javaw', 'java',
                # Security and system tools
                'antivirus', 'eset', 'kaspersky', 'norton', 'mcafee', 'avast', 'avg',
                'defender', 'security', 'firewall', 'malware',
                # Common utilities and drivers
                'nvidia', 'nvcontainer', 'nvdisplay', 'nvcpl', 'nvprofileupdater',
                'amd', 'radeon', 'intel', 'driver', 'update', 'service',
                'adobe', 'office', 'outlook', 'teams', 'zoom', 'skype',
                # System containers and helpers
                'container', 'helper', 'updater', 'background'
            ]
            if any(x in proc_name for x in skip_keywords):
                return False

            # Check for game-related keywords in process name
            game_keywords = [
                'game', 'play',
                'win64-shipping', 'win32-shipping'  # More specific than just win64/win32
            ]

            if any(keyword in proc_name for keyword in game_keywords):
                return True

            # Check if in specific game directories (more specific paths)
            if proc.info.get('exe'):
                exe_path = proc.info['exe'].lower()
                game_paths = [
                    'steam\\steamapps',  # Steam games
                    'epic games\\',      # Epic Games
                    'riot games\\',      # Riot Games
                    '\\games\\',         # Generic games folder
                    'gog galaxy\\games'  # GOG Galaxy
                ]
                if any(path in exe_path for path in game_paths):
                    return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        except Exception as e:
            logger.debug(f"Error checking if process looks like game: {e}")

        return False

    def _identify_unknown_game(self, proc) -> Optional[Dict[str, str]]:
        """Try to identify an unknown game"""
        try:
            proc_name = proc.info['name']
            exe_path = proc.info.get('exe', '')

            # Extract potential game name from path or process name
            game_name = None

            if exe_path:
                # Use PureWindowsPath to handle Windows paths correctly
                # (works on any OS)
                path = PureWindowsPath(exe_path)

                # Check the full path for system folders
                path_lower = str(path).lower()

                # First, check if it's in a known game directory
                # These paths are allowed even if in Program Files
                game_directories = [
                    '\\steam\\steamapps\\',
                    '\\steamapps\\',
                    '\\epic games\\',
                    '\\riot games\\',
                    '\\games\\',
                    '\\gog galaxy\\games\\',
                ]

                is_in_game_directory = any(gdir in path_lower for gdir in game_directories)

                # Only filter out system folders if it's NOT in a game directory
                if not is_in_game_directory:
                    # Filter out system and common folders
                    system_folders = [
                        '\\system32\\', '\\syswow64\\', '\\windows\\',
                        '\\program files\\', '\\program files (x86)\\',
                        '\\programdata\\', '\\common files\\',
                        '\\microsoft\\', '\\windowsapps\\', '\\temp\\',
                        '\\appdata\\', 'c:\\windows\\'
                    ]

                    if any(folder in path_lower for folder in system_folders):
                        # This is likely a system process, not a game
                        return None

                # Get parent folder name for game name extraction
                parent_folder = path.parent.name

                # Clean up the name
                game_name = self._clean_game_name(parent_folder)

            if not game_name:
                game_name = self._clean_game_name(proc_name.replace('.exe', ''))

            return {
                'name': game_name,
                'process': proc_name,
                'exe': exe_path,
                'unknown': True
            }

        except Exception as e:
            logger.error(f"Error identifying unknown game: {e}", exc_info=True)
            return None

    def _clean_game_name(self, name: str) -> str:
        """Clean up game name for display"""
        # Remove common suffixes
        name = re.sub(r'(-win64|-win32|-shipping|\.exe)$', '', name, flags=re.IGNORECASE)

        # Replace separators with spaces
        name = re.sub(r'[_-]', ' ', name)

        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())

        return name

    def get_current_game(self) -> Optional[Dict[str, str]]:
        """Get currently detected game"""
        return self.current_game

    def add_known_game(self, process_name: str, game_name: str):
        """Add a game to the known games list"""
        self.KNOWN_GAMES[process_name.lower()] = game_name
        self._save_cache()


if __name__ == "__main__":
    # Test the game detector
    detector = GameDetector()
    print("Scanning for running games...")

    game = detector.detect_running_game()
    if game:
        print(f"\nDetected game: {game['name']}")
        print(f"Process: {game['process']}")
    else:
        print("\nNo game detected")
