#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaming AI Assistant
Main entry point for the application

A real-time AI assistant that detects what game you're playing
and provides tips, strategies, and answers to your questions.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup logging FIRST - before any other imports
log_file = f"gaming_ai_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

logger.info("=" * 70)
logger.info("GAMING AI ASSISTANT STARTING")
logger.info("=" * 70)
logger.info(f"Log file: {log_file}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Executable: {sys.executable}")
logger.info(f"Frozen (bundled): {getattr(sys, 'frozen', False)}")
logger.info("")

try:
    logger.info("Importing modules...")
    from config import Config
    logger.info("  [OK] config imported")

    from credential_store import CredentialStore
    logger.info("  [OK] credential_store imported")

    from game_detector import GameDetector
    logger.info("  [OK] game_detector imported")

    from ai_assistant import AIAssistant
    logger.info("  [OK] ai_assistant imported")

    from info_scraper import InfoScraper
    logger.info("  [OK] info_scraper imported")

    from gui import run_gui
    logger.info("  [OK] gui imported")
    logger.info("")

except Exception as e:
    logger.error(f"FATAL: Import failed: {e}", exc_info=True)
    print(f"\n❌ FATAL ERROR: Failed to import modules")
    print(f"Error: {e}")
    print(f"\nCheck the log file for details: {log_file}")
    input("\nPress Enter to exit...")
    sys.exit(1)


def main():
    """Main application entry point"""
    print("=" * 60)
    print("🎮 Gaming AI Assistant")
    print("=" * 60)
    print()
    print(f"📝 Logging to: {log_file}")
    print()

    try:
        # Load configuration (without requiring API keys)
        logger.info("Step 1: Loading configuration...")
        print("Loading configuration...")

        config = Config(require_keys=False)

        logger.info(f"Configuration loaded")
        logger.info(f"  AI Provider: {config.ai_provider}")
        logger.info(f"  Hotkey: {config.overlay_hotkey}")
        logger.info(f"  Check interval: {config.check_interval}")
        logger.info(f"  OpenAI key present: {bool(config.openai_api_key)}")
        logger.info(f"  Anthropic key present: {bool(config.anthropic_api_key)}")
        logger.info(f"  Configuration complete: {config.is_configured()}")

        print(f"[OK] Configuration loaded")
        print(f"  AI Provider: {config.ai_provider}")
        print(f"  Hotkey: {config.overlay_hotkey}")

        if not config.is_configured():
            print(f"  ⚠️  No API keys configured - Settings dialog will open")
        print()

        credential_store = CredentialStore()
        session_tokens = credential_store.get_provider_tokens(config.ai_provider)

        if session_tokens:
            logger.info(
                "Loaded session tokens for provider %s: %s",
                config.ai_provider,
                list(session_tokens.keys()),
            )
        else:
            logger.info("No session tokens found for provider %s", config.ai_provider)

        # Initialize game detector
        logger.info("Step 2: Initializing game detector...")
        print("Initializing game detector...")

        game_detector = GameDetector()

        logger.info(f"Game detector initialized")
        logger.info(f"  Known games: {len(game_detector.common_games)}")

        print("[OK] Game detector ready")
        print()

        # Initialize AI assistant (only if API keys are configured)
        ai_assistant = None
        if config.has_provider_key() or session_tokens:
            logger.info("Step 3: Initializing AI assistant...")
            print("Initializing AI assistant...")

            ai_assistant = AIAssistant(
                provider=config.ai_provider,
                api_key=config.get_api_key(),
                session_tokens=session_tokens,
            )

            logger.info(f"AI assistant initialized")
            logger.info(f"  Provider: {ai_assistant.provider}")

            print("[OK] AI assistant ready")
            print()
        else:
            logger.info("Step 3: Skipping AI assistant initialization (no credentials)")
            print("[INFO] AI assistant will be initialized after you configure credentials")
            print()

        # Initialize info scraper
        logger.info("Step 4: Initializing information scraper...")
        print("Initializing information scraper...")

        info_scraper = InfoScraper()

        logger.info(f"Info scraper initialized")
        logger.info(f"  Wiki sources: {len(info_scraper.wiki_urls)}")

        print("[OK] Info scraper ready")
        print()

        # Test game detection
        logger.info("Step 5: Scanning for running games...")
        print("Scanning for running games...")

        game = game_detector.detect_running_game()
        if game:
            logger.info(f"Detected game: {game['name']} (PID: {game.get('pid', 'unknown')})")
            print(f"[OK] Detected game: {game['name']}")
        else:
            logger.info("No game currently running")
            print("  No game currently running")
        print()

        logger.info("=" * 70)
        logger.info("All initialization complete - Starting GUI...")
        logger.info("=" * 70)

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
        logger.info("Calling run_gui()...")
        run_gui(game_detector, ai_assistant, info_scraper, config, credential_store)

        logger.info("GUI exited normally")

    except ValueError as e:
        logger.error(f"Configuration error: {e}", exc_info=True)
        print(f"\n❌ Configuration Error: {e}")
        print("\nSetup instructions:")
        print("1. Make sure .env file exists in the same folder as the .exe")
        print()
        print("2. Edit .env and add your API key:")
        print("   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here")
        print("   AI_PROVIDER=anthropic")
        print()
        print(f"3. Check the log file for details: {log_file}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        print(f"\n❌ Import Error: {e}")
        print("\nThis usually means a required library is missing.")
        print(f"Check the log file for details: {log_file}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("User interrupted (Ctrl+C)")
        print("\n\n👋 Shutting down...")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected Error: {e}")
        print()
        print("Full error details:")
        import traceback
        traceback.print_exc()
        print()
        print(f"📝 Full log saved to: {log_file}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"\n💥 FATAL ERROR: {e}")
        print(f"📝 Check log file: {log_file}")
        input("\nPress Enter to exit...")
        sys.exit(1)
