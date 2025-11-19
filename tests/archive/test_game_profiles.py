"""
Unit tests for game profile system
Tests game detection, profile resolution, and copilot core functionality
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from game_profile import GameProfile, GameProfileStore, get_profile_store
from game_detector import GameDetector
from overlay_modes import OverlayMode, OverlayModeConfig, ModeTransitionHelper


class TestGameProfile(unittest.TestCase):
    """Test GameProfile model"""

    def test_profile_creation(self):
        """Test creating a game profile"""
        profile = GameProfile(
            id="test_game",
            display_name="Test Game",
            exe_names=["test.exe"],
            system_prompt="Test prompt",
            default_provider="anthropic",
            overlay_mode_default="compact"
        )
        self.assertEqual(profile.id, "test_game")
        self.assertEqual(profile.display_name, "Test Game")
        self.assertEqual(len(profile.exe_names), 1)
        self.assertFalse(profile.is_builtin)

    def test_profile_to_dict(self):
        """Test profile serialization to dict"""
        profile = GameProfile(
            id="test",
            display_name="Test",
            exe_names=["test.exe"],
            system_prompt="Prompt",
        )
        profile_dict = profile.to_dict()
        self.assertIsInstance(profile_dict, dict)
        self.assertEqual(profile_dict['id'], 'test')
        self.assertEqual(profile_dict['display_name'], 'Test')

    def test_profile_from_dict(self):
        """Test profile deserialization from dict"""
        data = {
            'id': 'test',
            'display_name': 'Test',
            'exe_names': ['test.exe'],
            'system_prompt': 'Prompt',
            'default_provider': 'anthropic',
            'default_model': None,
            'overlay_mode_default': 'compact',
            'extra_settings': {},
            'is_builtin': False
        }
        profile = GameProfile.from_dict(data)
        self.assertEqual(profile.id, 'test')
        self.assertEqual(profile.display_name, 'Test')

    def test_matches_executable(self):
        """Test executable name matching"""
        profile = GameProfile(
            id="elden_ring",
            display_name="Elden Ring",
            exe_names=["eldenring.exe", "elden_ring.exe"],
            system_prompt="Prompt"
        )
        self.assertTrue(profile.matches_executable("eldenring.exe"))
        self.assertTrue(profile.matches_executable("ELDENRING.EXE"))  # Case insensitive
        self.assertTrue(profile.matches_executable("elden_ring.exe"))
        self.assertFalse(profile.matches_executable("other.exe"))

    def test_builtin_profile_flag(self):
        """Test built-in profile flag"""
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
        self.assertTrue(builtin.is_builtin)
        self.assertFalse(custom.is_builtin)


class TestGameProfileStore(unittest.TestCase):
    """Test GameProfileStore"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.path.expanduser("~")
        # Don't actually change home for these tests, just use temp dir

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_store_creation(self):
        """Test creating a profile store"""
        store = GameProfileStore()
        self.assertIsNotNone(store)
        self.assertGreater(len(store.list_profiles()), 0)

    def test_builtin_profiles_loaded(self):
        """Test that built-in profiles are loaded"""
        store = GameProfileStore()
        profiles = store.list_profiles()
        builtin_ids = [p.id for p in profiles if p.is_builtin]
        self.assertIn("generic_game", builtin_ids)
        self.assertIn("elden_ring", builtin_ids)

    def test_get_profile_by_id(self):
        """Test retrieving profile by ID"""
        store = GameProfileStore()
        profile = store.get_profile_by_id("elden_ring")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.id, "elden_ring")
        self.assertEqual(profile.display_name, "Elden Ring")

    def test_get_profile_by_executable(self):
        """Test retrieving profile by executable name"""
        store = GameProfileStore()
        profile = store.get_profile_by_executable("eldenring.exe")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.id, "elden_ring")

    def test_unknown_executable_returns_generic(self):
        """Test that unknown executable returns generic profile"""
        store = GameProfileStore()
        profile = store.get_profile_by_executable("unknown.exe")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.id, "generic_game")

    def test_create_custom_profile(self):
        """Test creating a custom profile"""
        store = GameProfileStore()

        # Use unique ID to avoid conflicts with other tests
        test_id = "test_custom_game_001"

        # Clean up if it exists from a previous test
        if store.get_profile_by_id(test_id):
            store.delete_profile(test_id)

        profile = GameProfile(
            id=test_id,
            display_name="My Game",
            exe_names=["mygame001.exe"],
            system_prompt="Custom prompt",
            is_builtin=False
        )
        success = store.create_profile(profile)
        self.assertTrue(success)
        retrieved = store.get_profile_by_id(test_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.display_name, "My Game")

        # Clean up
        store.delete_profile(test_id)

    def test_create_duplicate_profile_fails(self):
        """Test that creating duplicate profile fails"""
        store = GameProfileStore()

        # Clean up if profile exists from previous run
        if store.get_profile_by_id("dup_test"):
            store.delete_profile("dup_test")

        profile1 = GameProfile(
            id="dup_test",
            display_name="Duplicate Test",
            exe_names=["dup.exe"],
            system_prompt="Prompt"
        )
        self.assertTrue(store.create_profile(profile1))
        # Try to create another with same ID
        self.assertFalse(store.create_profile(profile1))

        # Clean up after test
        store.delete_profile("dup_test")

    def test_update_profile(self):
        """Test updating a custom profile"""
        store = GameProfileStore()
        profile = GameProfile(
            id="update_test",
            display_name="Update Test",
            exe_names=["test.exe"],
            system_prompt="Original prompt"
        )
        store.create_profile(profile)

        # Update it
        profile.system_prompt = "Updated prompt"
        profile.overlay_mode_default = "full"
        success = store.update_profile(profile)
        self.assertTrue(success)

        # Verify update
        retrieved = store.get_profile_by_id("update_test")
        self.assertEqual(retrieved.system_prompt, "Updated prompt")
        self.assertEqual(retrieved.overlay_mode_default, "full")

    def test_cannot_update_builtin_profile(self):
        """Test that built-in profiles cannot be updated"""
        store = GameProfileStore()
        generic = store.get_profile_by_id("generic_game")
        generic.system_prompt = "Modified prompt"
        success = store.update_profile(generic)
        self.assertFalse(success)

    def test_delete_profile(self):
        """Test deleting a custom profile"""
        store = GameProfileStore()
        profile = GameProfile(
            id="delete_test",
            display_name="Delete Test",
            exe_names=["test.exe"],
            system_prompt="Prompt"
        )
        store.create_profile(profile)
        self.assertIsNotNone(store.get_profile_by_id("delete_test"))

        success = store.delete_profile("delete_test")
        self.assertTrue(success)
        self.assertIsNone(store.get_profile_by_id("delete_test"))

    def test_cannot_delete_builtin_profile(self):
        """Test that built-in profiles cannot be deleted"""
        store = GameProfileStore()
        success = store.delete_profile("generic_game")
        self.assertFalse(success)
        # Verify it still exists
        self.assertIsNotNone(store.get_profile_by_id("generic_game"))

    def test_duplicate_profile(self):
        """Test duplicating a profile"""
        store = GameProfileStore()

        # Clean up if profile exists from previous run
        if store.get_profile_by_id("elden_ring_custom"):
            store.delete_profile("elden_ring_custom")

        original = store.get_profile_by_id("elden_ring")
        success = store.duplicate_profile(
            "elden_ring",
            "elden_ring_custom",
            "Elden Ring Custom"
        )
        self.assertTrue(success)
        duplicate = store.get_profile_by_id("elden_ring_custom")
        self.assertIsNotNone(duplicate)
        self.assertEqual(duplicate.display_name, "Elden Ring Custom")
        self.assertEqual(duplicate.system_prompt, original.system_prompt)

        # Clean up after test
        store.delete_profile("elden_ring_custom")

    def test_list_custom_profiles(self):
        """Test listing only custom profiles"""
        store = GameProfileStore()
        # Create a custom profile
        profile = GameProfile(
            id="custom_profile",
            display_name="Custom Profile",
            exe_names=["custom.exe"],
            system_prompt="Prompt"
        )
        store.create_profile(profile)

        custom_profiles = store.list_custom_profiles()
        custom_ids = [p.id for p in custom_profiles]
        self.assertIn("custom_profile", custom_ids)
        self.assertNotIn("generic_game", custom_ids)


class TestGameDetector(unittest.TestCase):
    """Test game detection"""

    def test_detector_creation(self):
        """Test creating a game detector"""
        detector = GameDetector()
        self.assertIsNotNone(detector)
        self.assertGreater(len(detector.common_games), 0)

    def test_known_games_attribute(self):
        """Test legacy KNOWN_GAMES attribute exists"""
        detector = GameDetector()
        self.assertTrue(hasattr(detector, 'KNOWN_GAMES'))
        self.assertIsInstance(detector.KNOWN_GAMES, dict)

    def test_add_custom_game(self):
        """Test adding a custom game"""
        detector = GameDetector()
        success = detector.add_custom_game(
            "My Custom Game",
            ["custom.exe", "custom2.exe"]
        )
        self.assertTrue(success)
        self.assertIn("My Custom Game", detector.common_games)

    def test_cannot_add_duplicate_game_name(self):
        """Test that duplicate game names are rejected"""
        detector = GameDetector()
        # Try to add duplicate of existing game (case-insensitive)
        success = detector.add_custom_game(
            "Elden Ring",  # Already exists
            ["different.exe"]
        )
        self.assertFalse(success)

    def test_cannot_add_duplicate_process(self):
        """Test that duplicate processes are rejected"""
        detector = GameDetector()
        # Try to use a process that's already tracked
        success = detector.add_custom_game(
            "Another Game",
            ["eldenring.exe"]  # Already tracked for Elden Ring
        )
        self.assertFalse(success)


class TestOverlayModes(unittest.TestCase):
    """Test overlay mode configuration"""

    def test_mode_validation(self):
        """Test mode validation"""
        self.assertTrue(OverlayModeConfig.is_valid_mode("compact"))
        self.assertTrue(OverlayModeConfig.is_valid_mode("full"))
        self.assertFalse(OverlayModeConfig.is_valid_mode("invalid"))

    def test_mode_config_retrieval(self):
        """Test retrieving mode configuration"""
        config = OverlayModeConfig.get_mode_config("compact")
        self.assertIsNotNone(config)
        self.assertEqual(config['display_name'], 'Compact')

    def test_default_dimensions(self):
        """Test getting default dimensions"""
        width, height = OverlayModeConfig.get_default_dimensions("compact")
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

        full_width, full_height = OverlayModeConfig.get_default_dimensions("full")
        # Full mode should be larger
        self.assertGreater(full_width, width)
        self.assertGreater(full_height, height)

    def test_min_dimensions(self):
        """Test getting minimum dimensions"""
        width, height = OverlayModeConfig.get_min_dimensions("compact")
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

    def test_visibility_settings(self):
        """Test visibility settings for modes"""
        # Compact mode should not show full history
        self.assertFalse(OverlayModeConfig.should_show_conversation_history("compact"))
        # Full mode should show history
        self.assertTrue(OverlayModeConfig.should_show_conversation_history("full"))

    def test_list_modes(self):
        """Test listing available modes"""
        modes = OverlayModeConfig.list_modes()
        self.assertIn("compact", modes)
        self.assertIn("full", modes)
        self.assertEqual(len(modes), 2)

    def test_mode_transition(self):
        """Test mode transition helper"""
        # Expanding from compact to full
        new_width, new_height = ModeTransitionHelper.calculate_new_size(
            500, 120, "compact", "full"
        )
        self.assertGreater(new_width, 500)
        self.assertGreater(new_height, 120)

    def test_position_preservation(self):
        """Test that position is preserved during transitions"""
        preserve = ModeTransitionHelper.should_preserve_position("compact", "full")
        self.assertTrue(preserve)

    def test_transition_message(self):
        """Test transition messages"""
        msg = ModeTransitionHelper.get_transition_message("compact", "full")
        self.assertIn("full", msg.lower())
        self.assertGreater(len(msg), 0)


class TestProfileIntegration(unittest.TestCase):
    """Integration tests for game profiles"""

    def setUp(self):
        """Set up test fixtures"""
        self.store = GameProfileStore()
        # Clean up any existing test profile
        if self.store.get_profile_by_id("my_game_test"):
            self.store.delete_profile("my_game_test")

    def tearDown(self):
        """Clean up after tests"""
        # Remove test profile if it exists
        if self.store.get_profile_by_id("my_game_test"):
            self.store.delete_profile("my_game_test")

    def test_profile_to_game_integration(self):
        """Test profile integration with game detection"""
        detector = GameDetector()
        store = GameProfileStore()

        # Detect a known game profile
        profile = store.get_profile_by_executable("eldenring.exe")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.id, "elden_ring")

    def test_custom_profile_resolution(self):
        """Test that custom profiles can be resolved"""
        # Create custom profile with unique ID
        profile = GameProfile(
            id="my_game_test",
            display_name="My Game Test",
            exe_names=["mygame_test.exe"],
            system_prompt="Custom AI behavior"
        )
        self.store.create_profile(profile)

        # Resolve it by executable
        resolved = self.store.get_profile_by_executable("mygame_test.exe")
        self.assertEqual(resolved.id, "my_game_test")
        self.assertEqual(resolved.system_prompt, "Custom AI behavior")

    def test_profile_executable_matching_case_insensitive(self):
        """Test that executable matching is case-insensitive"""
        store = GameProfileStore()
        profile = store.get_profile_by_executable("ELDENRING.EXE")
        self.assertEqual(profile.id, "elden_ring")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_empty_executable_list(self):
        """Test profile with empty executable list"""
        profile = GameProfile(
            id="generic",
            display_name="Generic",
            exe_names=[],
            system_prompt="Matches any game"
        )
        # Should not match anything specifically, but generic profiles
        # are OK with empty exe_names
        self.assertFalse(profile.matches_executable("test.exe"))

    def test_none_executable_matching(self):
        """Test matching with None or invalid input"""
        profile = GameProfile(
            id="test",
            display_name="Test",
            exe_names=["test.exe"],
            system_prompt="Prompt"
        )
        # These should not crash
        self.assertFalse(profile.matches_executable(""))

    def test_overlay_mode_edge_cases(self):
        """Test overlay mode edge cases"""
        # Invalid mode should return compact config
        config = OverlayModeConfig.get_mode_config("invalid_mode")
        # Should have some fallback
        self.assertIsNotNone(config)

    def test_profile_store_persistence(self):
        """Test that profile store can be created multiple times"""
        store1 = GameProfileStore()
        profiles1 = len(store1.list_profiles())

        # Create another store
        store2 = GameProfileStore()
        profiles2 = len(store2.list_profiles())

        # Both should have same built-in profiles
        self.assertGreater(profiles1, 0)
        self.assertGreaterEqual(profiles2, profiles1)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGameProfile))
    suite.addTests(loader.loadTestsFromTestCase(TestGameProfileStore))
    suite.addTests(loader.loadTestsFromTestCase(TestGameDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestOverlayModes))
    suite.addTests(loader.loadTestsFromTestCase(TestProfileIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
