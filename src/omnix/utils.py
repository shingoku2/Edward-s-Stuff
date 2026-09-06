"""Utility helpers for centralized logging and safe execution wrappers."""

from __future__ import annotations

import functools
import logging
import os
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from omnix.security import ensure_private_dir, ensure_private_file


def setup_logging(log_level: str = "INFO") -> Path:
    """Configure application logging with timestamped file and console output.

    Args:
        log_level: Logging level name (e.g., "DEBUG", "INFO").

    Returns:
        Path to the log file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"gaming_ai_assistant_{timestamp}.log"

    config_dir = Path(os.getenv("OMNIX_CONFIG_DIR", str(Path.home() / ".gaming_ai_assistant")))
    log_dir = config_dir / "logs"

    try:
        ensure_private_dir(log_dir)
    except (PermissionError, OSError) as e:
        fallback_dir = Path(tempfile.gettempdir()) / "omnix-logs"
        print(f"⚠️  Cannot write to application log directory ({e}); using {fallback_dir}")
        ensure_private_dir(fallback_dir)
        log_dir = fallback_dir

    log_file = log_dir / log_filename
    print(f"✓ Log file will be created at: {log_file}")

    try:
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
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

        ensure_private_file(log_file)

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
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
            force=True,
        )
        print("⚠️  Logging to console only")

    return log_file


def cleanup_logging(log_file_path: Optional[Path] = None):
    """Ensure all log handlers are flushed and closed properly."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Application shutting down - closing log file")
    if log_file_path:
        logger.info(f"Final log location: {log_file_path}")
    logger.info("=" * 70)

    # Flush and close all handlers
    for handler in logging.getLogger().handlers[:]:
        handler.flush()
        handler.close()
        logging.getLogger().removeHandler(handler)


def error_handler(
    logger: Optional[logging.Logger] = None,
    *,
    reraise: bool = True,
    default_return: Any = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for consistent error handling and logging.

    Args:
        logger: Optional logger to use. Defaults to the function's module logger.
        reraise: Whether to re-raise the exception after logging.
        default_return: Value to return when ``reraise`` is False.

    Returns:
        Wrapped function with error handling.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                log = logger or logging.getLogger(func.__module__)
                log.error("Error in %s: %s", func.__name__, exc)
                log.debug(traceback.format_exc())

                if reraise:
                    raise
                return default_return

        return wrapper

    return decorator


class SafeExecutor:
    """Safe execution helper with optional retry handling."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self, func: Callable[..., Any], *args: Any, default_return: Any = None, **kwargs: Any
    ) -> Any:
        """Execute a callable with error handling.

        Args:
            func: Callable to execute.
            default_return: Value to return when execution fails.

        Returns:
            Result of ``func`` or ``default_return`` when an exception occurs.
        """

        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Error executing %s: %s", func.__name__, exc)
            self.logger.debug(traceback.format_exc())
            return default_return

    def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        max_retries: int = 3,
        delay: float = 1.0,
        **kwargs: Any,
    ) -> Any:
        """Execute a callable with retry logic.

        Args:
            func: Callable to execute.
            max_retries: Number of retries after the initial attempt.
            delay: Delay between attempts in seconds.

        Returns:
            Result of ``func`` on success.

        Raises:
            Exception: Last exception encountered after exhausting retries.
        """

        import time

        last_exception: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                last_exception = exc
                if attempt < max_retries:
                    self.logger.warning(
                        "Attempt %s failed for %s: %s. Retrying in %.1fs...",
                        attempt + 1,
                        func.__name__,
                        exc,
                        delay,
                    )
                    self.logger.debug(traceback.format_exc())
                    time.sleep(delay)
                else:
                    self.logger.error(
                        "All %s attempts failed for %s: %s", max_retries + 1, func.__name__, exc
                    )
                    self.logger.debug(traceback.format_exc())

        raise (
            last_exception
            if last_exception is not None
            else RuntimeError("Unknown execution error")
        )
