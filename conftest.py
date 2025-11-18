"""
Pytest configuration and shared fixtures for Omnix Gaming Companion tests.

This file is automatically discovered by pytest and provides fixtures
that are available to all test files.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Generator
from unittest.mock import Mock, MagicMock

import pytest

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


# ============================================================================
# Session-scoped fixtures (run once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "tests" / "data"


# ============================================================================
# Function-scoped fixtures (run for each test)
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Provide a temporary directory that is cleaned up after the test.

    Usage:
        def test_something(temp_dir):
            file_path = temp_dir / "test.txt"
            file_path.write_text("content")
    """
    tmpdir = tempfile.mkdtemp()
    try:
        yield Path(tmpdir)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def temp_config_dir(temp_dir) -> Path:
    """Provide a temporary config directory for testing."""
    config_dir = temp_dir / ".gaming_ai_assistant"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def mock_config(temp_config_dir):
    """
    Provide a mock Config instance with safe defaults.

    Usage:
        def test_something(mock_config):
            assert mock_config.ai_provider == "anthropic"
    """
    from src.config import Config

    # Create config with temp directory
    config = Config(config_dir=str(temp_config_dir))

    # Set safe test defaults
    config.ai_provider = "anthropic"
    config.check_interval = 5
    config.overlay_hotkey = "ctrl+shift+g"

    return config


@pytest.fixture
def mock_game_detector():
    """
    Provide a GameDetector instance for testing.

    Usage:
        def test_detection(mock_game_detector):
            detector = mock_game_detector
            game = detector.detect_running_game()
    """
    from src.game_detector import GameDetector
    return GameDetector()


@pytest.fixture
def mock_game_process():
    """
    Provide a mock game process for testing.

    Usage:
        def test_game(mock_game_process):
            assert mock_game_process.name == "eldenring.exe"
    """
    mock = MagicMock()
    mock.name.return_value = "eldenring.exe"
    mock.pid = 12345
    mock.is_running.return_value = True
    return mock


@pytest.fixture
def mock_game_profile():
    """
    Provide a mock GameProfile for testing.

    Usage:
        def test_profile(mock_game_profile):
            assert mock_game_profile.id == "elden_ring"
    """
    from src.game_profile import GameProfile

    return GameProfile(
        id="elden_ring",
        display_name="Elden Ring",
        exe_names=["eldenring.exe"],
        system_prompt="You are an expert Elden Ring guide.",
        default_provider="anthropic",
        overlay_mode_default="full"
    )


@pytest.fixture
def mock_ai_provider():
    """
    Provide a mock AI provider for testing.

    Usage:
        def test_ai(mock_ai_provider):
            response = await mock_ai_provider.chat([...])
            assert response["content"]
    """
    mock = MagicMock()
    mock.name = "mock_provider"
    mock.is_configured.return_value = True

    # Mock chat method
    async def mock_chat(messages, **kwargs):
        return {
            "content": "This is a test response.",
            "model": "test-model",
            "usage": {"total_tokens": 100}
        }

    mock.chat = mock_chat

    # Mock test_connection
    def mock_test():
        return type('Health', (), {'healthy': True, 'message': 'OK'})()

    mock.test_connection = mock_test

    return mock


@pytest.fixture
def mock_credential_store(temp_config_dir):
    """
    Provide a CredentialStore with temporary storage.

    Usage:
        def test_creds(mock_credential_store):
            mock_credential_store.set_credential("service", "key", "value")
    """
    from src.credential_store import CredentialStore

    # Use temp directory for credential storage
    return CredentialStore(config_dir=str(temp_config_dir))


@pytest.fixture
def sample_macro():
    """
    Provide a sample macro for testing.

    Usage:
        def test_macro(sample_macro):
            assert len(sample_macro.steps) > 0
    """
    from src.macro_manager import Macro, MacroStep, MacroStepType

    return Macro(
        id="test_macro",
        name="Test Macro",
        description="A test macro",
        steps=[
            MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"),
            MacroStep(type=MacroStepType.DELAY.value, duration_ms=100),
            MacroStep(type=MacroStepType.KEY_PRESS.value, key="b")
        ]
    )


@pytest.fixture
def sample_knowledge_pack():
    """
    Provide a sample knowledge pack for testing.

    Usage:
        def test_knowledge(sample_knowledge_pack):
            assert len(sample_knowledge_pack.sources) > 0
    """
    from src.knowledge_pack import KnowledgePack, KnowledgeSource

    source = KnowledgeSource(
        id="test_source",
        type="note",
        title="Test Note",
        content="This is test content about game mechanics."
    )

    return KnowledgePack(
        id="test_pack",
        name="Test Pack",
        description="A test knowledge pack",
        game_profile_id="elden_ring",
        sources=[source]
    )


@pytest.fixture
def sample_session_events():
    """
    Provide sample session events for testing.

    Usage:
        def test_session(sample_session_events):
            assert len(sample_session_events) > 0
    """
    from src.session_logger import SessionEvent
    from datetime import datetime

    return [
        SessionEvent(
            timestamp=datetime.now(),
            event_type="question",
            game_profile_id="elden_ring",
            content="How do I beat Margit?",
            meta={}
        ),
        SessionEvent(
            timestamp=datetime.now(),
            event_type="answer",
            game_profile_id="elden_ring",
            content="Use ranged attacks and summon help.",
            meta={"tokens": 50}
        )
    ]


# ============================================================================
# Qt/GUI fixtures
# ============================================================================

@pytest.fixture(scope="session")
def qapp():
    """
    Provide a QApplication instance for GUI tests.

    This is session-scoped to avoid creating multiple QApplication instances.

    Usage:
        @pytest.mark.ui
        def test_gui(qapp):
            from PyQt6.QtWidgets import QPushButton
            button = QPushButton("Test")
            assert button.text() == "Test"
    """
    from PyQt6.QtWidgets import QApplication
    import sys

    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    yield app

    # Cleanup is handled automatically by pytest-qt


@pytest.fixture
def qtbot(qapp, request):
    """
    Provide QtBot for Qt widget testing.

    Usage:
        @pytest.mark.ui
        def test_button_click(qtbot):
            from PyQt6.QtWidgets import QPushButton
            button = QPushButton("Click me")
            qtbot.addWidget(button)

            with qtbot.waitSignal(button.clicked):
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    """
    try:
        from pytestqt.qtbot import QtBot
        bot = QtBot(request)
        yield bot
    except ImportError:
        pytest.skip("pytest-qt not installed")


# ============================================================================
# Mocking fixtures
# ============================================================================

@pytest.fixture
def mock_keyring():
    """
    Mock the keyring module to avoid actual system keyring usage.

    Usage:
        def test_something(mock_keyring):
            # keyring operations will be mocked
            pass
    """
    import keyring
    from unittest.mock import patch

    with patch('keyring.get_password') as mock_get, \
         patch('keyring.set_password') as mock_set, \
         patch('keyring.delete_password') as mock_del:

        # Store in-memory credentials
        credentials = {}

        def set_password(service, username, password):
            credentials[f"{service}:{username}"] = password

        def get_password(service, username):
            return credentials.get(f"{service}:{username}")

        def delete_password(service, username):
            key = f"{service}:{username}"
            if key in credentials:
                del credentials[key]

        mock_set.side_effect = set_password
        mock_get.side_effect = get_password
        mock_del.side_effect = delete_password

        yield {
            'get': mock_get,
            'set': mock_set,
            'delete': mock_del
        }


@pytest.fixture
def mock_psutil():
    """
    Mock psutil for game detection testing without actual processes.

    Usage:
        def test_detection(mock_psutil):
            # psutil.process_iter() will return mock processes
            pass
    """
    from unittest.mock import patch, MagicMock

    with patch('psutil.process_iter') as mock_iter:
        # Create mock processes
        mock_process = MagicMock()
        mock_process.info = {'name': 'eldenring.exe', 'pid': 12345}
        mock_process.name.return_value = 'eldenring.exe'

        mock_iter.return_value = [mock_process]

        yield mock_iter


# ============================================================================
# Environment fixtures
# ============================================================================

@pytest.fixture
def clean_env():
    """
    Provide a clean environment without API keys for testing.

    Usage:
        def test_no_keys(clean_env):
            # No API keys in environment
            assert "ANTHROPIC_API_KEY" not in os.environ
    """
    original_env = os.environ.copy()

    # Remove API keys
    keys_to_remove = [
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'GEMINI_API_KEY',
    ]

    for key in keys_to_remove:
        os.environ.pop(key, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def test_api_keys():
    """
    Provide test API keys (fake) for testing.

    Usage:
        def test_with_keys(test_api_keys):
            assert os.environ["ANTHROPIC_API_KEY"]
    """
    original_env = os.environ.copy()

    # Set fake API keys
    os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-key-12345'
    os.environ['OPENAI_API_KEY'] = 'sk-test-key-12345'
    os.environ['GEMINI_API_KEY'] = 'test-gemini-key-12345'

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Markers and hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Ensure Qt platform is set for headless testing
    if 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'


def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.

    This automatically skips certain tests in CI environments.
    """
    skip_in_ci = pytest.mark.skip(reason="Skipped in CI environment")

    for item in items:
        # Skip tests marked with skip_ci in CI
        if "skip_ci" in item.keywords and os.environ.get("CI"):
            item.add_marker(skip_in_ci)

        # Skip tests requiring API keys if not available
        if "requires_api_key" in item.keywords:
            has_key = any([
                os.environ.get("ANTHROPIC_API_KEY"),
                os.environ.get("OPENAI_API_KEY"),
                os.environ.get("GEMINI_API_KEY")
            ])
            if not has_key:
                item.add_marker(pytest.mark.skip(reason="No API keys available"))
