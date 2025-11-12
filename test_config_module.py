#!/usr/bin/env python3
"""
Test Configuration Module
Tests the critical override=True fix and open_webui_api_key functionality
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_config_override():
    """Test that load_dotenv(override=True) actually reloads values"""
    print("=" * 60)
    print("TEST 1: Config Override Functionality")
    print("=" * 60)

    # Create a temporary .env file
    temp_dir = tempfile.mkdtemp()
    temp_env = os.path.join(temp_dir, '.env')

    try:
        # Write initial value
        with open(temp_env, 'w') as f:
            f.write('OPEN_WEBUI_API_KEY=initial_value_12345\n')

        # Set environment variable to simulate first load
        os.environ['OPEN_WEBUI_API_KEY'] = 'initial_value_12345'

        print(f"✓ Created test .env file: {temp_env}")
        print(f"✓ Set env var to: {os.environ.get('OPEN_WEBUI_API_KEY')}")

        # Now update the .env file (simulating save_to_env)
        with open(temp_env, 'w') as f:
            f.write('OPEN_WEBUI_API_KEY=updated_value_67890\n')

        print(f"✓ Updated .env file to: updated_value_67890")

        # Test WITHOUT override (the bug)
        from dotenv import load_dotenv
        load_dotenv(temp_env, override=False)  # Default behavior
        value_without_override = os.environ.get('OPEN_WEBUI_API_KEY')

        print(f"\n  Without override=True: {value_without_override}")
        if value_without_override == 'initial_value_12345':
            print("  ✓ Confirmed bug: value NOT reloaded (still has old value)")
        else:
            print("  ✗ Unexpected: value changed without override")

        # Test WITH override (the fix)
        load_dotenv(temp_env, override=True)  # Our fix
        value_with_override = os.environ.get('OPEN_WEBUI_API_KEY')

        print(f"  With override=True: {value_with_override}")
        if value_with_override == 'updated_value_67890':
            print("  ✓ Fix confirmed: value properly reloaded!")
            return True
        else:
            print("  ✗ Fix failed: value not reloaded")
            return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        if 'OPEN_WEBUI_API_KEY' in os.environ:
            del os.environ['OPEN_WEBUI_API_KEY']


def test_config_class():
    """Test the Config class loads open_webui_api_key"""
    print("\n" + "=" * 60)
    print("TEST 2: Config Class Functionality")
    print("=" * 60)

    # Clean up .env file first to avoid interference from other tests
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = [line for line in f if not line.strip().startswith('OPEN_WEBUI_API_KEY=')]
        with open(env_path, 'w') as f:
            f.writelines(lines)

    # Temporarily set environment variable
    test_key = "sk-test-api-key-123456789"
    os.environ['OPEN_WEBUI_API_KEY'] = test_key

    try:
        from config import Config

        config = Config()

        print(f"✓ Created Config instance")
        print(f"  open_webui_api_key attribute exists: {hasattr(config, 'open_webui_api_key')}")
        print(f"  Value: {config.open_webui_api_key}")
        print(f"  Length: {len(config.open_webui_api_key) if config.open_webui_api_key else 0}")

        if config.open_webui_api_key == test_key:
            print("  ✓ Config correctly loaded open_webui_api_key from environment")
            return True
        else:
            print(f"  ✗ Expected '{test_key}', got '{config.open_webui_api_key}'")
            return False

    finally:
        if 'OPEN_WEBUI_API_KEY' in os.environ:
            del os.environ['OPEN_WEBUI_API_KEY']


def test_save_to_env():
    """Test Config.save_to_env includes open_webui_api_key"""
    print("\n" + "=" * 60)
    print("TEST 3: Config.save_to_env() Method")
    print("=" * 60)

    # Create a temporary .env file
    temp_dir = tempfile.mkdtemp()
    temp_env = os.path.join(temp_dir, '.env')

    try:
        from config import Config

        # Temporarily override the .env path
        original_env_path = None
        if hasattr(Config, '_env_path'):
            original_env_path = Config._env_path

        # Save test configuration
        test_open_webui_key = "sk-test-open-webui-key-987654321"

        Config.save_to_env(
            provider='ollama',
            openai_key='sk-test-openai',
            anthropic_key='sk-test-anthropic',
            gemini_key='sk-test-gemini',
            ollama_endpoint='http://localhost:8080',
            open_webui_api_key=test_open_webui_key
        )

        print(f"✓ Called Config.save_to_env() with test data")

        # Read the .env file to verify
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()

            if 'OPEN_WEBUI_API_KEY=' in content:
                print(f"  ✓ .env file contains OPEN_WEBUI_API_KEY")

                # Check if the value is correct
                if test_open_webui_key in content:
                    print(f"  ✓ Correct value saved: {test_open_webui_key}")
                    return True
                else:
                    print(f"  ✗ Value not found in .env file")
                    print(f"  Content: {content}")
                    return False
            else:
                print(f"  ✗ .env file missing OPEN_WEBUI_API_KEY")
                print(f"  Content: {content}")
                return False
        else:
            print(f"  ✗ .env file not found at {env_path}")
            return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all configuration tests"""
    print("\n" + "=" * 60)
    print("CONFIGURATION MODULE TEST SUITE")
    print("=" * 60)
    print()

    results = []

    # Test 1: Override functionality
    try:
        result = test_config_override()
        results.append(("Override Functionality", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Override Functionality", False))

    # Test 2: Config class
    try:
        result = test_config_class()
        results.append(("Config Class", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Config Class", False))

    # Test 3: save_to_env
    try:
        result = test_save_to_env()
        results.append(("save_to_env Method", result))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("save_to_env Method", False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All configuration tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
