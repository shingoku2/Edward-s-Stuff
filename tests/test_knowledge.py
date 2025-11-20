from pathlib import Path

import pytest

from knowledge_ingestion import FileIngestor, IngestionError
from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
from knowledge_pack import KnowledgePack, KnowledgeSource


@pytest.mark.unit
def test_ingest_file_valid_and_invalid_paths(tmp_path):
    downloads_dir = Path.home() / "Downloads" / "omnix_test"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    valid_file = downloads_dir / "notes.txt"
    valid_file.write_text("Use stealth to avoid detection.")

    content = FileIngestor.ingest_file(str(valid_file))
    assert "stealth" in content

    invalid_file = tmp_path / "outside.txt"
    invalid_file.write_text("not allowed")

    with pytest.raises(IngestionError):
        FileIngestor.ingest_file(str(invalid_file))


@pytest.mark.unit
def test_ingest_file_blocks_path_traversal(tmp_path):
    sneaky_dir = tmp_path / "nested"
    sneaky_dir.mkdir(parents=True, exist_ok=True)
    sneaky_file = sneaky_dir / "../escape.txt"
    sneaky_file.write_text("traverse")

    with pytest.raises(IngestionError):
        FileIngestor.ingest_file(str(sneaky_file))


@pytest.mark.unit
def test_knowledge_index_adds_and_queries_chunks(tmp_path):
    embedding_provider = SimpleTFIDFEmbedding()
    source = KnowledgeSource(
        id="s1",
        type="note",
        title="Boss Guide",
        content="Use fire damage on ice bosses for maximum effect.",
    )
    pack = KnowledgePack(
        id="p1",
        name="Test Pack",
        description="Pack for testing",
        game_profile_id="game1",
        sources=[source],
    )

    class StubStore:
        def get_packs_for_game(self, game_profile_id):
            if game_profile_id == pack.game_profile_id:
                return {pack.id: pack}
            return {}

    index = KnowledgeIndex(
        config_dir=str(tmp_path),
        embedding_provider=embedding_provider,
        knowledge_store=StubStore(),
    )

    index.add_pack(pack)
    results = index.query("game1", "ice bosses")

    assert results
    assert "fire damage" in results[0].text
    assert (Path(tmp_path) / "knowledge_index" / "index.json").exists()
