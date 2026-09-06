"""Knowledge Pack Store Module."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from omnix.base_store import BaseStore
from omnix.knowledge_pack import KnowledgePack, KnowledgeSource

logger = logging.getLogger(__name__)


class KnowledgePackStore(BaseStore[KnowledgePack]):
    """
    Stores and retrieves knowledge packs from disk
    Handles JSON serialization and game profile associations
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the knowledge pack store

        Args:
            config_dir: Directory to store packs (defaults to ~/.gaming_ai_assistant)
        """
        super().__init__("knowledge_packs", config_dir=config_dir)
        self.packs_dir = self.base_dir
        self.sources_dir = self.ensure_subdir("knowledge_sources")

        logger.info("KnowledgePackStore initialized at %s", self.config_dir)

    def save_pack(self, pack: KnowledgePack) -> bool:
        """
        Save a knowledge pack to disk

        Args:
            pack: KnowledgePack object to save

        Returns:
            True if successful, False otherwise
        """
        pack.updated_at = datetime.now()
        pack_file = self.packs_dir / f"{pack.id}.json"
        if self._json_save(pack_file, pack.to_dict()):
            logger.info("Saved knowledge pack: %s (ID: %s)", pack.name, pack.id)
            return True

        logger.error("Failed to save knowledge pack %s", pack.id)
        return False

    def load_pack(self, pack_id: str) -> Optional[KnowledgePack]:
        """
        Load a knowledge pack from disk by ID

        Args:
            pack_id: ID of pack to load

        Returns:
            KnowledgePack object or None if not found
        """
        pack_file = self.packs_dir / f"{pack_id}.json"
        data = self._json_load(pack_file)
        if not data:
            logger.warning("Knowledge pack file not found: %s", pack_id)
            return None

        try:
            pack = KnowledgePack.from_dict(data)
            logger.debug("Loaded knowledge pack: %s (ID: %s)", pack.name, pack.id)
            return pack
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to deserialize knowledge pack %s: %s", pack_id, exc)
            return None

    def delete_pack(self, pack_id: str) -> bool:
        """
        Delete a knowledge pack from disk

        Args:
            pack_id: ID of pack to delete

        Returns:
            True if successful, False otherwise
        """
        pack_file = self.packs_dir / f"{pack_id}.json"
        if self._delete_file(pack_file):
            logger.info("Deleted knowledge pack file: %s", pack_id)
            return True

        logger.warning("Knowledge pack file not found: %s", pack_id)
        return False

    def load_all_packs(self) -> Dict[str, KnowledgePack]:
        """
        Load all knowledge packs from disk

        Returns:
            Dictionary of {pack_id: KnowledgePack}
        """
        packs: Dict[str, KnowledgePack] = {}

        for pack_file in self.iter_json_files(self.packs_dir):
            data = self._json_load(pack_file)
            if not data:
                continue
            try:
                pack = KnowledgePack.from_dict(data)
                packs[pack.id] = pack
            except Exception as exc:  # pragma: no cover
                logger.error("Failed to load knowledge pack from %s: %s", pack_file, exc)

        logger.info("Loaded %s knowledge packs from disk", len(packs))
        return packs

    def save_all_packs(self, packs: Dict[str, KnowledgePack]) -> bool:
        """
        Save all knowledge packs to disk

        Args:
            packs: Dictionary of {pack_id: KnowledgePack}

        Returns:
            True if all saved successfully
        """
        all_success = True

        for pack_id, pack in packs.items():
            if not self.save_pack(pack):
                all_success = False

        if all_success:
            logger.info(f"Saved {len(packs)} knowledge packs to disk")
        else:
            logger.warning(f"Failed to save some knowledge packs")

        return all_success

    def get_packs_for_game(self, game_profile_id: str) -> Dict[str, KnowledgePack]:
        """
        Get all knowledge packs for a specific game profile

        Args:
            game_profile_id: ID of game profile

        Returns:
            Dictionary of {pack_id: KnowledgePack} for that game
        """
        all_packs = self.load_all_packs()
        game_packs = {}

        for pack_id, pack in all_packs.items():
            if pack.game_profile_id == game_profile_id:
                game_packs[pack_id] = pack

        logger.debug(f"Found {len(game_packs)} packs for game profile '{game_profile_id}'")
        return game_packs

    def get_enabled_packs_for_game(self, game_profile_id: str) -> Dict[str, KnowledgePack]:
        """
        Get only enabled knowledge packs for a specific game profile

        Args:
            game_profile_id: ID of game profile

        Returns:
            Dictionary of {pack_id: KnowledgePack} for that game (enabled only)
        """
        game_packs = self.get_packs_for_game(game_profile_id)
        enabled_packs = {pack_id: pack for pack_id, pack in game_packs.items() if pack.enabled}

        logger.debug(
            f"Found {len(enabled_packs)} enabled packs for game profile '{game_profile_id}'"
        )
        return enabled_packs

    def search_packs(self, query: str) -> Dict[str, KnowledgePack]:
        """
        Search knowledge packs by name or description

        Args:
            query: Search query

        Returns:
            Dictionary of {pack_id: KnowledgePack} matching query
        """
        all_packs = self.load_all_packs()
        results = {}
        query_lower = query.lower()

        for pack_id, pack in all_packs.items():
            if query_lower in pack.name.lower() or query_lower in pack.description.lower():
                results[pack_id] = pack

        return results

    def get_pack_stats(self) -> Dict:
        """
        Get statistics about stored knowledge packs

        Returns:
            Dictionary with pack statistics
        """
        all_packs = self.load_all_packs()

        total_sources = sum(len(p.sources) for p in all_packs.values())

        game_profiles: Dict[str, int] = {}
        for pack in all_packs.values():
            profile_id = pack.game_profile_id
            game_profiles[profile_id] = game_profiles.get(profile_id, 0) + 1

        source_types: Dict[str, int] = {}
        for pack in all_packs.values():
            for source in pack.sources:
                source_types[source.type] = source_types.get(source.type, 0) + 1

        return {
            "total_packs": len(all_packs),
            "total_sources": total_sources,
            "game_profiles": game_profiles,
            "source_types": source_types,
            "last_updated": datetime.now().isoformat(),
        }

    def export_pack(self, pack_id: str, export_path: str) -> bool:
        """
        Export a knowledge pack to a standalone JSON file

        Args:
            pack_id: ID of pack to export
            export_path: Path to export to

        Returns:
            True if successful
        """
        pack = self.load_pack(pack_id)
        if not pack:
            logger.error("Knowledge pack not found: %s", pack_id)
            return False

        return self._json_save(Path(export_path), pack.to_dict())

    def import_pack(self, import_path: str) -> Optional[KnowledgePack]:
        """
        Import a knowledge pack from a JSON file

        Args:
            import_path: Path to JSON file to import

        Returns:
            Imported KnowledgePack object or None if failed
        """
        data = self._json_load(Path(import_path))
        if not data:
            logger.error("Failed to import knowledge pack from %s", import_path)
            return None

        try:
            pack = KnowledgePack.from_dict(data)
        except Exception as exc:  # pragma: no cover
            logger.error("Invalid knowledge pack file %s: %s", import_path, exc)
            return None

        if self.save_pack(pack):
            logger.info("Imported knowledge pack: %s", pack.name)
            return pack
        return None


# Global knowledge pack store instance
_knowledge_pack_store: Optional[KnowledgePackStore] = None


def get_knowledge_pack_store() -> KnowledgePackStore:
    """Get or create the global knowledge pack store instance"""
    global _knowledge_pack_store
    if _knowledge_pack_store is None:
        _knowledge_pack_store = KnowledgePackStore()
    return _knowledge_pack_store
