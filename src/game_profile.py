"""
Game Profile Module
Manages per-game AI assistant configurations
"""

import json
import logging
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Configuration directory for game profiles
CONFIG_DIR = Path.home() / '.gaming_ai_assistant'
PROFILES_FILE = CONFIG_DIR / 'game_profiles.json'


@dataclass
class GameProfile:
    """
    Represents a game-specific AI profile.

    Attributes:
        id: Unique identifier (slug, e.g., "elden_ring")
        display_name: Human-readable name (e.g., "Elden Ring")
        exe_names: List of executable names to match (e.g., ["eldenring.exe"])
        system_prompt: AI behavior customization for this game
        default_provider: Preferred AI provider (openai, anthropic, gemini)
        default_model: Optional model override (e.g., "gpt-4", "claude-3-opus")
        overlay_mode_default: Default overlay mode (compact or full)
        extra_settings: Future extensibility dictionary
        is_builtin: Whether this is a built-in template profile
    """
    id: str
    display_name: str
    exe_names: List[str]
    system_prompt: str
    default_provider: str = "anthropic"
    default_model: Optional[str] = None
    overlay_mode_default: str = "compact"
    extra_settings: Dict = field(default_factory=dict)
    is_builtin: bool = False

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "GameProfile":
        """Create profile from dictionary"""
        return cls(**data)

    def matches_executable(self, exe_name: str) -> bool:
        """
        Check if this profile matches the given executable name.

        Args:
            exe_name: Executable filename (case-insensitive)

        Returns:
            True if exe_name matches any in exe_names list
        """
        exe_lower = exe_name.lower()
        return any(exe.lower() == exe_lower for exe in self.exe_names)


class GameProfileStore:
    """
    Manages game profile persistence and lookup.

    Features:
    - Load/save profiles from JSON file
    - CRUD operations
    - Lookup by executable name
    - Built-in default profiles
    """

    # Built-in default profiles that ship with the app
    BUILTIN_PROFILES = [
        GameProfile(
            id="generic_game",
            display_name="Generic Game",
            exe_names=[],  # Matches anything not in other profiles
            system_prompt=(
                "You are a helpful gaming AI assistant. Provide strategic tips, "
                "gameplay advice, and answers about the game. Keep responses concise "
                "and actionable. Focus on being useful in-game."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="mmorpg_generic",
            display_name="MMORPG (Generic)",
            exe_names=[],
            system_prompt=(
                "You are an expert MMORPG gaming assistant. Help with: build optimization, "
                "questlines, dungeon strategies, PvP tactics, and game mechanics. "
                "Provide build recommendations and dungeon guides. Keep advice concise."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="elden_ring",
            display_name="Elden Ring",
            exe_names=["eldenring.exe"],
            system_prompt=(
                "You are an expert Elden Ring guide. Help with: boss strategies, "
                "build optimization, questlines, item locations, PvP tactics, and map guidance. "
                "Provide concise, actionable tips for tough fights. Mention alternative strategies."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="baldurs_gate_3",
            display_name="Baldur's Gate 3",
            exe_names=["bg3.exe", "bg3_dx11.exe"],
            system_prompt=(
                "You are a Baldur's Gate 3 expert. Help with: build crafting, "
                "companion quests, dialogue choices, combat tactics, spell usage, and exploration. "
                "Consider roleplay implications and provide spoiler-free guidance where possible."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="cyberpunk_2077",
            display_name="Cyberpunk 2077",
            exe_names=["cyberpunk2077.exe"],
            system_prompt=(
                "You are a Cyberpunk 2077 expert. Help with: build optimization, "
                "quest walkthroughs, side gigs, weapon recommendations, cyberware setups, "
                "and secret locations. Provide concise tactical advice for combat."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="dark_souls_3",
            display_name="Dark Souls III",
            exe_names=["darksoulsiii.exe"],
            system_prompt=(
                "You are a Dark Souls III veteran. Help with: boss strategies, "
                "build recommendations, PvP tactics, item locations, and level design. "
                "Provide concise tips for tough encounters and mention parry/backstab opportunities."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="league_of_legends",
            display_name="League of Legends",
            exe_names=["LeagueClientUx.exe", "League of Legends.exe"],
            system_prompt=(
                "You are a Challenger-tier League of Legends coach. Provide pick/ban advice, "
                "lane matchups, rune setups, and mid-game macro plans tailored to the asked role."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="valorant",
            display_name="Valorant",
            exe_names=["VALORANT.exe", "valorant.exe"],
            system_prompt=(
                "You are an expert Valorant shot-caller. Provide agent compositions, "
                "utility lineups, economy advice, and map-specific executes."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="counter_strike_2",
            display_name="Counter-Strike 2",
            exe_names=["cs2.exe", "csgo.exe"],
            system_prompt=(
                "You are a Counter-Strike 2 analyst. Share buy strats, nade lineups, callouts, "
                "and aim/spray control tips for competitive play."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="dota_2",
            display_name="Dota 2",
            exe_names=["dota2.exe"],
            system_prompt=(
                "You are a Dota 2 drafter and coach. Offer hero counters, lane builds, "
                "power spike reminders, and teamfight execution plans."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="world_of_warcraft",
            display_name="World of Warcraft",
            exe_names=["Wow.exe", "WowClassic.exe"],
            system_prompt=(
                "You are a World of Warcraft raid lead. Give rotation tips, gearing paths, "
                "dungeon/raid mechanics, and class talent suggestions for retail and classic."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="minecraft",
            display_name="Minecraft",
            exe_names=["Minecraft.exe", "MinecraftLauncher.exe"],
            system_prompt=(
                "You are a master Minecraft builder. Provide crafting recipes, redstone ideas, "
                "survival progression routes, and mob farming tips."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="fortnite",
            display_name="Fortnite",
            exe_names=["FortniteClient-Win64-Shipping.exe"],
            system_prompt=(
                "You are a Fortnite coach. Offer drop spot plans, building/edit drills, "
                "loadout advice, and rotating strategies for the current season."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="pubg",
            display_name="PUBG",
            exe_names=["TslGame.exe"],
            system_prompt=(
                "You are a PUBG strategist. Provide drop recommendations, loot routes, "
                "mid-game rotation guidance, and gunplay tips for each map."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
        GameProfile(
            id="gta_v",
            display_name="GTA V",
            exe_names=["GTA5.exe", "gtavicecity.exe"],
            system_prompt=(
                "You are a GTA V expert. Provide heist prep tips, vehicle and weapon suggestions, "
                "and efficient money-making or exploration ideas."
            ),
            default_provider="anthropic",
            overlay_mode_default="compact",
            is_builtin=True,
        ),
    ]

    def __init__(self):
        """Initialize profile store and load profiles"""
        self.profiles: Dict[str, GameProfile] = {}
        self._custom_profile_ids: set = set()
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load profiles from JSON file and populate with built-ins"""
        # Start with built-in profiles
        for profile in self.BUILTIN_PROFILES:
            self.profiles[profile.id] = profile

        # Load custom profiles from file
        if PROFILES_FILE.exists():
            try:
                with open(PROFILES_FILE, 'r') as f:
                    data = json.load(f)
                    for profile_data in data.get('profiles', []):
                        profile = GameProfile.from_dict(profile_data)
                        self.profiles[profile.id] = profile
                        self._custom_profile_ids.add(profile.id)
                logger.info(f"Loaded {len(self._custom_profile_ids)} custom game profiles")
            except Exception as e:
                logger.error(f"Failed to load game profiles: {e}")

    def _save_to_disk(self) -> None:
        """Save all custom profiles to JSON file"""
        try:
            # Ensure directory exists
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # Only save custom profiles (not built-ins)
            custom_profiles = [
                self.profiles[pid].to_dict()
                for pid in self._custom_profile_ids
                if pid in self.profiles
            ]

            with open(PROFILES_FILE, 'w') as f:
                json.dump({'profiles': custom_profiles}, f, indent=2)
            logger.info(f"Saved {len(custom_profiles)} custom game profiles")
        except Exception as e:
            logger.error(f"Failed to save game profiles: {e}")

    def get_profile_by_id(self, profile_id: str) -> Optional[GameProfile]:
        """Get a profile by its ID"""
        return self.profiles.get(profile_id)

    def get_profile_by_executable(self, exe_name: str) -> GameProfile:
        """
        Find the profile matching the given executable name.

        Args:
            exe_name: Executable filename

        Returns:
            Matching GameProfile or generic_game profile as fallback
        """
        # Try exact matches first
        for profile in self.profiles.values():
            if profile.matches_executable(exe_name):
                logger.debug(f"Matched executable '{exe_name}' to profile '{profile.id}'")
                return profile

        # Fallback to generic game profile
        generic = self.profiles.get("generic_game")
        if generic:
            logger.debug(f"No specific profile for '{exe_name}', using generic profile")
            return generic

        # Should never happen, but have a hardcoded fallback
        logger.warning(f"No generic profile found, creating temporary fallback")
        return GameProfile(
            id="fallback",
            display_name="Game",
            exe_names=[],
            system_prompt="You are a helpful gaming AI assistant.",
            is_builtin=True,
        )

    def list_profiles(self) -> List[GameProfile]:
        """Get all profiles (built-in and custom)"""
        return list(self.profiles.values())

    def list_custom_profiles(self) -> List[GameProfile]:
        """Get only custom (non-built-in) profiles"""
        return [
            self.profiles[pid]
            for pid in self._custom_profile_ids
            if pid in self.profiles
        ]

    def create_profile(self, profile: GameProfile) -> bool:
        """
        Create a new custom profile.

        Args:
            profile: GameProfile to create

        Returns:
            True if created successfully, False if ID already exists
        """
        if profile.id in self.profiles:
            # Preserve the original contract: creation must be an insert-only
            # operation so accidental overwrites are prevented. Callers that
            # need to mutate an existing custom profile should use
            # ``update_profile``.
            logger.warning(
                "Profile ID '%s' already exists; creation is idempotent but will not overwrite",
                profile.id,
            )
            return False

        self.profiles[profile.id] = profile
        self._custom_profile_ids.add(profile.id)
        self._save_to_disk()
        logger.info(f"Created new game profile: {profile.id}")
        return True

    def update_profile(self, profile: GameProfile) -> bool:
        """
        Update an existing profile.

        Args:
            profile: GameProfile with updated values

        Returns:
            True if updated, False if not found
        """
        if profile.id not in self.profiles:
            logger.warning(f"Profile ID '{profile.id}' not found")
            return False

        # Cannot update built-in profiles
        if profile.id not in self._custom_profile_ids:
            logger.warning(f"Cannot update built-in profile '{profile.id}'")
            return False

        self.profiles[profile.id] = profile
        self._save_to_disk()
        logger.info(f"Updated game profile: {profile.id}")
        return True

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a custom profile.

        Args:
            profile_id: ID of profile to delete

        Returns:
            True if deleted, False if not found or is built-in
        """
        if profile_id not in self.profiles:
            logger.warning(f"Profile ID '{profile_id}' not found")
            return False

        # Cannot delete built-in profiles
        if profile_id not in self._custom_profile_ids:
            logger.warning(f"Cannot delete built-in profile '{profile_id}'")
            return False

        del self.profiles[profile_id]
        self._custom_profile_ids.discard(profile_id)
        self._save_to_disk()
        logger.info(f"Deleted game profile: {profile_id}")
        return True

    def duplicate_profile(self, profile_id: str, new_id: str, new_name: str) -> bool:
        """
        Create a copy of an existing profile with a new ID.

        Args:
            profile_id: ID of profile to duplicate
            new_id: New ID for the duplicate
            new_name: New display name for the duplicate

        Returns:
            True if duplicated successfully
        """
        if profile_id not in self.profiles:
            logger.warning(f"Profile ID '{profile_id}' not found")
            return False

        if new_id in self.profiles:
            logger.warning(f"Profile ID '{new_id}' already exists")
            return False

        original = self.profiles[profile_id]
        duplicate = GameProfile(
            id=new_id,
            display_name=new_name,
            exe_names=list(original.exe_names),
            system_prompt=original.system_prompt,
            default_provider=original.default_provider,
            default_model=original.default_model,
            overlay_mode_default=original.overlay_mode_default,
            extra_settings=dict(original.extra_settings),
            is_builtin=False,
        )

        return self.create_profile(duplicate)


# Global profile store instance
_profile_store: Optional[GameProfileStore] = None


def get_profile_store() -> GameProfileStore:
    """Get or create the global profile store instance"""
    global _profile_store
    if _profile_store is None:
        _profile_store = GameProfileStore()
    return _profile_store
