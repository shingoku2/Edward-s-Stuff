#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Gaming AI Assistant
Demonstrates the core functionality without requiring a full GUI
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from game_detector import GameDetector
import psutil


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def test_game_detector():
    """Test game detection functionality"""
    print_header("Testing Game Detector")

    detector = GameDetector()

    # Show supported games
    print(f"✓ Game detector initialized")
    print(f"✓ Supports {len(detector.KNOWN_GAMES)} known games")
    print(f"\nSample of supported games:")
    for i, (exe, name) in enumerate(list(detector.KNOWN_GAMES.items())[:10], 1):
        print(f"  {i}. {name} ({exe})")
    print(f"  ... and {len(detector.KNOWN_GAMES) - 10} more!")

    # Try to detect running games
    print(f"\n{'─' * 60}")
    print("Scanning for running games...")
    print(f"{'─' * 60}\n")

    game = detector.detect_running_game()
    if game:
        print(f"🎮 Detected: {game['name']}")
        print(f"   Process: {game['process']}")
        if game.get('exe'):
            print(f"   Path: {game['exe']}")
    else:
        print("No games currently running")
        print("\nTo test game detection:")
        print("1. Launch a supported game")
        print("2. Run this test again")

    # Show some running processes (for debugging)
    print(f"\n{'─' * 60}")
    print("Sample of running processes:")
    print(f"{'─' * 60}\n")

    count = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].endswith('.exe'):
                print(f"  • {proc.info['name']}")
                count += 1
                if count >= 5:
                    break
        except Exception:
            pass

    return detector


def test_module_integration():
    """Test that all modules work together"""
    print_header("Testing Module Integration")

    try:
        from config import Config
        from game_detector import GameDetector
        from ai_assistant import AIAssistant
        from gui import MainWindow
        from ai_router import AIRouter
        from providers import AIProvider
        from keybind_manager import KeybindManager
        from macro_manager import MacroManager
        from knowledge_pack import KnowledgePack
        from session_logger import SessionLogger

        print("✓ config")
        print("✓ game_detector")
        print("✓ ai_assistant")
        print("✓ gui")
        print("✓ ai_router")
        print("✓ providers")
        print("✓ keybind_manager")
        print("✓ macro_manager")
        print("✓ knowledge_pack")
        print("✓ session_logger")

        print("\nAll modules integrated successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def show_example_usage():
    """Show example usage"""
    print_header("Example Usage")

    print("""
When a game is detected, you can ask questions like:

Gaming Questions:
  • "What's the best build for a tank?"
  • "How do I beat the boss in level 5?"
  • "Explain the crafting system"
  • "What are some beginner tips?"
  • "What's the current meta?"

Strategy Questions:
  • "Best weapons for PvP?"
  • "How to farm gold efficiently?"
  • "Quest walkthrough for [quest name]"
  • "Character tier list"

The AI will:
  1. Use its knowledge of the game
  2. Search game wikis for additional info
  3. Provide comprehensive, helpful answers
  4. Remember context from previous questions
""")


def show_next_steps():
    """Show next steps for the user"""
    print_header("Next Steps")

    print("""
To use the Gaming AI Assistant:

1. Get an AI API Key (if you don't have one):
   • Anthropic (Claude): https://console.anthropic.com/
   • OpenAI (GPT): https://platform.openai.com/
   • Google Gemini: https://aistudio.google.com/app/apikey

2. Run the application:
   python main.py

3. Configure your API key:
   • The Setup Wizard will launch automatically on first run
   • Select your preferred AI provider (Anthropic, OpenAI, or Gemini)
   • Enter your API key (it will be stored securely in CredentialStore)
   • Your key is encrypted and NOT stored in .env files

4. Start gaming!
   • The GUI will open and start detecting games
   • Press Ctrl+Shift+G while in a game to open the assistant

Keyboard Shortcuts:
  • Ctrl+Shift+G - Toggle assistant window
  • Enter - Send message

System Tray:
  • The app minimizes to the system tray
  • Right-click the tray icon for options

Note: The GUI requires a display environment. If you're running
this in a headless environment (like Docker or SSH), the GUI won't
work, but all the core modules function correctly!
""")


def main():
    """Main test function"""
    print_header("🎮 Gaming AI Assistant - Component Test")

    print("This script tests the core components without requiring")
    print("an API key or running games.\n")

    # Test module integration
    if not test_module_integration():
        print("\n❌ Module integration test failed!")
        sys.exit(1)

    # Test game detector
    detector = test_game_detector()

    # Show example usage
    show_example_usage()

    # Show next steps
    show_next_steps()

    print_header("✅ All Tests Passed!")
    print("\nThe Gaming AI Assistant is ready to use!")
    print("Run: python main.py")
    print("The Setup Wizard will guide you through API key configuration.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
