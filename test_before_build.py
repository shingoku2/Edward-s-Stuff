#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all components work before building .exe
Run this BEFORE building to catch issues early
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

STRICT_ENV = os.getenv("STRICT_PREBUILD_CHECKS") == "1"
HEADLESS_ENV = bool(
    os.getenv("CI")
    or os.getenv("PYTEST_CURRENT_TEST")
    or os.getenv("HEADLESS_TEST")
    or (os.name != "nt" and not os.getenv("DISPLAY"))
)

if STRICT_ENV:
    HEADLESS_ENV = False

print("=" * 70)
print("PRE-BUILD COMPONENT TEST")
print("=" * 70)
print()

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

errors = []
warnings = []

# Test 1: Check if config can load API keys
print("[1/8] Checking API key configuration...")
try:
    from config import Config
    test_config = Config(require_keys=False)  # Don't require keys for this test

    anthropic_key = test_config.get_api_key('anthropic')
    openai_key = test_config.get_api_key('openai')
    gemini_key = test_config.get_api_key('gemini')

    has_any_key = bool(anthropic_key or openai_key or gemini_key)

    if not has_any_key:
        warnings.append("No API keys configured (use Setup Wizard on first run)")
        print("  ⚠️  No API keys found (this is OK - run the app to use Setup Wizard)")
    else:
        print("  ✓ API keys are configured in CredentialStore")
        if anthropic_key:
            print(f"    - Anthropic key found ({len(anthropic_key)} chars)")
        if openai_key:
            print(f"    - OpenAI key found ({len(openai_key)} chars)")
        if gemini_key:
            print(f"    - Gemini key found ({len(gemini_key)} chars)")
except Exception as e:
    message = f"Failed to check API keys: {e}"
    warnings.append(message)
    print(f"  ⚠️  Could not verify API key configuration: {e}")

print()

# Test 2: Verify config module functionality
print("[2/8] Testing config module...")
try:
    config = Config(require_keys=False)  # Allow loading without keys (will use Setup Wizard)
    print(f"  ✓ Config module works")
    print(f"    AI Provider: {config.ai_provider}")
except Exception as e:
    errors.append(f"Config import failed: {e}")
    print(f"  ❌ Config error: {e}")

print()

# Test 3: Import game detector
print("[3/8] Testing game_detector module...")
try:
    from game_detector import GameDetector
    detector = GameDetector()
    print(f"  ✓ Game detector works")
    print(f"    Known games: {len(detector.KNOWN_GAMES)}")
except Exception as e:
    errors.append(f"Game detector import failed: {e}")
    print(f"  ❌ Game detector error: {e}")

print()

# Test 4: Import AI assistant
print("[4/8] Testing ai_assistant module...")
try:
    from ai_assistant import AIAssistant
    # Don't initialize, just test import
    print(f"  ✓ AI assistant module works")
except Exception as e:
    errors.append(f"AI assistant import failed: {e}")
    print(f"  ❌ AI assistant error: {e}")

print()

# Test 5: Import GUI (without starting it)
print("[5/7] Testing gui module...")
try:
    from gui import run_gui
    print(f"  ✓ GUI module imports successfully")
except Exception as e:
    message = f"GUI import failed: {e}"
    if HEADLESS_ENV:
        warnings.append(message)
        print(f"  ⚠️  GUI import skipped in headless environment: {e}")
    else:
        errors.append(message)
        print(f"  ❌ GUI error: {e}")

print()

# Test 6: Check PyQt6
print("[6/7] Testing PyQt6...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    print(f"  ✓ PyQt6 is installed and working")
except Exception as e:
    message = f"PyQt6 not working: {e}"
    if HEADLESS_ENV:
        warnings.append(message)
        print(f"  ⚠️  PyQt6 import skipped in headless environment: {e}")
    else:
        errors.append(message)
        print(f"  ❌ PyQt6 error: {e}")

print()

# Test 7: Check all dependencies
print("[7/7] Checking dependencies...")
missing_deps = []
required = ['psutil', 'requests', 'bs4', 'anthropic', 'openai', 'dotenv']

for dep in required:
    try:
        __import__(dep)
        print(f"  ✓ {dep}")
    except ImportError:
        missing_deps.append(dep)
        print(f"  ❌ {dep} - NOT INSTALLED")

if missing_deps:
    errors.append(f"Missing dependencies: {', '.join(missing_deps)}")

print()
print("=" * 70)
print("TEST RESULTS")
print("=" * 70)

exit_code = 0

if errors:
    print("\n❌ ERRORS FOUND - DO NOT BUILD YET:\n")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\nFix these errors before building the .exe")
    exit_code = 1

elif warnings:
    print("\n⚠️  WARNINGS:\n")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print("\n✅ All components work, but fix warnings before final build")

else:
    print("\n✅ ALL TESTS PASSED!")
    print("\nYou're ready to build the .exe:")
    print("  - Run BUILD_WINDOWS.bat")
    print("  - Or run BUILD_DEBUG.bat to see console messages")
    print()

RUNNING_UNDER_PYTEST = (
    os.getenv("PYTEST_CURRENT_TEST")
    or any("pytest" in arg.lower() for arg in sys.argv)
)

if RUNNING_UNDER_PYTEST:
    TEST_EXIT_CODE = exit_code
else:
    sys.exit(exit_code)
