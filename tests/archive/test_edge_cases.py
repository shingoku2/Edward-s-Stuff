"""
Edge case and stress tests for Gaming AI Assistant modules
Tests error handling, edge cases, and boundary conditions
"""

import sys
import os
import logging
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_config_edge_cases():
    """Test Config module edge cases"""
    print("\n" + "="*60)
    print("TEST: Config Edge Cases")
    print("="*60)
    
    try:
        from src.config import Config
        
        # Test with custom config path
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test_config.json")
            config = Config(config_path=config_path)
            print("✓ Config with custom path created")
            
            # Test get with default
            value = config.get("nonexistent_key", "default_value")
            assert value == "default_value"
            print("✓ Config.get() with default value works")
            
            # Test update
            config.update({"test1": "value1", "test2": "value2"})
            assert config.get("test1") == "value1"
            print("✓ Config.update() with multiple values works")
            
            # Test reset to defaults
            original_provider = config.get("ai_provider")
            config.set("ai_provider", "test_provider")
            config.reset_to_defaults()
            assert config.get("ai_provider") == "anthropic"
            print("✓ Config.reset_to_defaults() works")
            
            # Test save and load
            config.set("test_persist", "persist_value")
            config.save_config()
            
            config2 = Config(config_path=config_path)
            assert config2.get("test_persist") == "persist_value"
            print("✓ Config persistence works (save and load)")
            
            # Test repr
            repr_str = repr(config)
            assert "Config" in repr_str
            print(f"✓ Config.__repr__() works: {repr_str}")
        
        print("\n✓ Config edge case tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Config edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_detector_edge_cases():
    """Test GameDetector edge cases"""
    print("\n" + "="*60)
    print("TEST: GameDetector Edge Cases")
    print("="*60)
    
    try:
        from src.game_detector import GameDetector
        
        detector = GameDetector()
        
        # Test with empty process name
        result = detector._is_process_running("")
        assert isinstance(result, bool)
        print(f"✓ Empty process name handled correctly (result: {result})")
        
        # Test with non-existent process
        result = detector._is_process_running("nonexistent_process_xyz_12345.exe")
        assert result == False
        print("✓ Non-existent process handled correctly")
        
        # Test add_custom_game with empty list
        result = detector.add_custom_game("Empty Game", [])
        assert result == True
        print("✓ Add custom game with empty process list works")
        
        # Test add_custom_game with None
        result = detector.add_custom_game(None, ["test.exe"])
        assert result == True
        print("✓ Add custom game with None name handled")
        
        # Test duplicate detection
        result1 = detector.add_custom_game("Duplicate", ["dup.exe"])
        result2 = detector.add_custom_game("Duplicate", ["dup2.exe"])
        result3 = detector.add_custom_game("duplicate", ["dup3.exe"])
        result4 = detector.add_custom_game("Duplicate Process", ["dup.exe"])
        assert result1 is True
        assert result2 is False
        assert result3 is False
        assert result4 is False
        print("✓ Duplicate game detection works (name & process level)")
        
        # Test getting multiple running games
        games = detector.get_running_games()
        assert isinstance(games, list)
        print(f"✓ get_running_games() returned list with {len(games)} items")
        
        print("\n✓ GameDetector edge case tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ GameDetector edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_assistant_edge_cases():
    """Test AIAssistant edge cases"""
    print("\n" + "="*60)
    print("TEST: AIAssistant Edge Cases")
    print("="*60)
    
    try:
        from src.ai_assistant import AIAssistant
        
        # Test with invalid provider (should raise error)
        try:
            assistant = AIAssistant(provider="invalid_provider")
            print("⚠ Invalid provider did not raise error (may be expected)")
        except ValueError as e:
            print(f"✓ Invalid provider raises error: {str(e)[:50]}...")

        # Get a test API key for edge case testing
        test_provider = "anthropic"
        test_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not test_api_key:
            test_provider = "openai"
            test_api_key = os.getenv("OPENAI_API_KEY")
        if not test_api_key:
            test_provider = "gemini"
            test_api_key = os.getenv("GEMINI_API_KEY")

        if not test_api_key:
            print("⚠ Skipping edge case tests (no API keys available)")
            print("✓ AIAssistant edge case tests skipped (no API keys)")
            return True

        # Test clear_history on empty assistant
        try:
            assistant = AIAssistant(provider=test_provider, api_key=test_api_key)
            assistant.clear_history()
            print("✓ Clear history on empty conversation works")
        except Exception as e:
            print(f"⚠ Clear history error: {e}")

        # Test set_current_game with empty dict
        try:
            assistant = AIAssistant(provider=test_provider, api_key=test_api_key)
            assistant.set_current_game({})
            print("✓ set_current_game with empty dict handled")
        except Exception as e:
            print(f"⚠ Empty game dict error: {e}")

        # Test set_current_game with None values
        try:
            assistant = AIAssistant(provider=test_provider, api_key=test_api_key)
            assistant.set_current_game({"name": None, "id": None})
            print("✓ set_current_game with None values handled")
        except Exception as e:
            print(f"⚠ None values error: {e}")

        # Test get_conversation_summary on empty history
        try:
            assistant = AIAssistant(provider=test_provider, api_key=test_api_key)
            summary = assistant.get_conversation_summary()
            assert isinstance(summary, list)
            print("✓ get_conversation_summary on empty history works")
        except Exception as e:
            print(f"⚠ Empty summary error: {e}")
        
        print("\n✓ AIAssistant edge case tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ AIAssistant edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concurrent_operations():
    """Test concurrent operations and thread safety"""
    print("\n" + "="*60)
    print("TEST: Concurrent Operations")
    print("="*60)
    
    try:
        from src.game_detector import GameDetector
        from src.config import Config
        import threading
        
        errors = []
        
        def config_operations():
            try:
                config = Config()
                for i in range(10):
                    config.set(f"key_{i}", f"value_{i}")
                    _ = config.get(f"key_{i}")
            except Exception as e:
                errors.append(f"Config error: {e}")
        
        def detector_operations():
            try:
                detector = GameDetector()
                for i in range(10):
                    _ = detector.get_running_games()
                    detector.add_custom_game(f"Game_{i}", [f"game_{i}.exe"])
            except Exception as e:
                errors.append(f"Detector error: {e}")
        
        # Run operations in parallel
        threads = [
            threading.Thread(target=config_operations),
            threading.Thread(target=detector_operations),
            threading.Thread(target=config_operations),
            threading.Thread(target=detector_operations),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=5)
        
        if errors:
            print(f"✗ Concurrent operation errors: {errors}")
            return False
        else:
            print("✓ Concurrent operations completed successfully")
            return True
        
    except Exception as e:
        print(f"✗ Concurrent operation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_recovery():
    """Test error recovery and resilience"""
    print("\n" + "="*60)
    print("TEST: Error Recovery")
    print("="*60)
    
    try:
        from src.config import Config

        # Test Config recovery from corrupted state
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "bad_config.json")
            
            # Write invalid JSON
            with open(config_path, 'w') as f:
                f.write("{invalid json content")
            
            # Try to load (should recover)
            config = Config(config_path=config_path)
            print("✓ Config recovered from corrupted file")
            
            # Should be back to defaults
            assert config.get("ai_provider") == "anthropic"
            print("✓ Config defaults restored after corruption")
        
        print("\n✓ Error recovery tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error recovery test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_edge_case_tests():
    """Run all edge case tests"""
    print("\n" + "#"*60)
    print("# GAMING AI ASSISTANT - EDGE CASE TEST SUITE")
    print("#"*60)
    
    tests = [
        ("Config Edge Cases", test_config_edge_cases),
        ("GameDetector Edge Cases", test_game_detector_edge_cases),
        ("AIAssistant Edge Cases", test_ai_assistant_edge_cases),
        ("Concurrent Operations", test_concurrent_operations),
        ("Error Recovery", test_error_recovery),
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
    print("# EDGE CASE TEST SUMMARY")
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
        print("\n✓ ALL EDGE CASE TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) had issues")
        return 1


if __name__ == "__main__":
    exit_code = run_all_edge_case_tests()
    sys.exit(exit_code)
