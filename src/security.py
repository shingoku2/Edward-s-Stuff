"""Security utilities for filesystem hardening and secret handling."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterable, Mapping

logger = logging.getLogger(__name__)

_POSIX = os.name != "nt"


def ensure_private_dir(path: Path) -> None:
    """Create a directory with owner-only permissions when possible."""
    path.mkdir(parents=True, exist_ok=True)
    if _POSIX:
        _set_mode(path, 0o700, is_dir=True)


def ensure_private_file(path: Path) -> None:
    """Restrict a file to owner-only access when possible."""
    if not path.exists() or not _POSIX:
        return
    _set_mode(path, 0o600, is_dir=False)


def _set_mode(path: Path, mode: int, *, is_dir: bool) -> None:
    try:
        os.chmod(path, mode)
    except OSError as exc:  # pragma: no cover - defensive guard
        logger.warning("Unable to set secure permissions on %s: %s", path, exc)
        return

    actual_mode = path.stat().st_mode & 0o777
    if actual_mode & 0o077:
        logger.warning(
            "Insecure permissions on %s (%o); expected owner-only %s (0%o)",
            path,
            actual_mode,
            "directory" if is_dir else "file",
            mode,
        )


def enforce_private_paths(paths: Iterable[Path], *, is_dir: bool = False) -> None:
    """Apply owner-only permissions to a batch of files or directories."""
    for path in paths:
        if is_dir:
            ensure_private_dir(path)
        else:
            ensure_private_file(path)


def redact_sensitive_values(
    data: Mapping[str, object], sensitive_keys: Iterable[str]
) -> dict:
    """Return a copy of ``data`` with sensitive keys redacted."""
    targets = {key.lower() for key in sensitive_keys}
    redacted = {}
    for key, value in data.items():
        if key.lower() in targets and value:
            redacted[key] = "***redacted***"
        else:
            redacted[key] = value
    return redacted
