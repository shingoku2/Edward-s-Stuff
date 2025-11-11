#!/usr/bin/env python3
"""
Gaming AI Assistant
Main entry point for the application

A real-time AI assistant that detects what game you're playing
and provides tips, strategies, and answers to your questions.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from config import Config
from game_detector import GameDetector
from ai_assistant import AIAssistant
from info_scraper import GameInfoScraper
from gui import run_gui


def main():
    """Main application entry point"""
    print("=" * 60)
    print("🎮 Gaming AI Assistant")
    print("=" * 60)
    print()

    try:
        # Load configuration
        print("Loading configuration...")
        config = Config()
        print(f"✓ Configuration loaded")
        print(f"  AI Provider: {config.ai_provider}")
        print(f"  Hotkey: {config.overlay_hotkey}")
        print()

        # Initialize game detector
        print("Initializing game detector...")
        game_detector = GameDetector()
        print("✓ Game detector ready")
        print()

        # Initialize AI assistant
        print("Initializing AI assistant...")
        ai_assistant = AIAssistant(
            provider=config.ai_provider,
            api_key=config.get_api_key()
        )
        print("✓ AI assistant ready")
        print()

        # Initialize info scraper
        print("Initializing information scraper...")
        info_scraper = GameInfoScraper()
        print("✓ Info scraper ready")
        print()

        # Test game detection
        print("Scanning for running games...")
        game = game_detector.detect_running_game()
        if game:
            print(f"✓ Detected game: {game['name']}")
        else:
            print("  No game currently running")
        print()

        print("=" * 60)
        print("Starting GUI...")
        print("=" * 60)
        print()
        print("Tips:")
        print("  • Press Ctrl+Shift+G to toggle the assistant window")
        print("  • The app will automatically detect when you launch a game")
        print("  • Ask questions about the game in real-time")
        print("  • Minimize to system tray to keep it running in background")
        print()

        # Run the GUI
        run_gui(game_detector, ai_assistant, info_scraper)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nSetup instructions:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print()
        print("2. Edit .env and add your API key:")
        print("   - For OpenAI: Add your OpenAI API key")
        print("   - For Anthropic: Add your Anthropic API key")
        print()
        print("3. Set your preferred AI provider in .env:")
        print("   AI_PROVIDER=anthropic  (or 'openai')")
        print()
        sys.exit(1)

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
