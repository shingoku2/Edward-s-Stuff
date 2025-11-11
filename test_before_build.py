#!/usr/bin/env python3
"""
Test script to verify all components work before building .exe
Run this BEFORE building to catch issues early
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print("PRE-BUILD COMPONENT TEST")
print("=" * 70)
print()

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

errors = []
warnings = []

# Test 1: Check .env file
print("[1/8] Checking .env file...")
if not os.path.exists('.env'):
    errors.append(".env file not found! Copy .env.example to .env and add your API key")
    print("  ❌ .env file not found")
else:
    print("  ✓ .env file exists")

    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()

    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')

    if not anthropic_key or anthropic_key == 'your_anthropic_api_key_here':
        warnings.append("Anthropic API key not set in .env")
        print("  ⚠️  Anthropic API key not configured")
    else:
        print(f"  ✓ Anthropic API key found ({len(anthropic_key)} chars)")

    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("  ℹ️  OpenAI API key not set (optional)")
    else:
        print(f"  ✓ OpenAI API key found ({len(openai_key)} chars)")

print()

# Test 2: Import config
print("[2/8] Testing config module...")
try:
    from config import Config
    config = Config()
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

# Test 5: Import info scraper
print("[5/8] Testing info_scraper module...")
try:
    from info_scraper import GameInfoScraper
    scraper = GameInfoScraper()
    print(f"  ✓ Info scraper works")
except Exception as e:
    errors.append(f"Info scraper import failed: {e}")
    print(f"  ❌ Info scraper error: {e}")

print()

# Test 6: Import GUI (without starting it)
print("[6/8] Testing gui module...")
try:
    from gui import run_gui
    print(f"  ✓ GUI module imports successfully")
except Exception as e:
    errors.append(f"GUI import failed: {e}")
    print(f"  ❌ GUI error: {e}")

print()

# Test 7: Check PyQt6
print("[7/8] Testing PyQt6...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    print(f"  ✓ PyQt6 is installed and working")
except Exception as e:
    errors.append(f"PyQt6 not working: {e}")
    print(f"  ❌ PyQt6 error: {e}")

print()

# Test 8: Check all dependencies
print("[8/8] Checking dependencies...")
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

if errors:
    print("\n❌ ERRORS FOUND - DO NOT BUILD YET:\n")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\nFix these errors before building the .exe")
    sys.exit(1)

elif warnings:
    print("\n⚠️  WARNINGS:\n")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print("\n✅ All components work, but fix warnings before final build")
    sys.exit(0)

else:
    print("\n✅ ALL TESTS PASSED!")
    print("\nYou're ready to build the .exe:")
    print("  - Run BUILD_WINDOWS.bat")
    print("  - Or run BUILD_DEBUG.bat to see console messages")
    print()
    sys.exit(0)
