"""
Unit tests for game profile system

Tests game profile creation, management, storage, and matching.
"""
import pytest
from pathlib import Path


@pytest.mark.unit
class TestGameProfile:
    """Test GameProfile model"""

    def test_profile_creation(self):
        """Test creating a game profile"""
        from game_profile import GameProfile

        profile = GameProfile(
            id="test_game",
            display_name="Test Game",
            exe_names=["test.exe"],
            system_prompt="Test prompt",
            default_provider="anthropic",
            overlay_mode_default="compact"
        )
        assert profile.id == "test_game"
        assert profile.display_name == "Test Game"
        assert len(profile.exe_names) == 1
        assert profile.is_builtin is False

    def test_profile_serialization(self):
        """Test profile to_dict and from_dict"""
        from game_profile import GameProfile

        profile = GameProfile(
            id="test",
            display_name="Test",
            exe_names=["test.exe"],
            system_prompt="Prompt"
        )

        # Serialize
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict['id'] == 'test'

        # Deserialize
        restored = GameProfile.from_dict(profile_dict)
        assert restored.id == profile.id
        assert restored.display_name == profile.display_name

    def test_matches_executable(self):
        """Test executable name matching"""
        from game_profile import GameProfile

        profile = GameProfile(
            id="elden_ring",
            display_name="Elden Ring",
            exe_names=["eldenring.exe", "elden_ring.exe"],
            system_prompt="Prompt"
        )

        # Should match case-insensitively
        assert profile.matches_executable("eldenring.exe") is True
        assert profile.matches_executable("ELDENRING.EXE") is True
        assert profile.matches_executable("elden_ring.exe") is True
        assert profile.matches_executable("other.exe") is False

    def test_builtin_flag(self):
        """Test built-in profile flag"""
        from game_profile import GameProfile

        builtin = GameProfile(
            id="generic",
            display_name="Generic",
            exe_names=[],
            system_prompt="Prompt",
            is_builtin=True
        )
        custom = GameProfile(
            id="custom",
            display_name="Custom",
            exe_names=["custom.exe"],
            system_prompt="Prompt",
            is_builtin=False
        )

        assert builtin.is_builtin is True
        assert custom.is_builtin is False


@pytest.mark.unit
class TestGameProfileStore:
    """Test GameProfileStore"""

    def test_store_initialization(self):
        """Test creating a profile store"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        assert store is not None
        # Should have built-in profiles loaded
        assert len(store.list_profiles()) > 0

    def test_builtin_profiles_loaded(self):
        """Test that built-in profiles are loaded"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        profiles = store.list_profiles()
        builtin_ids = [p.id for p in profiles if p.is_builtin]

        assert "generic_game" in builtin_ids
        assert "elden_ring" in builtin_ids

    def test_get_profile_by_id(self):
        """Test retrieving profile by ID"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        profile = store.get_profile_by_id("elden_ring")

        assert profile is not None
        assert profile.id == "elden_ring"
        assert profile.display_name == "Elden Ring"

    def test_get_profile_by_executable(self):
        """Test retrieving profile by executable name"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        profile = store.get_profile_by_executable("eldenring.exe")

        assert profile is not None
        assert profile.id == "elden_ring"

    def test_unknown_executable_returns_generic(self):
        """Test that unknown executable returns generic profile"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        profile = store.get_profile_by_executable("unknown.exe")

        assert profile is not None
        assert profile.id == "generic_game"

    def test_create_custom_profile(self, temp_dir):
        """Test creating a custom profile"""
        from game_profile import GameProfileStore, GameProfile

        store = GameProfileStore()
        test_id = "test_custom_unique"

        # Clean up if exists
        if store.get_profile_by_id(test_id):
            store.delete_profile(test_id)

        profile = GameProfile(
            id=test_id,
            display_name="My Game",
            exe_names=["mygame.exe"],
            system_prompt="Custom prompt",
            is_builtin=False
        )

        success = store.create_profile(profile)
        assert success is True

        retrieved = store.get_profile_by_id(test_id)
        assert retrieved is not None
        assert retrieved.display_name == "My Game"

        # Cleanup
        store.delete_profile(test_id)

    def test_duplicate_profile_fails(self):
        """Test that creating duplicate profile fails"""
        from game_profile import GameProfileStore, GameProfile

        store = GameProfileStore()

        profile = GameProfile(
            id="dup_test_unique",
            display_name="Duplicate Test",
            exe_names=["dup.exe"],
            system_prompt="Prompt"
        )

        # Clean up if exists
        if store.get_profile_by_id("dup_test_unique"):
            store.delete_profile("dup_test_unique")

        # First create should succeed
        assert store.create_profile(profile) is True
        # Second create with same ID should fail
        assert store.create_profile(profile) is False

        # Cleanup
        store.delete_profile("dup_test_unique")

    def test_cannot_update_builtin(self):
        """Test that built-in profiles cannot be updated"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        generic = store.get_profile_by_id("generic_game")
        generic.system_prompt = "Modified prompt"

        success = store.update_profile(generic)
        assert success is False

    def test_cannot_delete_builtin(self):
        """Test that built-in profiles cannot be deleted"""
        from game_profile import GameProfileStore

        store = GameProfileStore()
        success = store.delete_profile("generic_game")

        assert success is False
        # Verify still exists
        assert store.get_profile_by_id("generic_game") is not None


@pytest.mark.unit
class TestOverlayModes:
    """Test overlay mode configuration"""

    def test_mode_validation(self):
        """Test mode validation"""
        from overlay_modes import OverlayModeConfig

        assert OverlayModeConfig.is_valid_mode("compact") is True
        assert OverlayModeConfig.is_valid_mode("full") is True
        assert OverlayModeConfig.is_valid_mode("invalid") is False

    def test_mode_config_retrieval(self):
        """Test retrieving mode configuration"""
        from overlay_modes import OverlayModeConfig

        config = OverlayModeConfig.get_mode_config("compact")
        assert config is not None
        assert config['display_name'] == 'Compact'

    def test_default_dimensions(self):
        """Test getting default dimensions"""
        from overlay_modes import OverlayModeConfig

        width, height = OverlayModeConfig.get_default_dimensions("compact")
        assert width > 0
        assert height > 0

        # Full mode should be larger
        full_width, full_height = OverlayModeConfig.get_default_dimensions("full")
        assert full_width > width
        assert full_height > height

    def test_visibility_settings(self):
        """Test visibility settings for modes"""
        from overlay_modes import OverlayModeConfig

        # Compact should not show full history
        assert OverlayModeConfig.should_show_conversation_history("compact") is False
        # Full should show history
        assert OverlayModeConfig.should_show_conversation_history("full") is True
