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

# Add src to path (tests/integration -> tests -> repo root -> src)
repo_root = Path(__file__).resolve().parents[2]
src_path = repo_root / 'src'
sys.path.insert(0, str(src_path))

errors = []
warnings = []

# Test 1: Verify config module functionality
print("[1/7] Testing config module...")
try:
    from config import Config
    test_config = Config(require_keys=False)  # Don't require keys for this test
    print(f"  OK: Config module works")
    print(f"    AI Provider: {test_config.ai_provider}")
except Exception as e:
    errors.append(f"Config import failed: {e}")
    print(f"  FAIL: Config error: {e}")

print()

# Test 2: Import game detector
print("[2/7] Testing game_detector module...")
try:
    from game_detector import GameDetector
    detector = GameDetector()
    print(f"  OK: Game detector works")
    print(f"    Known games: {len(detector.KNOWN_GAMES)}")
except Exception as e:
    errors.append(f"Game detector import failed: {e}")
    print(f"  FAIL: Game detector error: {e}")

print()

# Test 3: Import AI assistant
print("[3/7] Testing ai_assistant module...")
try:
    from ai_assistant import AIAssistant
    # Don't initialize, just test import
    print(f"  OK: AI assistant module works")
except Exception as e:
    errors.append(f"AI assistant import failed: {e}")
    print(f"  FAIL: AI assistant error: {e}")

print()

# Test 4: Import GUI (without starting it)
print("[4/7] Testing gui module...")
try:
    from gui import run_gui
    print(f"  OK: GUI module imports successfully")
except Exception as e:
    message = f"GUI import failed: {e}"
    if HEADLESS_ENV:
        warnings.append(message)
        print(f"  WARNING: GUI import skipped in headless environment: {e}")
    else:
        errors.append(message)
        print(f"  FAIL: GUI error: {e}")

print()

# Test 5: Check PyQt6
print("[5/7] Testing PyQt6...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    print(f"  OK: PyQt6 is installed and working")
except Exception as e:
    message = f"PyQt6 not working: {e}"
    if HEADLESS_ENV:
        warnings.append(message)
        print(f"  WARNING: PyQt6 import skipped in headless environment: {e}")
    else:
        errors.append(message)
        print(f"  FAIL: PyQt6 error: {e}")

print()

# Test 6: Check all dependencies
print("[6/7] Checking dependencies...")
missing_deps = []
required = ['psutil', 'requests', 'beautifulsoup4', 'lxml', 'ollama', 'dotenv', 'PyYAML', 'cryptography', 'keyring', 'pynput']

for dep in required:
    try:
        __import__(dep)
        print(f"  OK: {dep}")
    except ImportError:
        missing_deps.append(dep)
        print(f"  FAIL: {dep} - NOT INSTALLED")

if missing_deps:
    errors.append(f"Missing dependencies: {', '.join(missing_deps)}")

print()

# Test 7: Check PyQt6 for GUI (pure PyQt6 — no WebEngine)
print("[7/7] Testing PyQt6...")
try:
    from PyQt6.QtWidgets import QApplication
    print(f"  OK: PyQt6 is installed and working")
except ImportError as e:
    errors.append(f"PyQt6 not installed: {e} (required for GUI)")
    print(f"  FAIL: PyQt6 error: {e}")

print()
print("=" * 70)
print("TEST RESULTS")
print("=" * 70)

exit_code = 0

if errors:
    print("\nFAIL: ERRORS FOUND - DO NOT BUILD YET:\n")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\nFix these errors before building the .exe")
    exit_code = 1

elif warnings:
    print("\nWARNING: WARNINGS:\n")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print("\nOK: All components work, but fix warnings before final build")

else:
    print("\nOK: ALL TESTS PASSED!")
    print("\nYou're ready to build the .exe:")
    print("  - Run BUILD.bat")
    print()

RUNNING_UNDER_PYTEST = (
    os.getenv("PYTEST_CURRENT_TEST")
    or any("pytest" in arg.lower() for arg in sys.argv)
)

if RUNNING_UNDER_PYTEST:
    TEST_EXIT_CODE = exit_code
else:
    sys.exit(exit_code)
