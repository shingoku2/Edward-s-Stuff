"""
Knowledge Pack Store Module
Handles persistence of knowledge packs to disk (JSON format)
"""

import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from knowledge_pack import KnowledgePack, KnowledgeSource

logger = logging.getLogger(__name__)


class KnowledgePackStore:
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
        if config_dir is None:
            config_dir = os.path.expanduser("~/.gaming_ai_assistant")

        self.config_dir = Path(config_dir)
        self.packs_dir = self.config_dir / "knowledge_packs"
        self.sources_dir = self.config_dir / "knowledge_sources"

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.packs_dir.mkdir(parents=True, exist_ok=True)
        self.sources_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"KnowledgePackStore initialized at {self.config_dir}")

    def save_pack(self, pack: KnowledgePack) -> bool:
        """
        Save a knowledge pack to disk

        Args:
            pack: KnowledgePack object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update timestamp
            pack.updated_at = datetime.now()

            # Save pack file
            pack_file = self.packs_dir / f"{pack.id}.json"

            with open(pack_file, 'w') as f:
                json.dump(pack.to_dict(), f, indent=2)

            logger.info(f"Saved knowledge pack: {pack.name} (ID: {pack.id})")
            return True

        except Exception as e:
            logger.error(f"Failed to save knowledge pack {pack.id}: {e}")
            return False

    def load_pack(self, pack_id: str) -> Optional[KnowledgePack]:
        """
        Load a knowledge pack from disk by ID

        Args:
            pack_id: ID of pack to load

        Returns:
            KnowledgePack object or None if not found
        """
        try:
            pack_file = self.packs_dir / f"{pack_id}.json"

            if not pack_file.exists():
                logger.warning(f"Knowledge pack file not found: {pack_id}")
                return None

            with open(pack_file, 'r') as f:
                data = json.load(f)

            pack = KnowledgePack.from_dict(data)
            logger.debug(f"Loaded knowledge pack: {pack.name} (ID: {pack.id})")
            return pack

        except Exception as e:
            logger.error(f"Failed to load knowledge pack {pack_id}: {e}")
            return None

    def delete_pack(self, pack_id: str) -> bool:
        """
        Delete a knowledge pack from disk

        Args:
            pack_id: ID of pack to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            pack_file = self.packs_dir / f"{pack_id}.json"

            if pack_file.exists():
                pack_file.unlink()
                logger.info(f"Deleted knowledge pack file: {pack_id}")
                return True

            logger.warning(f"Knowledge pack file not found: {pack_id}")
            return False

        except Exception as e:
            logger.error(f"Failed to delete knowledge pack {pack_id}: {e}")
            return False

    def load_all_packs(self) -> Dict[str, KnowledgePack]:
        """
        Load all knowledge packs from disk

        Returns:
            Dictionary of {pack_id: KnowledgePack}
        """
        packs = {}

        try:
            if not self.packs_dir.exists():
                logger.warning(f"Knowledge packs directory not found: {self.packs_dir}")
                return packs

            for pack_file in self.packs_dir.glob("*.json"):
                try:
                    with open(pack_file, 'r') as f:
                        data = json.load(f)

                    pack = KnowledgePack.from_dict(data)
                    packs[pack.id] = pack

                except Exception as e:
                    logger.error(f"Failed to load knowledge pack from {pack_file}: {e}")

            logger.info(f"Loaded {len(packs)} knowledge packs from disk")
            return packs

        except Exception as e:
            logger.error(f"Failed to load knowledge packs: {e}")
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
        enabled_packs = {
            pack_id: pack
            for pack_id, pack in game_packs.items()
            if pack.enabled
        }

        logger.debug(f"Found {len(enabled_packs)} enabled packs for game profile '{game_profile_id}'")
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

        game_profiles = {}
        for pack in all_packs.values():
            profile_id = pack.game_profile_id
            if profile_id not in game_profiles:
                game_profiles[profile_id] = 0
            game_profiles[profile_id] += 1

        source_types = {}
        for pack in all_packs.values():
            for source in pack.sources:
                if source.type not in source_types:
                    source_types[source.type] = 0
                source_types[source.type] += 1

        return {
            'total_packs': len(all_packs),
            'total_sources': total_sources,
            'game_profiles': game_profiles,
            'source_types': source_types,
            'last_updated': datetime.now().isoformat()
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
        try:
            pack = self.load_pack(pack_id)
            if not pack:
                logger.error(f"Knowledge pack not found: {pack_id}")
                return False

            with open(export_path, 'w') as f:
                json.dump(pack.to_dict(), f, indent=2)

            logger.info(f"Exported knowledge pack {pack_id} to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export knowledge pack {pack_id}: {e}")
            return False

    def import_pack(self, import_path: str) -> Optional[KnowledgePack]:
        """
        Import a knowledge pack from a JSON file

        Args:
            import_path: Path to JSON file to import

        Returns:
            Imported KnowledgePack object or None if failed
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)

            pack = KnowledgePack.from_dict(data)

            # Save the imported pack
            if self.save_pack(pack):
                logger.info(f"Imported knowledge pack: {pack.name}")
                return pack

            return None

        except Exception as e:
            logger.error(f"Failed to import knowledge pack from {import_path}: {e}")
            return None


# Global knowledge pack store instance
_knowledge_pack_store: Optional[KnowledgePackStore] = None


def get_knowledge_pack_store() -> KnowledgePackStore:
    """Get or create the global knowledge pack store instance"""
    global _knowledge_pack_store
    if _knowledge_pack_store is None:
        _knowledge_pack_store = KnowledgePackStore()
    return _knowledge_pack_store
