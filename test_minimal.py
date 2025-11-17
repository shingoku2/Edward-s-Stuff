#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal test - no GUI, just test if modules work
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("Minimal Component Test")
print("=" * 50)

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    print("\n1. Testing config...")
    from config import Config
    config = Config()
    print(f"   ✓ Config loaded - Provider: {config.ai_provider}")

    print("\n2. Testing game detector...")
    from game_detector import GameDetector
    detector = GameDetector()
    print(f"   ✓ Detector loaded - {len(detector.KNOWN_GAMES)} games")

    print("\n3. Testing AI assistant...")
    from ai_assistant import AIAssistant
    from ai_router import get_router
    # Initialize the router, which is what AIAssistant will use
    router = get_router(config)
    ai = AIAssistant(config=config)
    print(f"   ✓ AI assistant loaded (using router)")

    print("\n" + "=" * 50)
    print("✅ ALL CORE MODULES WORKING!")
    print("=" * 50)
    print("\nThe problem is likely with PyQt6/GUI.")
    print("Try running: BUILD_DEBUG.bat")
    print("This will show you the actual error message.")
    print()

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nFix this error before building!")
