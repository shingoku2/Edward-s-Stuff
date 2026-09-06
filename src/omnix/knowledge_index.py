"""
Knowledge Index Module
Handles embedding generation and semantic search over knowledge packs
"""

import hashlib
import json
import logging
import math
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from omnix.knowledge_pack import KnowledgePack, KnowledgeSource, RetrievedChunk
from omnix.knowledge_store import get_knowledge_pack_store

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """
    Abstract base for embedding generation.
    Currently uses SimpleTFIDFEmbedding for local operation.
    """

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        raise NotImplementedError

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (can be optimized per provider)"""
        return [self.generate_embedding(text) for text in texts]


class SimpleTFIDFEmbedding(EmbeddingProvider):
    """
    Simple TF-IDF based embedding provider for local operation.
    Not as powerful as transformer models but requires no external API.
    """

    def __init__(self):
        self.vocabulary = {}
        self.idf = {}
        self.documents = []

    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "type": "SimpleTFIDFEmbedding",
            "vocabulary": self.vocabulary,
            "idf": self.idf,
            "documents": self.documents,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SimpleTFIDFEmbedding":
        """Deserialize from dictionary"""
        instance = cls()
        instance.vocabulary = data.get("vocabulary", {})
        instance.idf = data.get("idf", {})
        instance.documents = data.get("documents", [])
        return instance

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and split on whitespace/punctuation
        import re

        text = text.lower()
        tokens = re.findall(r"\w+", text)
        return tokens

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency"""
        tf = {}
        total = len(tokens)
        if total == 0:
            return tf

        for token in tokens:
            tf[token] = tf.get(token, 0) + 1

        # Normalize
        for token in tf:
            tf[token] = tf[token] / total

        return tf

    def fit(self, documents: List[str]) -> None:
        """Fit the TF-IDF model on a corpus"""
        self.documents = documents
        doc_count = len(documents)

        # Build vocabulary and document frequency
        doc_freq = {}
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        # Compute IDF
        self.idf = {}
        for token, freq in doc_freq.items():
            self.idf[token] = math.log(doc_count / (freq + 1))

        # Build vocabulary
        self.vocabulary = {token: idx for idx, token in enumerate(sorted(self.idf.keys()))}

    def generate_embedding(self, text: str) -> List[float]:
        """Generate TF-IDF embedding vector"""
        if not self.vocabulary:
            # If not fitted, return a simple bag-of-words hash
            return self._simple_hash_embedding(text)

        tokens = self._tokenize(text)
        tf = self._compute_tf(tokens)

        # Create vector
        vector = [0.0] * len(self.vocabulary)
        for token, tf_value in tf.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                idf_value = self.idf.get(token, 0)
                vector[idx] = tf_value * idf_value

        # Normalize
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector

    def _simple_hash_embedding(self, text: str, size: int = 128) -> List[float]:
        """Fallback: simple hash-based embedding"""
        tokens = self._tokenize(text)
        vector = [0.0] * size

        for token in tokens:
            hash_val = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            idx = hash_val % size
            vector[idx] += 1.0

        # Normalize
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector


class KnowledgeIndex:
    """
    Vector index for knowledge packs.
    Supports adding packs, removing packs, and semantic search.
    """

    def __init__(
        self,
        config_dir: Optional[str] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        knowledge_store=None,
    ):
        """
        Initialize knowledge index

        Args:
            config_dir: Directory to store index (defaults to ~/.gaming_ai_assistant)
            embedding_provider: Provider for generating embeddings (defaults to SimpleTFIDFEmbedding)
            knowledge_store: KnowledgePackStore instance (defaults to global singleton)
                            Injecting this dependency makes testing much easier.
        """
        if config_dir is None:
            self.config_dir = Path(
                os.getenv("OMNIX_CONFIG_DIR", str(Path.home() / ".gaming_ai_assistant"))
            )
        else:
            self.config_dir = Path(config_dir)

        self.index_dir = self.config_dir / "knowledge_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.index_dir / "index.json"
        self.database_file = self.index_dir / "knowledge.db"
        self._initialize_database()

        # Embedding provider
        self.embedding_provider = embedding_provider or SimpleTFIDFEmbedding()

        # Knowledge store (with dependency injection for better testability)
        if knowledge_store is None:
            # Use global singleton as default
            self.knowledge_store = get_knowledge_pack_store()
        else:
            # Use injected store (useful for testing)
            self.knowledge_store = knowledge_store

        # Index data structures
        # {game_profile_id: {chunk_id: (text, source_id, pack_id, embedding, meta)}}
        self.index: Dict[str, Dict[str, Tuple[str, str, str, List[float], Dict]]] = {}

        # Load existing index
        self._load_index()

        logger.info(f"KnowledgeIndex initialized at {self.index_dir}")

    def _load_index(self) -> None:
        """Load index AND embedding model from disk (JSON format)"""
        try:
            # Try loading from JSON first (new secure format)
            if self.index_file.exists():
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Restore index
                self.index = data.get("index", {})

                # Restore embedding provider if present
                if data.get("embedding_provider"):
                    provider_data = data["embedding_provider"]
                    if provider_data.get("type") == "SimpleTFIDFEmbedding":
                        self.embedding_provider = SimpleTFIDFEmbedding.from_dict(provider_data)
                        logger.info("Loaded TF-IDF model from disk (JSON)")

                logger.info(
                    f"Loaded knowledge index with {sum(len(chunks) for chunks in self.index.values())} chunks"
                )
                return

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self.index = {}

        self._load_chunks_from_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_file, timeout=10)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize_database(self) -> None:
        """Create the durable chunk store and its built-in full-text index."""
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    game_profile_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    pack_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS chunks_game_idx ON chunks(game_profile_id);
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    game_profile_id UNINDEXED,
                    content,
                    tokenize='unicode61'
                );
                """)

    def _load_chunks_from_database(self) -> None:
        """Recover the in-memory index from SQLite when legacy JSON is absent."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT chunk_id, game_profile_id, source_id, pack_id, content, "
                "embedding_json, metadata_json FROM chunks"
            ).fetchall()
        for chunk_id, game_id, source_id, pack_id, content, embedding, metadata in rows:
            self.index.setdefault(game_id, {})[chunk_id] = (
                content,
                source_id,
                pack_id,
                json.loads(embedding),
                json.loads(metadata),
            )

    def _sync_database(self) -> None:
        rows = []
        for game_id, chunks in self.index.items():
            for chunk_id, (content, source_id, pack_id, embedding, metadata) in chunks.items():
                rows.append(
                    (
                        chunk_id,
                        game_id,
                        source_id,
                        pack_id,
                        content,
                        json.dumps(embedding),
                        json.dumps(metadata),
                    )
                )
        with self._connect() as connection:
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM chunks_fts")
            connection.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
            connection.executemany(
                "INSERT INTO chunks_fts(chunk_id, game_profile_id, content) VALUES (?, ?, ?)",
                [(row[0], row[1], row[4]) for row in rows],
            )

    def _save_index(self) -> None:
        """Save index AND embedding model to disk (JSON format)"""
        try:
            data = {
                "index": self.index,
                # Save the provider if it's our local TF-IDF one
                "embedding_provider": (
                    self.embedding_provider.to_dict()
                    if isinstance(self.embedding_provider, SimpleTFIDFEmbedding)
                    else None
                ),
            }
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self._sync_database()
            logger.info("Saved knowledge index and model to disk (JSON)")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks respecting word boundaries.

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters

        Returns:
            List of text chunks
        """
        if not text:
            return []

        words = text.split()
        chunks = []
        current_chunk_words = []
        current_length = 0

        # Helper to reconstruct string from words
        def join_words(word_list):
            return " ".join(word_list)

        for word in words:
            word_len = len(word) + 1  # +1 for space

            if current_length + word_len > chunk_size and current_chunk_words:
                # Chunk is full, save it
                chunks.append(join_words(current_chunk_words))

                # Calculate overlap (keep last N words that fit in overlap size)
                overlap_words = []
                overlap_len = 0
                for w in reversed(current_chunk_words):
                    if overlap_len + len(w) + 1 <= overlap:
                        overlap_words.insert(0, w)
                        overlap_len += len(w) + 1
                    else:
                        break

                current_chunk_words = overlap_words
                current_chunk_words.append(word)
                current_length = overlap_len + word_len
            else:
                current_chunk_words.append(word)
                current_length += word_len

        # Add the final chunk
        if current_chunk_words:
            chunks.append(join_words(current_chunk_words))

        return chunks

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def rebuild_index_for_game(self, game_profile_id: str) -> None:
        """
        Rebuild the entire index for a game profile.
        This ensures TF-IDF is calculated correctly across ALL packs for the game.

        Args:
            game_profile_id: Game profile ID to rebuild index for
        """
        logger.info(f"Rebuilding index for game profile: {game_profile_id}")

        # Get all packs for this game using injected dependency
        all_packs = self.knowledge_store.get_packs_for_game(game_profile_id)

        if not all_packs:
            logger.warning(f"No packs found for game profile: {game_profile_id}")
            return

        # Clear existing index for this game
        if game_profile_id in self.index:
            del self.index[game_profile_id]
        self.index[game_profile_id] = {}

        # Collect all texts from all packs for corpus-wide TF-IDF
        all_texts = []
        for pack in all_packs.values():
            if not pack.enabled:
                continue
            for source in pack.sources:
                if source.content:
                    # Chunk the text for TF-IDF fitting
                    chunks = self._chunk_text(source.content)
                    all_texts.extend(chunks)

        # Fit TF-IDF on entire corpus for this game
        if isinstance(self.embedding_provider, SimpleTFIDFEmbedding) and all_texts:
            logger.info(
                f"Fitting TF-IDF model on {len(all_texts)} chunks from {len(all_packs)} packs"
            )
            self.embedding_provider.fit(all_texts)

        # Now index each pack
        for pack in all_packs.values():
            if not pack.enabled:
                logger.info(f"Skipping disabled pack: {pack.name}")
                continue
            self._index_pack_with_existing_vocabulary(pack)

        # Save index
        self._save_index()
        logger.info(f"Rebuilt index for game '{game_profile_id}' with {len(all_packs)} packs")

    def _index_pack_with_existing_vocabulary(self, pack: KnowledgePack) -> None:
        """
        Index a pack using the already-fitted TF-IDF vocabulary.
        This is called by rebuild_index_for_game after fitting the model.

        Args:
            pack: KnowledgePack to index
        """
        game_profile_id = pack.game_profile_id

        if game_profile_id not in self.index:
            self.index[game_profile_id] = {}

        # Index each source
        for source in pack.sources:
            if not source.content:
                logger.warning(f"Skipping source {source.id} - no content")
                continue

            # Chunk the text
            chunks = self._chunk_text(source.content)

            # Generate embeddings and store
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{pack.id}_{source.id}_{idx}"

                # Generate embedding using existing vocabulary
                embedding = self.embedding_provider.generate_embedding(chunk)

                # Store in index
                meta = {
                    "source_title": source.title,
                    "source_type": source.type,
                    "pack_name": pack.name,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                }

                self.index[game_profile_id][chunk_id] = (chunk, source.id, pack.id, embedding, meta)

    def add_pack(self, pack: KnowledgePack) -> None:
        """
        Add a knowledge pack to the index.

        IMPORTANT: This method now rebuilds the entire index for the game
        to ensure TF-IDF is calculated correctly across ALL packs.

        Args:
            pack: KnowledgePack to index
        """
        logger.info(f"Adding knowledge pack: {pack.name}")

        # Rebuild entire index for this game to ensure correct TF-IDF
        self.rebuild_index_for_game(pack.game_profile_id)

    def remove_pack(self, pack_id: str, game_profile_id: Optional[str] = None) -> None:
        """
        Remove a knowledge pack from the index and rebuild to recalculate TF-IDF

        Args:
            pack_id: ID of pack to remove
            game_profile_id: Optional game profile ID to rebuild. If None, searches all games.
        """
        removed_count = 0
        affected_games = set()

        # Find and remove chunks from this pack
        for gp_id in list(self.index.keys()):
            # Remove all chunks from this pack
            chunks_to_remove = [
                chunk_id
                for chunk_id, (_, _, pid, _, _) in self.index[gp_id].items()
                if pid == pack_id
            ]

            if chunks_to_remove:
                for chunk_id in chunks_to_remove:
                    del self.index[gp_id][chunk_id]
                    removed_count += 1
                affected_games.add(gp_id)

        logger.info(f"Removed {removed_count} chunks for pack '{pack_id}'")

        # Rebuild index for affected games to recalculate TF-IDF
        for gp_id in affected_games:
            logger.info(f"Rebuilding index for game '{gp_id}' after pack removal")
            self.rebuild_index_for_game(gp_id)

        # Save index
        self._save_index()

    def query(self, game_profile_id: str, question: str, top_k: int = 5) -> List[RetrievedChunk]:
        """
        Query the index for relevant chunks

        Args:
            game_profile_id: Game profile to search within
            question: Question/query text
            top_k: Number of top results to return

        Returns:
            List of RetrievedChunk objects, sorted by relevance
        """
        if game_profile_id not in self.index:
            logger.debug(f"No index found for game profile: {game_profile_id}")
            return []

        # Generate query embedding
        query_embedding = self.embedding_provider.generate_embedding(question)

        candidate_ids = self._full_text_candidates(game_profile_id, question, max(top_k * 8, 40))

        # Score the lexical candidates semantically. If FTS finds no match, score
        # the whole game index so natural-language similarity remains available.
        scores = []
        for chunk_id, (text, source_id, pack_id, embedding, meta) in self.index[
            game_profile_id
        ].items():
            if candidate_ids and chunk_id not in candidate_ids:
                continue
            score = self._cosine_similarity(query_embedding, embedding)
            scores.append((score, text, source_id, meta))

        # Sort by score (descending)
        scores.sort(reverse=True, key=lambda x: x[0])

        # Return top K
        results = []
        for score, text, source_id, meta in scores[:top_k]:
            chunk = RetrievedChunk(text=text, source_id=source_id, score=score, meta=meta)
            results.append(chunk)

        logger.debug(f"Retrieved {len(results)} chunks for query in game '{game_profile_id}'")
        return results

    def _full_text_candidates(self, game_profile_id: str, question: str, limit: int) -> set[str]:
        tokens = (
            self.embedding_provider._tokenize(question)
            if isinstance(self.embedding_provider, SimpleTFIDFEmbedding)
            else question.split()
        )
        expression = " OR ".join(f'"{token}"' for token in tokens if token)
        if not expression:
            return set()
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH ? "
                    "AND game_profile_id = ? ORDER BY rank LIMIT ?",
                    (expression, game_profile_id, limit),
                ).fetchall()
            return {row[0] for row in rows}
        except sqlite3.OperationalError as exc:
            logger.warning("FTS query failed; using semantic index: %s", exc)
            return set()

    def get_stats(self) -> Dict:
        """Get statistics about the index"""
        total_chunks = sum(len(chunks) for chunks in self.index.values())
        game_profiles = list(self.index.keys())

        return {
            "total_chunks": total_chunks,
            "game_profiles": game_profiles,
            "embedding_provider": type(self.embedding_provider).__name__,
            "storage_backend": "sqlite-fts5",
        }


# Global knowledge index instance
_knowledge_index: Optional[KnowledgeIndex] = None


def get_knowledge_index(embedding_provider: Optional[EmbeddingProvider] = None) -> KnowledgeIndex:
    """Get or create the global knowledge index instance"""
    global _knowledge_index
    if _knowledge_index is None:
        _knowledge_index = KnowledgeIndex(embedding_provider=embedding_provider)
    return _knowledge_index
