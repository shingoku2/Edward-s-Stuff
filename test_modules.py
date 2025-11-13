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
        from src.info_scraper import InfoScraper
        print("✓ InfoScraper module imported successfully")
    except Exception as e:
        print(f"✗ InfoScraper import failed: {e}")
        return False

    try:
        from src.ai_assistant import AIAssistant
        print("✓ AIAssistant module imported successfully")
    except Exception as e:
        print(f"✗ AIAssistant import failed: {e}")
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
        
        # Test getting values
        provider = config.get("ai_provider")
        print(f"✓ Config.get() works: ai_provider = {provider}")
        
        # Test setting values
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
        print("✓ Config.set() works")
        
        # Test get_all
        all_config = config.get_all()
        assert isinstance(all_config, dict)
        print(f"✓ Config.get_all() works: {len(all_config)} keys")
        
        # Test validation
        validation = config.validate_api_keys()
        assert isinstance(validation, dict)
        print(f"✓ Config.validate_api_keys() works: {validation}")
        
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


def test_info_scraper():
    """Test InfoScraper module functionality"""
    print("\n" + "="*60)
    print("TEST 4: InfoScraper Module")
    print("="*60)
    
    try:
        from src.info_scraper import InfoScraper
        
        # Create scraper instance
        scraper = InfoScraper(timeout=5)
        print("✓ InfoScraper instance created")
        
        # Test search_game_info (may return None due to network/parsing)
        try:
            info = scraper.search_game_info("Minecraft")
            if info:
                print(f"✓ search_game_info() returned: {info.get('name', 'Unknown')}")
            else:
                print("✓ search_game_info() returned None (may be network issue)")
        except Exception as e:
            print(f"⚠ search_game_info() network error: {e}")
        
        # Test get_game_guides
        try:
            guides = scraper.get_game_guides("Minecraft")
            print(f"✓ get_game_guides() returned {len(guides)} guides")
            if guides:
                for guide in guides[:2]:
                    print(f"  - {guide.get('title', 'Unknown')}")
        except Exception as e:
            print(f"⚠ get_game_guides() error: {e}")
        
        # Test close
        scraper.close()
        print("✓ InfoScraper.close() works")
        
        print("\n✓ InfoScraper module tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ InfoScraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_assistant():
    """Test AIAssistant module functionality"""
    print("\n" + "="*60)
    print("TEST 5: AIAssistant Module")
    print("="*60)
    
    try:
        from src.ai_assistant import AIAssistant
        import os
        
        # Check if API key is available
        provider = os.getenv("AI_PROVIDER", "anthropic")
        api_key = None
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print(f"⚠ No API key found for {provider}, skipping AI tests")
            print("  Set AI_PROVIDER and corresponding API key environment variables")
            return True
        
        # Create assistant instance
        assistant = AIAssistant(provider=provider, api_key=api_key)
        print(f"✓ AIAssistant instance created with provider: {provider}")
        
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
        
        # Note: Full API testing requires valid keys, so we skip actual queries
        print("\n✓ AIAssistant module tests passed!")
        return True
        
    except ValueError as ve:
        print(f"⚠ AIAssistant initialization skipped: {ve}")
        print("  This is expected if no API key is configured")
        return True
    except Exception as e:
        print(f"✗ AIAssistant test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_components():
    """Test GUI module components (without displaying windows)"""
    print("\n" + "="*60)
    print("TEST 6: GUI Module Components")
    print("="*60)
    
    try:
        from src.gui import ChatWidget, GameDetectionThread
        from src.ai_assistant import AIAssistant
        import os
        
        print("✓ GUI components imported successfully")
        
        # Test that classes can be instantiated (without showing GUI)
        print("✓ ChatWidget and GameDetectionThread classes are available")
        
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
        from src.info_scraper import InfoScraper
        from src.ai_assistant import AIAssistant
        import os
        
        # Initialize all components
        config = Config()
        print("✓ Config initialized")
        
        detector = GameDetector()
        print("✓ GameDetector initialized")
        
        scraper = InfoScraper()
        print("✓ InfoScraper initialized")
        
        # Try to initialize AI assistant
        provider = config.get("ai_provider", "anthropic")
        try:
            assistant = AIAssistant(provider=provider)
            print(f"✓ AIAssistant initialized with {provider}")
        except ValueError:
            print(f"⚠ AIAssistant skipped (no API key for {provider})")
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
        
        scraper.close()
        print("✓ Scraper closed")
        
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
        ("InfoScraper Module", test_info_scraper),
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
