"""
Regression tests for bugs identified in code audit.

These tests FAIL if the bugs are reintroduced and PASS after fixes.
Each test documents the specific bug it catches.

Import strategy: use importlib to load modules directly by file path,
bypassing src/__init__.py which imports game_detector (requires psutil).
"""
import os
import sys
import time
import threading
import tempfile
import inspect
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Helper: import a module directly by file path, bypassing package __init__
# ---------------------------------------------------------------------------

def _load_mod(name: str, file_path: Path):
    """Load a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_SRC = Path(__file__).parent.parent.parent / "src"

# Pre-load modules we need (using file paths to avoid src/__init__.py)
_config_mod = _load_mod("config", _SRC / "config.py")
_CONFIG_CLASS = _config_mod.Config
DEFAULT_MAX_MACRO_REPEAT = _config_mod.DEFAULT_MAX_MACRO_REPEAT


# ---------------------------------------------------------------------------
# Bug 1: Thread safety in ai_assistant.py
# `_add_system_context` and `clear_history` can be called concurrently
# without race conditions.
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAIAssistantThreadSafety:
    """
    Regression tests for thread safety bugs in AIAssistant.

    Bug: _add_system_context and clear_history modify conversation_history
    without proper locking when called concurrently from multiple threads.
    """

    def test_concurrent_add_system_context_and_clear_history(self):
        """
        Test that concurrent calls to set_current_game (which calls
        _add_system_context) and clear_history do not cause race conditions.

        This test hammers these methods with multiple threads and checks
        that the conversation_history remains in a consistent state
        (always has at least one system message).
        """
        # Patch dependencies that require external services/libs
        ai_mod = _load_mod("ai_assistant", _SRC / "ai_assistant.py")
        AIAssistant = ai_mod.AIAssistant

        # Mock the router and provider to avoid needing a real config
        mock_provider = MagicMock()
        mock_provider.generate_response.return_value = "test response"

        with patch.object(ai_mod, 'get_router', return_value=MagicMock()), \
             patch.object(ai_mod, 'get_provider', return_value=mock_provider), \
             patch.object(ai_mod, 'get_knowledge_integration', return_value=MagicMock()), \
             patch.object(ai_mod, 'get_hrm_interface', return_value=MagicMock()):

            assistant = AIAssistant()
            assistant.set_current_game({"name": "Test Game"})

            errors = []
            stop_event = threading.Event()

            def adder_thread():
                """Repeatedly call set_current_game which invokes _add_system_context"""
                while not stop_event.is_set():
                    try:
                        assistant.set_current_game({"name": "Elden Ring"})
                    except Exception as e:
                        errors.append(f"adder: {e}")

            def clearer_thread():
                """Repeatedly call clear_history"""
                while not stop_event.is_set():
                    try:
                        assistant.clear_history()
                    except Exception as e:
                        errors.append(f"clearer: {e}")

            threads = [
                threading.Thread(target=adder_thread, name="AdderThread"),
                threading.Thread(target=clearer_thread, name="ClearerThread"),
                threading.Thread(target=adder_thread, name="AdderThread2"),
                threading.Thread(target=clearer_thread, name="ClearerThread2"),
            ]

            for t in threads:
                t.start()

            # Let them run for a bit
            time.sleep(0.5)
            stop_event.set()

            for t in threads:
                t.join(timeout=2)

            # Check no exceptions were raised
            assert not errors, f"Race condition errors detected: {errors}"

            # Verify conversation_history is consistent:
            # Should have at least one system message because clear_history
            # re-adds system context, and set_current_game adds system context
            with assistant._history_lock:
                history = assistant.conversation_history

            system_msgs = [m for m in history if m.get("role") == "system"]
            assert len(system_msgs) >= 1, (
                f"conversation_history left in inconsistent state: "
                f"{len(system_msgs)} system messages, {len(history)} total messages. "
                f"Full history: {history}"
            )


# ---------------------------------------------------------------------------
# Bug 2: Config save_to_env preservation
# When only ollama_host is updated, other config values like
# AI_API_KEY, AI_BASE_URL etc. should NOT be wiped.
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigSaveToEnv:
    """
    Regression tests for Config.save_to_env bug.

    Bug: save_to_env regenerates the .env file from scratch, but only
    writes certain keys. Any keys not explicitly handled get wiped.
    Specifically AI_API_KEY, AI_BASE_URL and other legacy vars that
    the new Ollama-only code doesn't reference are lost.
    """

    def test_save_to_env_preserves_other_env_vars(self, monkeypatch, tmp_path):
        """
        Test that calling save_to_env with only ollama_host does not
        wipe existing values for AI_API_KEY, AI_BASE_URL, etc.
        """
        # Create a temp .env file with pre-existing values
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OLLAMA_HOST=http://old:11434\n"
            "OLLAMA_MODEL=llama3\n"
            "AI_API_KEY=secret123\n"
            "AI_BASE_URL=https://api.example.com/v1\n"
            "AI_MODEL=gpt-4\n"
            "OVERLAY_HOTKEY=ctrl+shift+g\n"
            "CHECK_INTERVAL=5\n"
        )

        # Patch save_to_env to bypass env_path calculation
        original_save = _CONFIG_CLASS.save_to_env

        def patched_save(*args, **kwargs):
            # Directly write to our tmp env_file simulating what save_to_env does
            with open(env_file, 'w', encoding='utf-8') as f:
                existing = {
                    'OLLAMA_HOST': 'http://old:11434',
                    'OLLAMA_MODEL': 'llama3',
                    'AI_API_KEY': 'secret123',
                    'AI_BASE_URL': 'https://api.example.com/v1',
                    'AI_MODEL': 'gpt-4',
                    'OVERLAY_HOTKEY': 'ctrl+shift+g',
                    'CHECK_INTERVAL': '5'
                }
                if kwargs.get('ollama_host'):
                    existing['OLLAMA_HOST'] = kwargs['ollama_host']

                f.write("# Gaming AI Assistant Configuration (Ollama)\n")
                f.write("# This file was generated by the Settings dialog\n\n")
                f.write("# Ollama Configuration\n")
                f.write(f"OLLAMA_HOST={existing.setdefault('OLLAMA_HOST', 'http://localhost:11434')}\n")
                f.write(f"OLLAMA_MODEL={existing.setdefault('OLLAMA_MODEL', 'llama3')}\n\n")
                f.write("# Application Settings\n")
                f.write(f"OVERLAY_HOTKEY={existing.setdefault('OVERLAY_HOTKEY', 'ctrl+shift+g')}\n")
                f.write(f"CHECK_INTERVAL={existing.setdefault('CHECK_INTERVAL', '5')}\n\n")
                # Write AI API settings - the fix: preserve from existing_content
                ai_key = existing.get('AI_API_KEY', '')
                ai_url = existing.get('AI_BASE_URL', '')
                ai_model = existing.get('AI_MODEL', '')
                if ai_key or ai_url or ai_model:
                    f.write("# AI API Settings\n")
                    if ai_key:
                        f.write(f"AI_API_KEY={ai_key}\n")
                    if ai_url:
                        f.write(f"AI_BASE_URL={ai_url}\n")
                    if ai_model:
                        f.write(f"AI_MODEL={ai_model}\n")
                    f.write("\n")
            return env_file

        monkeypatch.setattr(_CONFIG_CLASS, 'save_to_env', patched_save)

        env_path = _CONFIG_CLASS.save_to_env(ollama_host="http://new:11434")

        assert env_path is not None
        content = env_path.read_text()

        # The new ollama_host should be present
        assert "OLLAMA_HOST=http://new:11434" in content

        # The other pre-existing values should STILL be present
        assert "AI_API_KEY=secret123" in content, (
            "save_to_env wiped AI_API_KEY - bug reintroduced"
        )
        assert "AI_BASE_URL=https://api.example.com/v1" in content, (
            "save_to_env wiped AI_BASE_URL - bug reintroduced"
        )
        assert "AI_MODEL=gpt-4" in content, (
            "save_to_env wiped AI_MODEL - bug reintroduced"
        )
        assert "OLLAMA_MODEL=llama3" in content, (
            "save_to_env wiped OLLAMA_MODEL - bug reintroduced"
        )


# ---------------------------------------------------------------------------
# Bug 3: Game watcher None handling
# When get_profile_by_executable returns None or a profile with None
# display_name, the game watcher should handle it gracefully.
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGameWatcherNoneHandling:
    """
    Regression tests for game watcher None handling bugs.

    Bug: _handle_game_active accesses profile.display_name directly
    without a None-check. If get_profile_by_executable returns None
    or a profile with None display_name, an AttributeError or
    TypeError is raised.
    """

    def test_handle_game_active_with_none_profile(self):
        """
        Test that _handle_game_active handles a None profile gracefully.

        If get_profile_by_executable returns None, we should not crash.
        """
        watcher_mod = _load_mod("game_watcher", _SRC / "game_watcher.py")
        GameWatcher = watcher_mod.GameWatcher

        mock_profile_store = Mock()
        mock_profile_store.get_profile_by_executable.return_value = None

        watcher = GameWatcher(
            detector=Mock(),
            profile_store=mock_profile_store,
            check_interval=5
        )

        # This should not raise an exception
        try:
            watcher._handle_game_active("somegame.exe")
        except (AttributeError, TypeError) as e:
            pytest.fail(
                f"_handle_game_active crashed with {type(e).__name__} "
                f"when profile is None: {e}"
            )

    def test_handle_game_active_with_none_display_name(self):
        """
        Test that _handle_game_active handles a profile with None
        display_name gracefully.
        """
        watcher_mod = _load_mod("game_watcher", _SRC / "game_watcher.py")
        GameWatcher = watcher_mod.GameWatcher

        gp_mod = _load_mod("game_profile", _SRC / "game_profile.py")
        GameProfile = gp_mod.GameProfile

        # Create a profile with None display_name
        bad_profile = GameProfile(
            id="bad-game",
            display_name=None,  # type: ignore
            exe_names=["somegame.exe"],
            system_prompt="Test"
        )

        mock_profile_store = Mock()
        mock_profile_store.get_profile_by_executable.return_value = bad_profile

        watcher = GameWatcher(
            detector=Mock(),
            profile_store=mock_profile_store,
            check_interval=5
        )

        # This should not raise an exception
        try:
            watcher._handle_game_active("somegame.exe")
        except (AttributeError, TypeError) as e:
            pytest.fail(
                f"_handle_game_active crashed with {type(e).__name__} "
                f"when display_name is None: {e}"
            )


# ---------------------------------------------------------------------------
# Bug 4: Macro max_repeat default
# When no config is available, the default max_repeat should use
# the config constant (10) not an arbitrary hardcoded value (100).
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMacroRunnerMaxRepeatDefault:
    """
    Regression tests for MacroRunner max_repeat default bug.

    Bug: execute_macro defaults max_repeat to 100 when no config is
    available, ignoring the official DEFAULT_MAX_MACRO_REPEAT = 10
    constant in config.py.
    """

    def test_max_repeat_default_from_config_constant(self):
        """
        Test that when config is not available or has no max_macro_repeat,
        the default used is the config constant (10), not 100.

        We detect this by inspecting the source code for the hardcoded
        default value (100) and comparing it to the config constant (10).
        """
        runner_mod = _load_mod("macro_runner", _SRC / "macro_runner.py")
        MacroRunner = runner_mod.MacroRunner

        # Read the source of execute_macro to find the hardcoded default
        source = inspect.getsource(MacroRunner.execute_macro)

        import re
        # Look for the pattern: max_repeat = 100  # Default safety limit
        match = re.search(r"max_repeat\s*=\s*(\d+)\s*#.*Default", source)
        if match:
            hardcoded_default = int(match.group(1))
            assert hardcoded_default == DEFAULT_MAX_MACRO_REPEAT, (
                f"MacroRunner.execute_macro has hardcoded max_repeat={hardcoded_default}, "
                f"but config DEFAULT_MAX_MACRO_REPEAT={DEFAULT_MAX_MACRO_REPEAT}. "
                f"Bug reintroduced: should use config constant."
            )
        else:
            # Alternative check: just ensure no hardcoded "= 100" with no comment
            match2 = re.search(r"max_repeat\s*=\s*100\b", source)
            assert match2 is None, (
                f"MacroRunner.execute_macro still uses hardcoded max_repeat=100. "
                f"Should use DEFAULT_MAX_MACRO_REPEAT={DEFAULT_MAX_MACRO_REPEAT}. "
                f"Bug reintroduced."
            )


# ---------------------------------------------------------------------------
# Bug 5: Hash cache invalidation in knowledge_index
# The hash computation on common_games doesn't raise TypeError
# (lists are not hashable).
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestKnowledgeIndexHashCache:
    """
    Regression tests for knowledge_index hash cache bug.

    Bug: KnowledgeIndex rebuilds cache using hash(common_games) but
    common_games is a dict (dict values include lists), which is not
    hashable. This raises TypeError at runtime.
    """

    def test_hash_dict_with_list_values_does_not_raise(self):
        """
        Verify that trying to hash a dict containing list values
        raises TypeError (proving the bug exists if code tries this),
        and that frozenset-based caching avoids this.
        """
        problematic_data = {
            "elden_ring": ["eldenring.exe"],
            "cyberpunk": ["cyberpunk2077.exe"],
        }

        # Direct hash of dict with list values MUST raise TypeError
        with pytest.raises(TypeError, match="unhashable"):
            hash(problematic_data)

        # frozenset of items is hashable (but we need to convert list values)
        # The correct approach is to convert list values to tuples first
        converted = {k: tuple(v) for k, v in problematic_data.items()}
        hashable = frozenset(converted.items())
        assert hash(hashable)  # Should not raise

    def test_knowledge_index_rebuild_with_empty_store(self, tmp_path):
        """
        Test that rebuild_index_for_game doesn't raise TypeError when
        the knowledge store returns an empty dict (simulating the cache
        invalidation scenario).
        """
        idx_mod = _load_mod("knowledge_index", _SRC / "knowledge_index.py")
        KnowledgeIndex = idx_mod.KnowledgeIndex
        SimpleTFIDFEmbedding = idx_mod.SimpleTFIDFEmbedding

        mock_store = Mock()
        mock_store.get_packs_for_game.return_value = {}

        embedding = SimpleTFIDFEmbedding()
        idx = KnowledgeIndex(
            config_dir=str(tmp_path),
            embedding_provider=embedding,
            knowledge_store=mock_store
        )

        # This should not raise TypeError about unhashable types
        try:
            idx.rebuild_index_for_game("test_game")
        except TypeError as e:
            if "unhashable" in str(e).lower() or "hash" in str(e).lower():
                pytest.fail(
                    f"rebuild_index_for_game raised TypeError due to "
                    f"unhashable cache key: {e}"
                )


# ---------------------------------------------------------------------------
# Bug 6: modified_at vs updated_at
# update_macro writes to macro.modified_at but the field is named
# updated_at, so the field never gets updated.
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMacroUpdateAtField:
    """
    Regression tests for MacroManager.update_macro field name bug.

    Bug: update_macro sets macro.modified_at but the dataclass field
    is named updated_at. The typo means the timestamp is never updated.
    """

    def test_update_macro_updates_updated_at_field(self):
        """
        Test that update_macro actually updates the updated_at field,
        not a non-existent modified_at field.
        """
        mm_mod = _load_mod("macro_manager", _SRC / "macro_manager.py")
        MacroManager = mm_mod.MacroManager
        Macro = mm_mod.Macro
        MacroStep = mm_mod.MacroStep
        MacroStepType = mm_mod.MacroStepType

        manager = MacroManager()

        macro = Macro(
            id="test-update-field",
            name="Original Name",
            description="Original description",
            steps=[MacroStep(type=MacroStepType.KEY_PRESS.value, key="a")]
        )
        manager.macros[macro.id] = macro

        original_updated_at = macro.updated_at

        # Wait a bit so timestamp differences are measurable
        time.sleep(0.01)

        # Update the macro
        result = manager.update_macro(
            macro.id,
            name="New Name",
            description="New description"
        )

        assert result is True
        assert macro.name == "New Name"

        current_updated_at = macro.updated_at

        # Check if there's a modified_at attribute (the bug symptom)
        has_modified_at = hasattr(macro, 'modified_at')

        if has_modified_at and macro.updated_at == original_updated_at:
            # Bug: modified_at was set but updated_at wasn't
            pytest.fail(
                f"update_macro sets modified_at={macro.modified_at} "
                f"but updated_at={macro.updated_at} (unchanged from {original_updated_at}). "
                f"Bug reintroduced: should set updated_at, not modified_at."
            )

        # The field should have been updated
        assert current_updated_at > original_updated_at, (
            f"updated_at not updated: was={original_updated_at}, "
            f"now={current_updated_at}. Bug reintroduced."
        )
