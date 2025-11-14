"""
Knowledge Pack Module
Manages per-game knowledge sources for grounded Q&A
"""

import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeSource:
    """
    Represents a single knowledge source (file, URL, or note).

    Attributes:
        id: Unique identifier for this source
        type: Source type - "file", "url", or "note"
        path: File system path (for type="file")
        url: Web URL (for type="url")
        title: Human-readable title/name
        tags: List of tags for organization
        content: Raw text content (for type="note", or cached content)
    """
    id: str
    type: str  # "file", "url", "note"
    title: str
    path: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    content: Optional[str] = None  # For notes or cached content

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "KnowledgeSource":
        """Create from dictionary"""
        return cls(**data)

    def validate(self) -> bool:
        """Validate source has required fields based on type"""
        if self.type == "file":
            return self.path is not None
        elif self.type == "url":
            return self.url is not None
        elif self.type == "note":
            return self.content is not None
        return False


@dataclass
class KnowledgePack:
    """
    Represents a collection of knowledge sources for a specific game.

    Attributes:
        id: Unique identifier
        name: Human-readable name
        description: Description of this knowledge pack
        game_profile_id: Associated game profile ID
        sources: List of knowledge sources
        enabled: Whether this pack is active for queries
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        extra_settings: Extensibility dictionary for future features
    """
    id: str
    name: str
    description: str
    game_profile_id: str
    sources: List[KnowledgeSource]
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extra_settings: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

        # Convert string timestamps back to datetime if needed
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

        # Convert source dicts to KnowledgeSource objects if needed
        if self.sources and isinstance(self.sources[0], dict):
            self.sources = [KnowledgeSource.from_dict(s) for s in self.sources]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "KnowledgePack":
        """Create from dictionary"""
        return cls(**data)

    def add_source(self, source: KnowledgeSource) -> None:
        """Add a knowledge source to this pack"""
        if source.validate():
            self.sources.append(source)
            self.updated_at = datetime.now()
            logger.info(f"Added source '{source.title}' to pack '{self.name}'")
        else:
            logger.error(f"Invalid source: {source}")

    def remove_source(self, source_id: str) -> bool:
        """Remove a source by ID"""
        original_len = len(self.sources)
        self.sources = [s for s in self.sources if s.id != source_id]
        if len(self.sources) < original_len:
            self.updated_at = datetime.now()
            logger.info(f"Removed source {source_id} from pack '{self.name}'")
            return True
        return False

    def get_source_count(self) -> int:
        """Get number of sources in this pack"""
        return len(self.sources)

    def get_sources_by_type(self, source_type: str) -> List[KnowledgeSource]:
        """Get all sources of a specific type"""
        return [s for s in self.sources if s.type == source_type]


@dataclass
class RetrievedChunk:
    """
    Represents a chunk of text retrieved from knowledge index.

    Attributes:
        text: The actual text content
        source_id: ID of the knowledge source this came from
        score: Relevance score (higher is better)
        meta: Additional metadata (source title, pack name, etc.)
    """
    text: str
    source_id: str
    score: float
    meta: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "RetrievedChunk":
        """Create from dictionary"""
        return cls(**data)
