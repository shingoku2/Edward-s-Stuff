"""
Gaming AI Assistant - Main Application Entry Point
"""

import logging
from pathlib import Path
from datetime import datetime
import sys
import traceback

# Add src to path for executable compatibility
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils import setup_logging, cleanup_logging
import atexit

log_file_path = setup_logging()
logger = logging.getLogger(__name__)

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
        logger.info("  Ollama host: %s", config.ollama_host)
        logger.info("  Configuration complete: %s", config.is_configured())

        print("[OK] Configuration loaded")
        print(f"  AI Provider: {config.ai_provider}")
        print(f"  Hotkey: {config.overlay_hotkey}")
        print(f"  Ollama host: {config.ollama_host}")
        if not config.is_configured():
            print("  ⚠️  Ollama not configured - Settings dialog will open")
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
            print(
                "[INFO] AI assistant will be initialized after you configure credentials"
            )
            print()

        logger.info("Step 4: Scanning for running games...")
        print("Scanning for running games...")

        game = game_detector.detect_running_game()
        if game:
            logger.info(
                "Detected game: %s (PID: %s)",
                game.get("name"),
                game.get("pid", "unknown"),
            )
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

        # ── License check ────────────────────────────────────────────────────────
        import os
        from src.licensing import get_validator

        _license_key = credential_store.get_credential("omnix", "license_key") or os.getenv("OMNIX_LICENSE_KEY", "")

        _supabase_url = os.getenv("SUPABASE_URL", "")
        _supabase_key = os.getenv("SUPABASE_ANON_KEY", "")

        # Skip licensing in dev mode
        _dev_mode = os.getenv("OMNIX_DEV_MODE", "").lower() in ("1", "true", "yes")

        if not _dev_mode and _supabase_url:
            _validator = get_validator(_supabase_url, _supabase_key)
            _valid, _msg = _validator.validate(_license_key) if _license_key else (False, "No key")

            if not _valid:
                from src.license_dialog import LicenseDialog
                dlg = LicenseDialog(_validator)
                if dlg.exec() != dlg.DialogCode.Accepted:
                    logger.warning("License not activated. Exiting.")
                    sys.exit(1)

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
        print("2. Edit .env and configure Ollama:")
        print("   OLLAMA_HOST=http://localhost:11434")
        print("   OLLAMA_MODEL=llama3")
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
