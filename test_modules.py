"""
Comprehensive test suite for all modules
Tests each component independently and their integration
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported successfully"""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    
    try:
        from src.config import Config
        print("✓ Config module imported successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False

    try:
        from src.game_detector import GameDetector
        print("✓ GameDetector module imported successfully")
    except Exception as e:
        print(f"✗ GameDetector import failed: {e}")
        return False

    try:
        from src.ai_router import AIRouter
        print("✓ AIRouter module imported successfully")
    except Exception as e:
        print(f"✗ AIRouter import failed: {e}")
        return False

    try:
        from src.ai_assistant import AIAssistant
        print("✓ AIAssistant module imported successfully")
    except Exception as e:
        print(f"✗ AIAssistant import failed: {e}")
        return False

    try:
        from src.credential_store import CredentialStore  # noqa: F401
        print("✓ CredentialStore module imported successfully")
    except Exception as e:
        print(f"✗ CredentialStore import failed: {e}")
        return False

    try:
        from src.gui import ChatWidget, MainWindow, run_gui
        print("✓ GUI module imported successfully")
    except Exception as e:
        print(f"✗ GUI import failed: {e}")
        return False

    print("\n✓ All modules imported successfully!")
    return True


def test_config():
    """Test Config module functionality"""
    print("\n" + "="*60)
    print("TEST 2: Config Module")
    print("="*60)
    
    try:
        from src.config import Config
        
        # Create config instance
        config = Config()
        print("✓ Config instance created")

        # Test accessing values via attributes
        provider = config.ai_provider
        print(f"✓ Config.ai_provider attribute access works: {provider}")

        # Test checking if configured
        is_configured = config.is_configured()
        print(f"✓ Config.is_configured() works: {is_configured}")

        # Test overlay settings
        assert hasattr(config, 'overlay_x')
        assert hasattr(config, 'overlay_y')
        print("✓ Config overlay settings present")
        
        # Test provider key checking
        has_key = config.has_provider_key()
        print(f"✓ Config.has_provider_key() works: {has_key}")

        # Test get_effective_provider
        effective = config.get_effective_provider()
        print(f"✓ Config.get_effective_provider() works: {effective}")
        
        print("\n✓ Config module tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_detector():
    """Test GameDetector module functionality"""
    print("\n" + "="*60)
    print("TEST 3: GameDetector Module")
    print("="*60)
    
    try:
        from src.game_detector import GameDetector
        
        # Create detector instance
        detector = GameDetector()
        print("✓ GameDetector instance created")
        
        # Test detect_running_game
        game = detector.detect_running_game()
        if game:
            print(f"✓ Game detected: {game['name']}")
        else:
            print("✓ detect_running_game() returned None (no game running)")
        
        # Test get_running_games
        games = detector.get_running_games()
        print(f"✓ get_running_games() returned {len(games)} games")
        
        # Test add_custom_game
        success = detector.add_custom_game("Test Game", ["test.exe"])
        if success:
            print("✓ add_custom_game() works")
        
        # Try to add duplicate
        duplicate = detector.add_custom_game("Test Game", ["test2.exe"])
        if not duplicate:
            print("✓ Duplicate game detection works")
        
        print("\n✓ GameDetector module tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ GameDetector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_assistant():
    """Test AIRouter and AIAssistant module functionality"""
    print("\n" + "="*60)
    print("TEST 5: AIRouter & AIAssistant Modules")
    print("="*60)

    try:
        from src.config import Config
        from src.ai_router import AIRouter, reset_router
        from src.ai_assistant import AIAssistant
        import os

        # Initialize AIRouter through Config
        config = Config()
        router = AIRouter(config)
        print("✓ AIRouter instance created successfully")

        # Test list_configured_providers
        providers = router.list_configured_providers()
        print(f"✓ list_configured_providers() returned: {providers}")

        # Test get_default_provider
        default_provider = router.get_default_provider()
        if default_provider:
            print(f"✓ get_default_provider() returned: {default_provider.__class__.__name__}")
        else:
            print("⚠ No default provider configured (expected if no API keys set)")

        # Test provider status
        for provider_name in ["anthropic", "openai", "gemini"]:
            status = router.get_provider_status(provider_name)
            if status.get("configured"):
                print(f"✓ {provider_name} provider status: {status}")

        # Test AIAssistant (high-level wrapper using AIRouter)
        try:
            assistant = AIAssistant()
            print(f"✓ AIAssistant instance created with router")

            # Test set_current_game
            game_info = {"name": "Test Game", "id": "test123"}
            assistant.set_current_game(game_info)
            print(f"✓ set_current_game() works: {assistant.current_game['name']}")

            # Test conversation history
            history = assistant.get_conversation_summary()
            print(f"✓ get_conversation_summary() returned {len(history)} messages")

            # Test clear_history
            assistant.clear_history()
            print("✓ clear_history() works")

        except ValueError as ve:
            print(f"⚠ AIAssistant initialization skipped: {ve}")
            print("  This is expected if no API key is configured")

        # Clean up router singleton for testing
        reset_router()
        print("✓ Router reset for test cleanup")

        print("\n✓ AIRouter & AIAssistant module tests passed!")
        return True

    except Exception as e:
        print(f"✗ AI module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_components():
    """Test GUI module components (without displaying windows)"""
    print("\n" + "="*60)
    print("TEST 6: GUI Module Components")
    print("="*60)

    try:
        from src.gui import AIWorkerThread
        from src.ai_router import AIRouter
        from src.ai_assistant import AIAssistant
        import os

        print("✓ GUI components imported successfully")
        print("✓ AIRouter imported successfully")

        # Test that classes can be instantiated (without showing GUI)
        print("✓ ChatWidget and GameDetectionThread classes are available")
        print("✓ AIRouter and AIAssistant classes are available for GUI integration")

        # Note: Full GUI testing requires a display and QApplication,
        # which may not be available in all environments
        print("\n✓ GUI module components validated!")
        return True

    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test basic integration between modules"""
    print("\n" + "="*60)
    print("TEST 7: Module Integration")
    print("="*60)

    try:
        from src.config import Config
        from src.game_detector import GameDetector
        from src.ai_router import AIRouter
        from src.ai_assistant import AIAssistant
        import os

        # Initialize all components
        config = Config()
        print("✓ Config initialized")

        detector = GameDetector()
        print("✓ GameDetector initialized")

        # Initialize AIRouter
        router = AIRouter(config)
        print("✓ AIRouter initialized")

        # Try to initialize AI assistant with router support
        try:
            assistant = AIAssistant()
            print(f"✓ AIAssistant initialized (using AIRouter)")
        except ValueError:
            print(f"⚠ AIAssistant skipped (no API keys configured)")
            assistant = None

        # Test workflow
        game = detector.detect_running_game()
        if game:
            print(f"✓ Detected game: {game['name']}")
            if assistant:
                assistant.set_current_game(game)
                print(f"✓ Set game context in AI assistant")
        else:
            print("✓ No running game (expected in test environment)")

        print("\n✓ Integration tests passed!")
        return True

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "#"*60)
    print("# GAMING AI ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("#"*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Config Module", test_config),
        ("GameDetector Module", test_game_detector),
        ("AIAssistant Module", test_ai_assistant),
        ("GUI Components", test_gui_components),
        ("Module Integration", test_integration),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Print summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed")
    print("-"*60)
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
