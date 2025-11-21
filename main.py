"""
Gaming AI Assistant - Main Application Entry Point
"""

import logging
from pathlib import Path
from datetime import datetime
import sys
import traceback

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def setup_logging() -> Path:
    """Setup logging with timestamped file in the current directory (for debug builds) or user's config directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"gaming_ai_assistant_{timestamp}.log"

    # Try to write to current directory first (for debug builds)
    log_file = Path.cwd() / log_filename

    try:
        # Test if we can write to current directory
        log_file.parent.mkdir(parents=True, exist_ok=True)
        test_write = log_file.parent / ".test_write"
        test_write.touch()
        test_write.unlink()
        print(f"✓ Log file will be created at: {log_file}")
    except (PermissionError, OSError) as e:
        # Fall back to user's home directory if current directory isn't writable
        print(f"⚠️  Cannot write to current directory ({e}), using home directory instead")
        log_dir = Path.home() / ".gaming_ai_assistant" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / log_filename
        print(f"✓ Log file will be created at: {log_file}")

    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout),
            ],
            force=True,
        )

        # Immediately write a test message to ensure file is created
        test_logger = logging.getLogger("startup")
        test_logger.info("=" * 70)
        test_logger.info("Gaming AI Assistant - Log Started")
        test_logger.info(f"Log file: {log_file}")
        test_logger.info(f"Timestamp: {datetime.now()}")
        test_logger.info("=" * 70)

        # Flush to ensure file is created immediately
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Verify the file was actually created
        if log_file.exists():
            print(f"✓ Log file created successfully: {log_file}")
        else:
            print(f"⚠️  Warning: Log file may not have been created at {log_file}")

    except Exception as e:
        print(f"❌ Error setting up logging: {e}")
        print(f"   Attempted log file path: {log_file}")
        traceback.print_exc()

        # As a last resort, try console-only logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
            force=True,
        )
        print("⚠️  Logging to console only")

    return log_file


log_file_path = setup_logging()
logger = logging.getLogger(__name__)


def cleanup_logging():
    """Ensure all log handlers are flushed and closed properly."""
    logger.info("=" * 70)
    logger.info("Application shutting down - closing log file")
    logger.info(f"Final log location: {log_file_path}")
    logger.info("=" * 70)

    # Flush and close all handlers
    for handler in logging.getLogger().handlers[:]:
        handler.flush()
        handler.close()
        logging.getLogger().removeHandler(handler)

    print(f"\n📝 Complete log saved to: {log_file_path}")
    print()


import atexit
atexit.register(cleanup_logging)


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catch and log all unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("=" * 70)
    logger.critical("UNHANDLED EXCEPTION CAUGHT!")
    logger.critical("=" * 70)
    logger.critical("Exception Type: %s", exc_type.__name__)
    logger.critical("Exception Value: %s", exc_value)
    logger.critical("Traceback:")
    for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
        logger.critical(line.rstrip())

    # Flush logs immediately to ensure everything is written
    for handler in logging.getLogger().handlers:
        handler.flush()

    print("\n" + "=" * 70)
    print("💥 UNHANDLED EXCEPTION!")
    print("=" * 70)
    print(f"Type: {exc_type.__name__}")
    print(f"Message: {exc_value}")
    print("\nFull traceback:")
    print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    print("=" * 70)
    print(f"\n📝 Full error log saved to: {log_file_path}")
    print()


sys.excepthook = global_exception_handler


def main():
    """Main application entry point with improved error handling."""

    print("=" * 60)
    print("🎮 Gaming AI Assistant")
    print("=" * 60)
    print(f"📝 Logging to: {log_file_path}")
    print()

    from config import Config
    from credential_store import CredentialStore
    from game_detector import GameDetector
    from ai_assistant import AIAssistant
    from gui import run_gui
    from ui.design_system import design_system

    try:
        logger.info("Step 1: Loading configuration...")
        print("Loading configuration...")

        config = Config(require_keys=False)

        logger.info("Configuration loaded")
        logger.info("  AI Provider: %s", config.ai_provider)
        logger.info("  Hotkey: %s", config.overlay_hotkey)
        logger.info("  Check interval: %s", config.check_interval)
        logger.info("  OpenAI key present: %s", bool(config.openai_api_key))
        logger.info("  Anthropic key present: %s", bool(config.anthropic_api_key))
        logger.info("  Configuration complete: %s", config.is_configured())

        print("[OK] Configuration loaded")
        print(f"  AI Provider: {config.ai_provider}")
        print(f"  Hotkey: {config.overlay_hotkey}")
        if not config.is_configured():
            print("  ⚠️  No API keys configured - Settings dialog will open")
        print()

        credential_store = CredentialStore()
        session_tokens = config.session_tokens.get(config.ai_provider, {})

        if session_tokens:
            logger.info("Loaded session tokens for provider %s", config.ai_provider)
        else:
            logger.info("No session tokens found for provider %s", config.ai_provider)

        logger.info("Step 2: Initializing game detector...")
        print("Initializing game detector...")

        game_detector = GameDetector()

        logger.info("Game detector initialized")
        logger.info("  Known games: %s", len(game_detector.common_games))

        print("[OK] Game detector ready")
        print(f"  Known games: {len(game_detector.common_games)}")
        print()

        ai_assistant = None
        if config.has_provider_key() or session_tokens:
            logger.info("Step 3: Initializing AI assistant...")
            print("Initializing AI assistant...")

            ai_assistant = AIAssistant(
                provider=config.ai_provider,
                config=config,
                session_tokens=session_tokens,
            )

            logger.info("AI assistant initialized")
            logger.info("  Provider: %s", ai_assistant.provider)

            print("[OK] AI assistant ready")
            print()
        else:
            logger.info("Step 3: Skipping AI assistant initialization (no credentials)")
            print("[INFO] AI assistant will be initialized after you configure credentials")
            print()

        logger.info("Step 4: Scanning for running games...")
        print("Scanning for running games...")

        game = game_detector.detect_running_game()
        if game:
            logger.info("Detected game: %s (PID: %s)", game.get("name"), game.get("pid", "unknown"))
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

        logger.info("Calling run_gui()...")
        run_gui(ai_assistant, config, credential_store, design_system, game_detector)
        logger.info("GUI exited normally")

    except ValueError as e:
        logger.error("Configuration error: %s", e, exc_info=True)
        # Flush logs immediately
        for handler in logging.getLogger().handlers:
            handler.flush()
        print(f"\n❌ Configuration Error: {e}")
        print("\nSetup instructions:")
        print("1. Make sure .env file exists in the same folder as the .exe")
        print()
        print("2. Edit .env and add your API key:")
        print("   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here")
        print("   AI_PROVIDER=anthropic")
        print()
        print(f"3. Check the log file for details: {log_file_path}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    except ImportError as e:
        logger.error("Import error: %s", e, exc_info=True)
        # Flush logs immediately
        for handler in logging.getLogger().handlers:
            handler.flush()
        print(f"\n❌ Import Error: {e}")
        print("\nThis usually means a required library is missing.")
        print(f"Check the log file for details: {log_file_path}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("User interrupted (Ctrl+C)")
        print("\n\n👋 Shutting down...")
        sys.exit(0)

    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        # Flush logs immediately
        for handler in logging.getLogger().handlers:
            handler.flush()
        print(f"\n❌ Unexpected Error: {e}")
        print()
        print("Full error details:")
        traceback.print_exc()
        print()
        print(f"📝 Full log saved to: {log_file_path}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Fatal error in main: %s", e, exc_info=True)
        # Flush logs immediately
        for handler in logging.getLogger().handlers:
            handler.flush()
        print(f"\n💥 FATAL ERROR: {e}")
        print(f"📝 Check log file: {log_file_path}")
        input("\nPress Enter to exit...")
        sys.exit(1)
