"""Utility helpers for centralized logging and safe execution wrappers."""

from __future__ import annotations

import functools
import logging
import traceback
from pathlib import Path
from typing import Any, Callable, Optional


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure application logging with file and console output.

    Args:
        log_level: Logging level name (e.g., "DEBUG", "INFO").

    Returns:
        Configured logger for the module.
    """

    log_dir = Path.home() / ".gaming_ai_assistant" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "gaming_ai_assistant.log"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)


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

        raise last_exception if last_exception is not None else RuntimeError("Unknown execution error")
