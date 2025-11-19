"""
Unit tests for Knowledge Pack system

Tests knowledge pack creation, storage, indexing, and retrieval.
"""
import pytest
from pathlib import Path
from datetime import datetime


@pytest.mark.unit
class TestKnowledgeModels:
    """Test knowledge pack data models"""

    def test_knowledge_source_creation(self):
        """Test creating a knowledge source"""
        from knowledge_pack import KnowledgeSource

        source = KnowledgeSource(
            id="test_source",
            type="note",
            title="Test Note",
            content="This is test content"
        )

        assert source.id == "test_source"
        assert source.type == "note"
        assert source.validate() is True

    def test_file_source_validation(self):
        """Test file source validation"""
        from knowledge_pack import KnowledgeSource

        # Valid file source
        file_source = KnowledgeSource(
            id="file1",
            type="file",
            title="File",
            path="/path/to/file.txt"
        )
        assert file_source.validate() is True

        # Invalid file source (no path)
        invalid_file = KnowledgeSource(
            id="file2",
            type="file",
            title="File"
        )
        assert invalid_file.validate() is False

    def test_knowledge_pack_creation(self):
        """Test creating a knowledge pack"""
        from knowledge_pack import KnowledgePack, KnowledgeSource

        sources = [
            KnowledgeSource(
                id="s1",
                type="note",
                title="Note 1",
                content="Content 1"
            )
        ]

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="A test pack",
            game_profile_id="elden_ring",
            sources=sources
        )

        assert pack.id == "pack1"
        assert len(pack.sources) == 1
        assert pack.enabled is True

    def test_knowledge_pack_add_remove_source(self):
        """Test adding and removing sources"""
        from knowledge_pack import KnowledgePack, KnowledgeSource

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="elden_ring",
            sources=[]
        )

        # Add source
        source = KnowledgeSource(
            id="s1",
            type="note",
            title="Note 1",
            content="Content 1"
        )
        pack.add_source(source)
        assert pack.get_source_count() == 1

        # Remove source
        pack.remove_source("s1")
        assert pack.get_source_count() == 0

    def test_knowledge_pack_serialization(self):
        """Test pack serialization"""
        from knowledge_pack import KnowledgePack

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )

        # Serialize
        pack_dict = pack.to_dict()
        assert pack_dict['id'] == 'pack1'

        # Deserialize
        pack2 = KnowledgePack.from_dict(pack_dict)
        assert pack2.id == pack.id
        assert pack2.name == pack.name


@pytest.mark.unit
class TestKnowledgeStore:
    """Test knowledge pack storage"""

    def test_save_and_load_pack(self, temp_dir):
        """Test saving and loading a pack"""
        from knowledge_store import KnowledgePackStore
        from knowledge_pack import KnowledgePack

        store = KnowledgePackStore(config_dir=temp_dir)

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )

        # Save
        success = store.save_pack(pack)
        assert success is True

        # Load
        loaded_pack = store.load_pack("pack1")
        assert loaded_pack is not None
        assert loaded_pack.id == "pack1"
        assert loaded_pack.name == "Test Pack"

    def test_delete_pack(self, temp_dir):
        """Test deleting a pack"""
        from knowledge_store import KnowledgePackStore
        from knowledge_pack import KnowledgePack

        store = KnowledgePackStore(config_dir=temp_dir)

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )

        # Save and delete
        store.save_pack(pack)
        success = store.delete_pack("pack1")
        assert success is True

        # Verify deleted
        loaded_pack = store.load_pack("pack1")
        assert loaded_pack is None

    def test_get_packs_for_game(self, temp_dir):
        """Test filtering packs by game profile"""
        from knowledge_store import KnowledgePackStore
        from knowledge_pack import KnowledgePack

        store = KnowledgePackStore(config_dir=temp_dir)

        pack1 = KnowledgePack(
            id="pack1",
            name="Pack 1",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )
        pack2 = KnowledgePack(
            id="pack2",
            name="Pack 2",
            description="Test",
            game_profile_id="game2",
            sources=[]
        )

        store.save_pack(pack1)
        store.save_pack(pack2)

        # Get packs for game1
        game1_packs = store.get_packs_for_game("game1")
        assert len(game1_packs) == 1
        assert "pack1" in game1_packs


@pytest.mark.unit
class TestKnowledgeIndex:
    """Test knowledge indexing and search"""

    def test_chunk_text(self, temp_dir):
        """Test text chunking"""
        from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding

        embedding_provider = SimpleTFIDFEmbedding()
        index = KnowledgeIndex(
            config_dir=temp_dir,
            embedding_provider=embedding_provider
        )

        text = "This is sentence one. This is sentence two. This is sentence three."
        chunks = index._chunk_text(text, chunk_size=30, overlap=10)

        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) > 0

    def test_add_and_query_pack(self, temp_dir):
        """Test adding and querying a knowledge pack"""
        from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
        from knowledge_pack import KnowledgePack, KnowledgeSource, RetrievedChunk
        from knowledge_store import get_knowledge_pack_store

        # Create index
        embedding_provider = SimpleTFIDFEmbedding()
        index = KnowledgeIndex(
            config_dir=temp_dir,
            embedding_provider=embedding_provider
        )

        # Create pack with content
        source = KnowledgeSource(
            id="s1",
            type="note",
            title="Build Guide",
            content="The best build for magic users is to focus on Intelligence stat and use Glintstone Sorcery."
        )

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="elden_ring",
            sources=[source]
        )

        # Save pack to store (required before indexing)
        store = get_knowledge_pack_store()
        store.save_pack(pack)

        # Add to index
        index.add_pack(pack)

        # Query
        results = index.query(
            game_profile_id="elden_ring",
            question="What is the best magic build?",
            top_k=3
        )

        # Should find relevant chunks
        assert len(results) > 0
        assert isinstance(results[0], RetrievedChunk)

    def test_remove_pack(self, temp_dir):
        """Test removing a pack from index"""
        from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
        from knowledge_pack import KnowledgePack, KnowledgeSource

        embedding_provider = SimpleTFIDFEmbedding()
        index = KnowledgeIndex(
            config_dir=temp_dir,
            embedding_provider=embedding_provider
        )

        # Add pack
        source = KnowledgeSource(
            id="s1",
            type="note",
            title="Note",
            content="Test content"
        )

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[source]
        )

        index.add_pack(pack)

        # Remove pack
        index.remove_pack("pack1")

        # Query should return nothing
        results = index.query(
            game_profile_id="game1",
            question="test",
            top_k=3
        )
        assert len(results) == 0

    def test_index_persistence_after_restart(self, temp_dir):
        """
        Test that TF-IDF model state persists across restarts.

        This is a critical regression test for the index corruption bug where
        the TF-IDF vocabulary was not being saved, causing search results to
        become random garbage after restarting the application.
        """
        from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
        from knowledge_pack import KnowledgePack, KnowledgeSource
        from knowledge_store import KnowledgePackStore

        # Create knowledge store
        store = KnowledgePackStore(config_dir=temp_dir)

        # Create pack with distinctive content
        source = KnowledgeSource(
            id="s1",
            type="note",
            title="Magic Build Guide",
            content="The best build for magic users is to focus on Intelligence stat and use Glintstone Sorcery. "
                   "You should prioritize leveling Intelligence and Mind. Equip the Staff of Loss for bonus damage."
        )

        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test pack for persistence",
            game_profile_id="elden_ring",
            sources=[source]
        )

        # Save pack to store (required before indexing)
        store.save_pack(pack)

        # Create first index instance and index the pack
        embedding_provider1 = SimpleTFIDFEmbedding()
        index1 = KnowledgeIndex(
            config_dir=temp_dir,
            embedding_provider=embedding_provider1,
            knowledge_store=store
        )
        index1.add_pack(pack)

        # Query before "restart" to establish baseline
        results_before = index1.query(
            game_profile_id="elden_ring",
            question="What stats should I level for magic build?",
            top_k=3
        )

        # Should find relevant results
        assert len(results_before) > 0
        first_result_before = results_before[0]
        assert first_result_before.score > 0.1  # Should have decent similarity

        # Destroy the first index (simulate application shutdown)
        del index1
        del embedding_provider1

        # Create NEW index instance (simulate application restart)
        # This should load the persisted TF-IDF model from disk
        embedding_provider2 = SimpleTFIDFEmbedding()
        index2 = KnowledgeIndex(
            config_dir=temp_dir,
            embedding_provider=embedding_provider2,
            knowledge_store=store
        )

        # Query after "restart" with same question
        results_after = index2.query(
            game_profile_id="elden_ring",
            question="What stats should I level for magic build?",
            top_k=3
        )

        # Verify results are still valid (not random garbage)
        assert len(results_after) > 0
        first_result_after = results_after[0]

        # Results should be similar (TF-IDF model was loaded correctly)
        # The scores should be comparable (within 10% tolerance)
        assert abs(first_result_before.score - first_result_after.score) < 0.1

        # The same top result should be retrieved
        assert first_result_before.text == first_result_after.text

        # Verify the embedding provider has vocabulary loaded
        # Note: index2.embedding_provider is the loaded one, not embedding_provider2
        assert len(index2.embedding_provider.vocabulary) > 0
        assert len(index2.embedding_provider.idf) > 0


@pytest.mark.unit
class TestIngestion:
    """Test content ingestion"""

    def test_ingest_text_file(self, temp_dir):
        """Test ingesting a text file"""
        from knowledge_ingestion import IngestionPipeline

        pipeline = IngestionPipeline()

        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_content = "This is test content from a text file."
        test_file.write_text(test_content)

        # Ingest
        content = pipeline.ingest('file', file_path=str(test_file))
        assert content == test_content

    def test_ingest_note(self):
        """Test ingesting a note"""
        from knowledge_ingestion import IngestionPipeline

        pipeline = IngestionPipeline()

        note_content = "This is a test note."
        content = pipeline.ingest('note', content=note_content)
        assert content.strip() == note_content

    def test_ingest_batch(self, temp_dir):
        """Test batch ingestion"""
        from knowledge_ingestion import IngestionPipeline

        pipeline = IngestionPipeline()

        # Create test files
        file1 = Path(temp_dir) / "file1.txt"
        file1.write_text("Content 1")

        sources = [
            {'type': 'file', 'file_path': str(file1)},
            {'type': 'note', 'content': 'Note content'}
        ]

        results = pipeline.ingest_batch(sources)
        assert len(results) == 2
        assert results[0] is not None
        assert results[1] is not None


@pytest.mark.unit
class TestSessionLogger:
    """Test session logging"""

    def test_log_event(self, temp_dir):
        """Test logging an event"""
        from session_logger import SessionLogger

        logger = SessionLogger(config_dir=temp_dir)

        logger.log_event(
            game_profile_id="elden_ring",
            event_type="question",
            content="How do I beat Malenia?"
        )

        # Get events
        events = logger.get_current_session_events("elden_ring")
        assert len(events) == 1
        assert events[0].event_type == "question"

    def test_session_summary(self, temp_dir):
        """Test getting session summary"""
        from session_logger import SessionLogger

        logger = SessionLogger(config_dir=temp_dir)

        # Log some events
        for i in range(5):
            logger.log_event(
                game_profile_id="elden_ring",
                event_type="question",
                content=f"Question {i}"
            )

        summary = logger.get_session_summary("elden_ring")
        assert summary['total_events'] == 5
        assert summary['event_types']['question'] == 5

    def test_multiple_sessions(self, temp_dir):
        """Test handling multiple game profiles"""
        from session_logger import SessionLogger

        logger = SessionLogger(config_dir=temp_dir)

        logger.log_event(
            game_profile_id="game1",
            event_type="question",
            content="Q1"
        )

        logger.log_event(
            game_profile_id="game2",
            event_type="question",
            content="Q2"
        )

        events1 = logger.get_current_session_events("game1")
        events2 = logger.get_current_session_events("game2")

        assert len(events1) == 1
        assert len(events2) == 1
