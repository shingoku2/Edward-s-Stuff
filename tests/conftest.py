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

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def clean_config_dir(temp_dir):
    """Provide a clean config directory for tests"""
    config_dir = Path(temp_dir) / "config"
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
