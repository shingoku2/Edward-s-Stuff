#!/usr/bin/env python3
"""
Ollama Integration Verification Script

This script tests the Ollama integration in Omnix Gaming AI Assistant.
Run this script to verify that Ollama is properly installed and configured.

Usage:
    python test_ollama_integration.py
"""

import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def test_ollama_library():
    """Test if ollama library is installed"""
    print("\n" + "=" * 60)
    print("TEST 1: Checking Ollama Python Library")
    print("=" * 60)

    try:
        import ollama
        print("✅ Ollama library is installed")
        print(f"   Version: {ollama.__version__ if hasattr(ollama, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print("❌ Ollama library is NOT installed")
        print("   Install with: pip install ollama")
        return False


def test_ollama_connection(base_url="http://localhost:11434"):
    """Test connection to Ollama daemon"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing Ollama Daemon Connection")
    print("=" * 60)
    print(f"   Base URL: {base_url}")

    try:
        import ollama
        client = ollama.Client(host=base_url)

        # Try to list models
        result = client.list()
        models = result.get("models", [])

        if models:
            print(f"✅ Connected to Ollama daemon!")
            print(f"   Found {len(models)} installed models:")
            for model in models:
                model_name = model.get("name", "Unknown")
                model_size = model.get("size", 0)
                size_gb = model_size / (1024**3)
                print(f"   - {model_name} ({size_gb:.2f} GB)")
            return True
        else:
            print("⚠️  Connected to Ollama, but no models are installed")
            print("   Install a model with: ollama pull llama3")
            return True

    except Exception as e:
        print(f"❌ Failed to connect to Ollama daemon")
        print(f"   Error: {e}")
        print("\n   Troubleshooting:")
        print("   1. Is Ollama installed? Visit: https://ollama.com/")
        print("   2. Is the Ollama daemon running?")
        print("      - Windows/Mac: Ollama should auto-start")
        print("      - Linux: Run 'ollama serve' in a terminal")
        print(f"   3. Is Ollama listening on {base_url}?")
        return False


def test_omnix_provider():
    """Test Omnix OllamaProvider integration"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Omnix OllamaProvider Integration")
    print("=" * 60)

    try:
        from src.providers import OllamaProvider

        # Initialize provider
        provider = OllamaProvider()
        print(f"✅ OllamaProvider initialized")
        print(f"   Base URL: {provider.base_url}")
        print(f"   Default Model: {provider.default_model}")

        # Test configuration
        is_configured = provider.is_configured()
        print(f"   Is Configured: {is_configured}")

        if not is_configured:
            print("❌ Provider is not configured (client not initialized)")
            return False

        # Test connection
        print("\n   Testing connection...")
        health = provider.test_connection()

        if health.is_healthy:
            print(f"✅ {health.message}")
            if health.details and "models" in health.details:
                print(f"   Available models: {', '.join(health.details['models'])}")
            return True
        else:
            print(f"❌ {health.message}")
            return False

    except Exception as e:
        print(f"❌ Failed to test OllamaProvider")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_chat():
    """Test a simple chat request"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Simple Chat Request")
    print("=" * 60)

    try:
        from src.providers import OllamaProvider

        provider = OllamaProvider()

        if not provider.is_configured():
            print("⚠️  Skipping chat test - provider not configured")
            return False

        print("   Sending test message: 'Say hello in 5 words or less'")
        print("   (This may take a moment...)")

        messages = [
            {"role": "user", "content": "Say hello in 5 words or less"}
        ]

        response = provider.chat(messages)

        print(f"✅ Chat request successful!")
        print(f"   Model: {response.get('model', 'Unknown')}")
        print(f"   Response: {response.get('content', 'No content')}")

        return True

    except Exception as e:
        print(f"❌ Chat request failed")
        print(f"   Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("OMNIX OLLAMA INTEGRATION VERIFICATION")
    print("=" * 60)
    print("\nThis script will verify that Ollama is properly integrated")
    print("with Omnix Gaming AI Assistant.\n")

    results = []

    # Test 1: Library
    results.append(("Ollama Library", test_ollama_library()))

    # Test 2: Connection
    results.append(("Ollama Daemon", test_ollama_connection()))

    # Test 3: Provider
    results.append(("OllamaProvider", test_omnix_provider()))

    # Test 4: Chat (only if previous tests passed)
    if all(r[1] for r in results):
        results.append(("Simple Chat", test_simple_chat()))
    else:
        print("\n⚠️  Skipping chat test due to previous failures")
        results.append(("Simple Chat", None))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⊘  SKIP"
        print(f"   {status} - {test_name}")

    passed = sum(1 for r in results if r[1] is True)
    total = len([r for r in results if r[1] is not None])

    print(f"\n   Result: {passed}/{total} tests passed")

    if passed == total and total > 0:
        print("\n🎉 All tests passed! Ollama is ready to use in Omnix!")
        print("\nNext steps:")
        print("1. Launch Omnix: python main.py")
        print("2. Go to Settings > AI Providers")
        print("3. Select 'Ollama (Local)' from the dropdown")
        print("4. Click 'Test Connection' to verify")
        print("5. Click 'Save' to use Ollama as your AI provider")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nQuick troubleshooting:")
        print("- Install Ollama: https://ollama.com/")
        print("- Install Python library: pip install ollama")
        print("- Pull a model: ollama pull llama3")
        print("- Start Ollama daemon (should auto-start on most systems)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
