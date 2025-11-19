"""
Pytest configuration and fixtures for Omnix test suite

Provides common fixtures and configuration for all tests.
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path

# Ensure QT_QPA_PLATFORM is set before any Qt imports
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

# Set master password for credential store in test environments
# This allows tests to run in CI where system keyring is unavailable
os.environ.setdefault('OMNIX_MASTER_PASSWORD', 'test-master-password-for-ci')

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def clean_config_dir(temp_dir):
    """Provide a clean config directory for tests"""
    config_dir = temp_dir / "config"
    config_dir.mkdir(exist_ok=True)
    return str(config_dir)


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing"""
    return "sk-test-1234567890abcdef"


@pytest.fixture
def mock_game_profile():
    """Provide a test game profile"""
    from game_profile import GameProfile
    return GameProfile(
        id="test_game",
        display_name="Test Game",
        exe_names=["testgame.exe"],
        system_prompt="You are a test assistant",
        default_provider="anthropic"
    )


@pytest.fixture
def game_detector():
    """Provide a GameDetector instance"""
    from game_detector import GameDetector
    return GameDetector()


@pytest.fixture
def game_profile_store():
    """Provide a GameProfileStore instance"""
    from game_profile import GameProfileStore
    return GameProfileStore()


@pytest.fixture
def config(temp_dir):
    """Provide a test Config instance"""
    from config import Config
    config_path = temp_dir / "test_config.json"
    return Config(config_path=str(config_path), require_keys=False)


@pytest.fixture
def macro_store(temp_dir):
    """Provide a MacroStore instance"""
    from macro_store import MacroStore
    return MacroStore(str(temp_dir))


@pytest.fixture
def knowledge_pack_store(temp_dir):
    """Provide a KnowledgePackStore instance"""
    from knowledge_store import KnowledgePackStore
    return KnowledgePackStore(config_dir=str(temp_dir))


@pytest.fixture
def knowledge_index(temp_dir):
    """Provide a KnowledgeIndex instance"""
    from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
    embedding_provider = SimpleTFIDFEmbedding()
    return KnowledgeIndex(
        config_dir=str(temp_dir),
        embedding_provider=embedding_provider
    )


@pytest.fixture
def session_logger(temp_dir):
    """Provide a SessionLogger instance"""
    from session_logger import SessionLogger
    return SessionLogger(config_dir=str(temp_dir))


@pytest.fixture
def sample_knowledge_pack():
    """Provide a sample knowledge pack for testing"""
    from knowledge_pack import KnowledgePack, KnowledgeSource

    source = KnowledgeSource(
        id="sample_source",
        type="note",
        title="Sample Note",
        content="This is sample content for testing knowledge packs."
    )

    return KnowledgePack(
        id="sample_pack",
        name="Sample Pack",
        description="A sample knowledge pack for testing",
        game_profile_id="test_game",
        sources=[source]
    )


@pytest.fixture
def sample_macro():
    """Provide a sample macro for testing"""
    from macro_manager import Macro, MacroStep, MacroStepType

    return Macro(
        id="sample_macro",
        name="Sample Macro",
        description="A sample macro for testing",
        steps=[
            MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"),
            MacroStep(type=MacroStepType.DELAY.value, duration_ms=100),
            MacroStep(type=MacroStepType.KEY_PRESS.value, key="b")
        ]
    )
