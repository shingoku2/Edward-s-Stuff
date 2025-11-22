#!/usr/bin/env python3
"""
Test script for Ollama dropdown model selection
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import():
    """Test that providers_tab can be imported"""
    try:
        from providers_tab import ProvidersTab, FetchOllamaModelsThread
        print("✅ Successfully imported ProvidersTab and FetchOllamaModelsThread")
        return True
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return False


def test_thread_class():
    """Test that FetchOllamaModelsThread can be instantiated"""
    try:
        from providers_tab import FetchOllamaModelsThread
        from PyQt6.QtWidgets import QApplication

        # Create app instance (required for Qt)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        thread = FetchOllamaModelsThread("http://localhost:11434")
        print("✅ Successfully created FetchOllamaModelsThread instance")
        print(f"   Base URL: {thread.base_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to create thread: {e}")
        return False


def test_providers_tab_init():
    """Test that ProvidersTab can be initialized"""
    try:
        from providers_tab import ProvidersTab
        from config import Config
        from PyQt6.QtWidgets import QApplication

        # Create app instance (required for Qt)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create config
        config = Config(require_keys=False)

        # Create tab (this should trigger auto_fetch_ollama_models)
        print("Creating ProvidersTab...")
        tab = ProvidersTab(config)

        # Check that fetch thread was created
        if hasattr(tab, 'fetch_models_thread'):
            print("✅ ProvidersTab initialized successfully")
            print(f"   Fetch thread created: {tab.fetch_models_thread is not None}")
            print(f"   Ollama model combo exists: {hasattr(tab, 'ollama_model_combo')}")
            return True
        else:
            print("❌ Fetch thread not created")
            return False

    except Exception as e:
        print(f"❌ Failed to initialize ProvidersTab: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Ollama Dropdown Model Selection")
    print("=" * 60)
    print()

    tests = [
        ("Import Test", test_import),
        ("Thread Class Test", test_thread_class),
        ("ProvidersTab Initialization", test_providers_tab_init),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 40)
        results.append(test_func())
        print()

    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
