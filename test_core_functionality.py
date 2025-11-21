#!/usr/bin/env python3
"""
Test core functionality of the Gaming AI Assistant
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_game_detector():
    """Test game detection system"""
    print("Testing Game Detector...")
    from game_detector import GameDetector

    detector = GameDetector()
    assert len(detector.common_games) > 0, "No games configured"
    print(f"  ✓ {len(detector.common_games)} games configured")

    # Test detection (will return None if no games running)
    game = detector.detect_running_game()
    if game:
        print(f"  ✓ Detected running game: {game.get('name')}")
    else:
        print("  ℹ No games currently running")

def test_game_profiles():
    """Test game profile system"""
    print("\nTesting Game Profiles...")
    from game_profile import get_profile_store

    profile_store = get_profile_store()
    profiles = profile_store.list_profiles()
    assert isinstance(profiles, list), "Profile list was not returned"
    print(f"  ✓ {len(profiles)} game profiles available")

    # Test getting a profile
    if profiles:
        profile = profile_store.get_profile_by_id(profiles[0])
        assert profile is not None, "Failed to load profile"
        print(f"  ✓ Loaded profile: {profile.display_name}")

def test_config_system():
    """Test configuration management"""
    print("\nTesting Configuration System...")
    from config import Config

    config = Config(require_keys=False)
    print(f"  ✓ AI Provider: {config.ai_provider}")
    print(f"  ✓ Hotkey: {config.overlay_hotkey}")
    print(f"  ✓ Check interval: {config.check_interval}s")

def test_credential_store():
    """Test credential storage"""
    print("\nTesting Credential Store...")
    # Set a master password for the test environment
    import os
    os.environ['OMNIX_MASTER_PASSWORD'] = 'test_password_for_testing_only'

    from credential_store import CredentialStore

    store = CredentialStore()
    print("  ✓ Credential store initialized")

    # Test set/get/delete
    test_key = "test_service"
    test_name = "test_key"
    test_value = "test_value_123"

    store.set_credential(test_key, test_name, test_value)
    retrieved = store.get_credential(test_key, test_name)
    assert retrieved == test_value, "Value mismatch"
    print("  ✓ Set/Get credential working")

    store.delete_credential(test_key, test_name)
    deleted = store.get_credential(test_key, test_name)
    assert deleted is None, "Credential not deleted"
    print("  ✓ Delete credential working")

def test_knowledge_system():
    """Test knowledge pack system"""
    print("\nTesting Knowledge System...")
    from knowledge_store import get_knowledge_pack_store
    from knowledge_index import get_knowledge_index

    store = get_knowledge_pack_store()
    print("  ✓ Knowledge store initialized")

    index = get_knowledge_index()
    print("  ✓ Knowledge index initialized")
    assert index is not None, "Knowledge index was not created"

    packs = store.list_packs()
    assert isinstance(packs, list), "Knowledge packs not returned as list"
    print(f"  ✓ {len(packs)} knowledge packs available")

def test_macro_system():
    """Test macro management system"""
    print("\nTesting Macro System...")
    from macro_manager import MacroManager
    from macro_runner import MacroRunner

    manager = MacroManager()
    print("  ✓ Macro manager initialized")

    runner = MacroRunner(enabled=False)
    print("  ✓ Macro runner initialized")
    assert runner is not None, "Macro runner failed to initialize"

    macros = manager.get_all_macros()
    assert isinstance(macros, list), "Macros were not returned as a list"
    print(f"  ✓ {len(macros)} macros configured")

def test_ui_components():
    """Test UI component system"""
    print("\nTesting UI Components...")
    from ui.design_system import design_system
    from ui.tokens import COLORS, TYPOGRAPHY, SPACING
    from ui.components import OmnixIconButton, OmnixLineEdit

    print("  ✓ Design system loaded")
    print(f"  ✓ Color tokens available: {type(COLORS).__name__}")
    print(f"  ✓ Typography tokens available: {type(TYPOGRAPHY).__name__}")
    print(f"  ✓ Spacing tokens available: {type(SPACING).__name__}")

    # Test component imports
    assert OmnixIconButton is not None and OmnixLineEdit is not None, "UI components missing"
    print("  ✓ UI components available")

def test_gui_creation():
    """Test GUI window creation"""
    print("\nTesting GUI Creation...")
    from PyQt6.QtWidgets import QApplication
    from config import Config
    from credential_store import CredentialStore
    from ui.design_system import design_system
    from gui import MainWindow

    app = QApplication(sys.argv)
    config = Config(require_keys=False)
    credential_store = CredentialStore()

    window = MainWindow(
        ai_assistant=None,
        config=config,
        credential_store=credential_store,
        design_system=design_system
    )
    print("  ✓ Main window created")

    # Check key components exist
    assert hasattr(window, 'chat_panel'), "Missing chat_panel"
    assert hasattr(window, 'game_status_panel'), "Missing game_status_panel"
    assert hasattr(window, 'overlay_window'), "Missing overlay_window"
    print("  ✓ All UI panels present")

    # Clean up
    window.cleanup()
    app.quit()

if __name__ == "__main__":
    print("=" * 70)
    print("Gaming AI Assistant - Core Functionality Test")
    print("=" * 70)
    print()

    tests = [
        ("Config System", test_config_system),
        ("Credential Store", test_credential_store),
        ("Game Detector", test_game_detector),
        ("Game Profiles", test_game_profiles),
        ("Knowledge System", test_knowledge_system),
        ("Macro System", test_macro_system),
        ("UI Components", test_ui_components),
        ("GUI Creation", test_gui_creation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result is False:
                failed += 1
            else:
                passed += 1
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} total")
    print("=" * 70)

    if failed == 0:
        print("\n✓ All core functionality tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {failed} test(s) failed")
        sys.exit(1)
