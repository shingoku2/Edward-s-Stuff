"""
Test helper functions and utilities

Provides common utilities used across multiple test files.
"""
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional


def create_test_config_file(config_dir: str, config_data: Optional[Dict[str, Any]] = None) -> Path:
    """
    Create a test configuration file

    Args:
        config_dir: Directory to create config file in
        config_data: Optional configuration data to write

    Returns:
        Path to the created config file
    """
    config_path = Path(config_dir) / "test_config.json"

    if config_data is None:
        config_data = {
            "ai_provider": "anthropic",
            "overlay_x": 100,
            "overlay_y": 100,
            "overlay_width": 800,
            "overlay_height": 600
        }

    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

    return config_path


def create_temp_text_file(directory: str, filename: str, content: str) -> Path:
    """
    Create a temporary text file for testing

    Args:
        directory: Directory to create file in
        filename: Name of the file
        content: Content to write to file

    Returns:
        Path to the created file
    """
    file_path = Path(directory) / filename
    file_path.write_text(content)
    return file_path


def cleanup_test_profile(store, profile_id: str):
    """
    Clean up a test game profile if it exists

    Args:
        store: GameProfileStore instance
        profile_id: ID of the profile to clean up
    """
    from game_profile import GameProfileStore

    if isinstance(store, GameProfileStore):
        profile = store.get_profile_by_id(profile_id)
        if profile and not profile.is_builtin:
            store.delete_profile(profile_id)


def has_any_api_key() -> bool:
    """
    Check if any API key is configured

    Returns:
        True if at least one API key is available
    """
    return any([
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("GEMINI_API_KEY")
    ])


def is_headless_environment() -> bool:
    """
    Check if running in a headless environment

    Returns:
        True if running in CI/headless environment
    """
    return bool(
        os.getenv("CI")
        or os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("HEADLESS_TEST")
        or (os.name != "nt" and not os.getenv("DISPLAY"))
    )


def assert_valid_game_profile(profile):
    """
    Assert that a game profile has all required fields

    Args:
        profile: GameProfile instance to validate
    """
    assert profile is not None
    assert hasattr(profile, 'id')
    assert hasattr(profile, 'display_name')
    assert hasattr(profile, 'exe_names')
    assert hasattr(profile, 'system_prompt')
    assert hasattr(profile, 'default_provider')
    assert isinstance(profile.exe_names, list)


def assert_valid_macro(macro):
    """
    Assert that a macro has all required fields

    Args:
        macro: Macro instance to validate
    """
    assert macro is not None
    assert hasattr(macro, 'id')
    assert hasattr(macro, 'name')
    assert hasattr(macro, 'description')
    assert hasattr(macro, 'steps')
    assert isinstance(macro.steps, list)


def assert_valid_knowledge_pack(pack):
    """
    Assert that a knowledge pack has all required fields

    Args:
        pack: KnowledgePack instance to validate
    """
    assert pack is not None
    assert hasattr(pack, 'id')
    assert hasattr(pack, 'name')
    assert hasattr(pack, 'description')
    assert hasattr(pack, 'game_profile_id')
    assert hasattr(pack, 'sources')
    assert isinstance(pack.sources, list)


def normalize_line_endings(text: str) -> str:
    """
    Normalize line endings to LF

    Args:
        text: Text to normalize

    Returns:
        Text with normalized line endings
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def strip_ansi_codes(text: str) -> str:
    """
    Strip ANSI color codes from text

    Args:
        text: Text with potential ANSI codes

    Returns:
        Text without ANSI codes
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
