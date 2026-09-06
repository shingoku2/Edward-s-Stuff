"""Macro Store Module."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from omnix.base_store import BaseStore
from omnix.macro_manager import Macro, MacroStep

logger = logging.getLogger(__name__)


class MacroStore(BaseStore[Macro]):
    """
    Stores and retrieves macros from disk
    Handles JSON serialization and game profile associations
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the macro store

        Args:
            config_dir: Directory to store macros (defaults to ~/.gaming_ai_assistant)
        """
        super().__init__("macros", config_dir=config_dir)
        self.macros_dir = self.base_dir
        logger.info("MacroStore initialized at %s", self.macros_dir)

    def save_macro(self, macro: Macro) -> bool:
        """
        Save a macro to disk

        Args:
            macro: Macro object to save

        Returns:
            True if successful, False otherwise
        """
        macro_file = self.macros_dir / f"{macro.id}.json"
        if self._json_save(macro_file, macro.to_dict()):
            logger.info("Saved macro: %s (ID: %s)", macro.name, macro.id)
            return True
        logger.error("Failed to save macro %s", macro.id)
        return False

    def load_macro(self, macro_id: str) -> Optional[Macro]:
        """
        Load a macro from disk by ID

        Args:
            macro_id: ID of macro to load

        Returns:
            Macro object or None if not found
        """
        macro_file = self.macros_dir / f"{macro_id}.json"
        data = self._json_load(macro_file)
        if not data:
            logger.warning("Macro file not found: %s", macro_id)
            return None

        try:
            macro = Macro.from_dict(data)
            logger.debug("Loaded macro: %s (ID: %s)", macro.name, macro.id)
            return macro
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to deserialize macro %s: %s", macro_id, exc)
            return None

    def delete_macro(self, macro_id: str) -> bool:
        """
        Delete a macro from disk

        Args:
            macro_id: ID of macro to delete

        Returns:
            True if successful, False otherwise
        """
        macro_file = self.macros_dir / f"{macro_id}.json"
        if self._delete_file(macro_file):
            logger.info("Deleted macro file: %s", macro_id)
            return True
        logger.warning("Macro file not found: %s", macro_id)
        return False

    def load_all_macros(self) -> Dict[str, Macro]:
        """
        Load all macros from disk

        Returns:
            Dictionary of {macro_id: Macro}
        """
        macros: Dict[str, Macro] = {}
        for macro_file in self.iter_json_files(self.macros_dir):
            data = self._json_load(macro_file)
            if not data:
                continue
            try:
                macro = Macro.from_dict(data)
                macros[macro.id] = macro
            except Exception as exc:  # pragma: no cover
                logger.error("Failed to load macro from %s: %s", macro_file, exc)

        logger.info("Loaded %s macros from disk", len(macros))
        return macros

    def save_all_macros(self, macros: Dict[str, Macro]) -> bool:
        """
        Save all macros to disk

        Args:
            macros: Dictionary of {macro_id: Macro}

        Returns:
            True if all saved successfully
        """
        all_success = True

        for macro_id, macro in macros.items():
            if not self.save_macro(macro):
                all_success = False

        if all_success:
            logger.info(f"Saved {len(macros)} macros to disk")
        else:
            logger.warning(f"Failed to save some macros")

        return all_success

    def get_macros_for_game(self, game_profile_id: str) -> Dict[str, Macro]:
        """
        Get all macros for a specific game profile

        Args:
            game_profile_id: ID of game profile

        Returns:
            Dictionary of {macro_id: Macro} for that game
        """
        all_macros = self.load_all_macros()
        game_macros = {}

        for macro_id, macro in all_macros.items():
            if macro.game_profile_id == game_profile_id or macro.game_profile_id is None:
                game_macros[macro_id] = macro

        return game_macros

    def search_macros(self, query: str) -> Dict[str, Macro]:
        """
        Search macros by name or description

        Args:
            query: Search query

        Returns:
            Dictionary of {macro_id: Macro} matching query
        """
        all_macros = self.load_all_macros()
        results = {}
        query_lower = query.lower()

        for macro_id, macro in all_macros.items():
            if query_lower in macro.name.lower() or query_lower in macro.description.lower():
                results[macro_id] = macro

        return results

    def export_macro(self, macro_id: str, export_path: str) -> bool:
        """
        Export a macro to a standalone JSON file

        Args:
            macro_id: ID of macro to export
            export_path: Path to export to

        Returns:
            True if successful
        """
        try:
            macro = self.load_macro(macro_id)
            if not macro:
                logger.error(f"Macro not found: {macro_id}")
                return False

            with open(export_path, "w") as f:
                json.dump(macro.to_dict(), f, indent=2)

            logger.info(f"Exported macro {macro_id} to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export macro {macro_id}: {e}")
            return False

    def import_macro(self, import_path: str) -> Optional[Macro]:
        """
        Import a macro from a JSON file

        Args:
            import_path: Path to JSON file to import

        Returns:
            Imported Macro object or None if failed
        """
        try:
            with open(import_path, "r") as f:
                data = json.load(f)

            macro = Macro.from_dict(data)

            # Save the imported macro
            if self.save_macro(macro):
                logger.info(f"Imported macro: {macro.name}")
                return macro

            return None

        except Exception as e:
            logger.error(f"Failed to import macro from {import_path}: {e}")
            return None

    def get_macro_stats(self) -> Dict:
        """
        Get statistics about stored macros

        Returns:
            Dictionary with macro statistics
        """
        all_macros = self.load_all_macros()

        total_steps = sum(len(m.steps) for m in all_macros.values())
        total_duration = sum(m.get_total_duration() for m in all_macros.values())

        game_profiles: Dict[str, int] = {}
        for macro in all_macros.values():
            profile_id = macro.game_profile_id or "global"
            game_profiles[profile_id] = game_profiles.get(profile_id, 0) + 1

        return {
            "total_macros": len(all_macros),
            "total_steps": total_steps,
            "total_duration_ms": total_duration,
            "game_profiles": game_profiles,
            "last_updated": datetime.now().isoformat(),
        }
