"""
Unit tests for the Knowledge Pack & Coaching system
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime

# Import modules to test
from src.knowledge_pack import KnowledgeSource, KnowledgePack, RetrievedChunk
from src.knowledge_store import KnowledgePackStore, get_knowledge_pack_store
from src.knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
from src.knowledge_ingestion import IngestionPipeline, FileIngestor, NoteIngestor
from src.session_logger import SessionLogger, SessionEvent


class TestKnowledgeModels(unittest.TestCase):
    """Test knowledge pack data models"""

    def test_knowledge_source_creation(self):
        """Test creating a knowledge source"""
        source = KnowledgeSource(
            id="test_source",
            type="note",
            title="Test Note",
            content="This is test content"
        )

        self.assertEqual(source.id, "test_source")
        self.assertEqual(source.type, "note")
        self.assertTrue(source.validate())

    def test_knowledge_source_validation(self):
        """Test source validation"""
        # Valid file source
        file_source = KnowledgeSource(
            id="file1",
            type="file",
            title="File",
            path="/path/to/file.txt"
        )
        self.assertTrue(file_source.validate())

        # Invalid file source (no path)
        invalid_file = KnowledgeSource(
            id="file2",
            type="file",
            title="File"
        )
        self.assertFalse(invalid_file.validate())

    def test_knowledge_pack_creation(self):
        """Test creating a knowledge pack"""
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

        self.assertEqual(pack.id, "pack1")
        self.assertEqual(len(pack.sources), 1)
        self.assertTrue(pack.enabled)

    def test_knowledge_pack_add_remove_source(self):
        """Test adding and removing sources from a pack"""
        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="A test pack",
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
        self.assertEqual(pack.get_source_count(), 1)

        # Remove source
        pack.remove_source("s1")
        self.assertEqual(pack.get_source_count(), 0)

    def test_knowledge_pack_serialization(self):
        """Test pack to_dict and from_dict"""
        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )

        # Convert to dict
        pack_dict = pack.to_dict()
        self.assertEqual(pack_dict['id'], 'pack1')

        # Convert back from dict
        pack2 = KnowledgePack.from_dict(pack_dict)
        self.assertEqual(pack2.id, pack.id)
        self.assertEqual(pack2.name, pack.name)


class TestKnowledgeStore(unittest.TestCase):
    """Test knowledge pack store"""

    def setUp(self):
        """Create temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.store = KnowledgePackStore(config_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_save_and_load_pack(self):
        """Test saving and loading a pack"""
        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )

        # Save
        success = self.store.save_pack(pack)
        self.assertTrue(success)

        # Load
        loaded_pack = self.store.load_pack("pack1")
        self.assertIsNotNone(loaded_pack)
        self.assertEqual(loaded_pack.id, "pack1")
        self.assertEqual(loaded_pack.name, "Test Pack")

    def test_delete_pack(self):
        """Test deleting a pack"""
        pack = KnowledgePack(
            id="pack1",
            name="Test Pack",
            description="Test",
            game_profile_id="game1",
            sources=[]
        )

        # Save and delete
        self.store.save_pack(pack)
        success = self.store.delete_pack("pack1")
        self.assertTrue(success)

        # Verify deleted
        loaded_pack = self.store.load_pack("pack1")
        self.assertIsNone(loaded_pack)

    def test_get_packs_for_game(self):
        """Test filtering packs by game profile"""
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

        self.store.save_pack(pack1)
        self.store.save_pack(pack2)

        # Get packs for game1
        game1_packs = self.store.get_packs_for_game("game1")
        self.assertEqual(len(game1_packs), 1)
        self.assertIn("pack1", game1_packs)


class TestKnowledgeIndex(unittest.TestCase):
    """Test knowledge index"""

    def setUp(self):
        """Create temporary directory and index"""
        self.test_dir = tempfile.mkdtemp()
        self.embedding_provider = SimpleTFIDFEmbedding()
        self.index = KnowledgeIndex(
            config_dir=self.test_dir,
            embedding_provider=self.embedding_provider
        )

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_chunk_text(self):
        """Test text chunking"""
        text = "This is sentence one. This is sentence two. This is sentence three."
        chunks = self.index._chunk_text(text, chunk_size=30, overlap=10)

        self.assertGreater(len(chunks), 0)
        # Verify chunks have content
        for chunk in chunks:
            self.assertGreater(len(chunk), 0)

    def test_add_and_query_pack(self):
        """Test adding a pack and querying it"""
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

        # Save pack to store first (required before indexing)
        store = get_knowledge_pack_store()
        store.save_pack(pack)

        # Add to index
        self.index.add_pack(pack)

        # Query
        results = self.index.query(
            game_profile_id="elden_ring",
            question="What is the best magic build?",
            top_k=3
        )

        # Should find relevant chunks
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], RetrievedChunk)

    def test_remove_pack(self):
        """Test removing a pack from index"""
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

        self.index.add_pack(pack)

        # Remove pack
        self.index.remove_pack("pack1")

        # Query should return nothing
        results = self.index.query(
            game_profile_id="game1",
            question="test",
            top_k=3
        )
        self.assertEqual(len(results), 0)


class TestIngestion(unittest.TestCase):
    """Test ingestion pipeline"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.pipeline = IngestionPipeline()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_ingest_text_file(self):
        """Test ingesting a text file"""
        # Create test file
        test_file = Path(self.test_dir) / "test.txt"
        test_content = "This is test content from a text file."
        test_file.write_text(test_content)

        # Ingest
        content = self.pipeline.ingest('file', file_path=str(test_file))
        self.assertEqual(content, test_content)

    def test_ingest_note(self):
        """Test ingesting a note"""
        note_content = "This is a test note."
        content = self.pipeline.ingest('note', content=note_content)
        self.assertEqual(content.strip(), note_content)

    def test_ingest_batch(self):
        """Test batch ingestion"""
        # Create test files
        file1 = Path(self.test_dir) / "file1.txt"
        file1.write_text("Content 1")

        sources = [
            {'type': 'file', 'file_path': str(file1)},
            {'type': 'note', 'content': 'Note content'}
        ]

        results = self.pipeline.ingest_batch(sources)
        self.assertEqual(len(results), 2)
        self.assertIsNotNone(results[0])
        self.assertIsNotNone(results[1])


class TestSessionLogger(unittest.TestCase):
    """Test session logger"""

    def setUp(self):
        """Create temporary directory and logger"""
        self.test_dir = tempfile.mkdtemp()
        self.logger = SessionLogger(config_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_log_event(self):
        """Test logging an event"""
        self.logger.log_event(
            game_profile_id="elden_ring",
            event_type="question",
            content="How do I beat Malenia?"
        )

        # Get events
        events = self.logger.get_current_session_events("elden_ring")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "question")

    def test_session_summary(self):
        """Test getting session summary"""
        # Log some events
        for i in range(5):
            self.logger.log_event(
                game_profile_id="elden_ring",
                event_type="question",
                content=f"Question {i}"
            )

        summary = self.logger.get_session_summary("elden_ring")
        self.assertEqual(summary['total_events'], 5)
        self.assertEqual(summary['event_types']['question'], 5)

    def test_multiple_sessions(self):
        """Test handling multiple game profiles"""
        self.logger.log_event(
            game_profile_id="game1",
            event_type="question",
            content="Q1"
        )

        self.logger.log_event(
            game_profile_id="game2",
            event_type="question",
            content="Q2"
        )

        events1 = self.logger.get_current_session_events("game1")
        events2 = self.logger.get_current_session_events("game2")

        self.assertEqual(len(events1), 1)
        self.assertEqual(len(events2), 1)


if __name__ == '__main__':
    unittest.main()
