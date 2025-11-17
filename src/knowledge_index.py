"""
Knowledge Index Module
Handles embedding generation and semantic search over knowledge packs
"""

import logging
import json
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import math

from knowledge_pack import KnowledgePack, KnowledgeSource, RetrievedChunk
from knowledge_store import get_knowledge_pack_store

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """
    Abstract base for embedding generation.
    Can be extended to support different providers (OpenAI, sentence-transformers, etc.)
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

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and split on whitespace/punctuation
        import re
        text = text.lower()
        tokens = re.findall(r'\w+', text)
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
            hash_val = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = hash_val % size
            vector[idx] += 1.0

        # Normalize
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector


class OpenAIEmbedding(EmbeddingProvider):
    """
    OpenAI embedding provider using their embedding API.
    Requires OpenAI API key.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding provider

        Args:
            api_key: OpenAI API key
            model: Embedding model to use (default: text-embedding-3-small)
        """
        self.api_key = api_key
        self.model = model
        self._check_api_available()

    def _check_api_available(self):
        """Check if OpenAI library is available"""
        try:
            import openai
            self.openai = openai
        except ImportError:
            logger.warning("OpenAI library not available. Install with: pip install openai")
            self.openai = None

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        if not self.openai:
            raise RuntimeError("OpenAI library not available")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            response = client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (optimized batch API call)"""
        if not self.openai:
            raise RuntimeError("OpenAI library not available")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            response = client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in response.data]

        except Exception as e:
            logger.error(f"Failed to generate embeddings batch: {e}")
            raise


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
            config_dir = Path.home() / '.gaming_ai_assistant'
        else:
            config_dir = Path(config_dir)

        self.config_dir = config_dir
        self.index_dir = self.config_dir / "knowledge_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.index_dir / "index.pkl"

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
        """Load index from disk"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'rb') as f:
                    self.index = pickle.load(f)
                logger.info(f"Loaded knowledge index with {sum(len(chunks) for chunks in self.index.values())} chunks")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self.index = {}

    def _save_index(self) -> None:
        """Save index to disk"""
        try:
            with open(self.index_file, 'wb') as f:
                pickle.dump(self.index, f)
            logger.info("Saved knowledge index to disk")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation
                last_period = max(chunk.rfind('.'), chunk.rfind('?'), chunk.rfind('!'))
                if last_period > chunk_size // 2:  # Only break if in latter half
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk.strip())
            start = end - overlap

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
        for pack in all_packs:
            if not pack.enabled:
                continue
            for source in pack.sources:
                if source.content:
                    # Chunk the text for TF-IDF fitting
                    chunks = self._chunk_text(source.content)
                    all_texts.extend(chunks)

        # Fit TF-IDF on entire corpus for this game
        if isinstance(self.embedding_provider, SimpleTFIDFEmbedding) and all_texts:
            logger.info(f"Fitting TF-IDF model on {len(all_texts)} chunks from {len(all_packs)} packs")
            self.embedding_provider.fit(all_texts)

        # Now index each pack
        for pack in all_packs:
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
                    'source_title': source.title,
                    'source_type': source.type,
                    'pack_name': pack.name,
                    'chunk_index': idx,
                    'total_chunks': len(chunks)
                }

                self.index[game_profile_id][chunk_id] = (
                    chunk,
                    source.id,
                    pack.id,
                    embedding,
                    meta
                )

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

        # Score all chunks
        scores = []
        for chunk_id, (text, source_id, pack_id, embedding, meta) in self.index[game_profile_id].items():
            score = self._cosine_similarity(query_embedding, embedding)
            scores.append((score, text, source_id, meta))

        # Sort by score (descending)
        scores.sort(reverse=True, key=lambda x: x[0])

        # Return top K
        results = []
        for score, text, source_id, meta in scores[:top_k]:
            chunk = RetrievedChunk(
                text=text,
                source_id=source_id,
                score=score,
                meta=meta
            )
            results.append(chunk)

        logger.debug(f"Retrieved {len(results)} chunks for query in game '{game_profile_id}'")
        return results

    def get_stats(self) -> Dict:
        """Get statistics about the index"""
        total_chunks = sum(len(chunks) for chunks in self.index.values())
        game_profiles = list(self.index.keys())

        return {
            'total_chunks': total_chunks,
            'game_profiles': game_profiles,
            'embedding_provider': type(self.embedding_provider).__name__
        }


# Global knowledge index instance
_knowledge_index: Optional[KnowledgeIndex] = None


def get_knowledge_index(embedding_provider: Optional[EmbeddingProvider] = None) -> KnowledgeIndex:
    """Get or create the global knowledge index instance"""
    global _knowledge_index
    if _knowledge_index is None:
        _knowledge_index = KnowledgeIndex(embedding_provider=embedding_provider)
    return _knowledge_index
