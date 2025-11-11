#!/usr/bin/env python3
"""
Minimal test - no GUI, just test if modules work
"""

import sys
import os
from pathlib import Path

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
    ai = AIAssistant(provider=config.ai_provider, api_key=config.get_api_key())
    print(f"   ✓ AI assistant loaded")

    print("\n4. Testing info scraper...")
    from info_scraper import GameInfoScraper
    scraper = GameInfoScraper()
    print(f"   ✓ Info scraper loaded")

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
