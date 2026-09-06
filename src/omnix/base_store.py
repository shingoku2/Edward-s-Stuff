"""
BaseStore: shared helpers for persistent JSON-backed stores.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


class BaseStore(Generic[T]):
    """
    Provide common helpers for JSON-backed stores.

    Responsibilities:
    - Resolve and create the configuration directory
    - Manage per-store subdirectories
    - Provide safe JSON load/save utilities with logging
    - Offer convenience helpers for enumerating files
    """

    def __init__(self, store_name: str = "", config_dir: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        default_config_dir = os.getenv(
            "OMNIX_CONFIG_DIR", os.path.expanduser("~/.gaming_ai_assistant")
        )
        self.config_dir = Path(config_dir or default_config_dir)
        self.store_name = store_name
        self.base_dir = self.config_dir / store_name if store_name else self.config_dir
        self._ensure_dir(self.base_dir)

    def _ensure_dir(self, path: Path) -> Path:
        """Create the directory if it does not exist."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_subdir(self, relative: str) -> Path:
        """Create and return a subdirectory under the config dir."""
        return self._ensure_dir(self.config_dir / relative)

    def _json_load(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON data from disk."""
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return None
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("Failed to read %s: %s", file_path, exc)
            return None

    def _json_save(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Persist JSON data to disk atomically (write to a temp file in the
        same directory, then rename over the target). A crash or forced kill
        mid-write leaves the original file intact instead of truncated."""
        temp_path: Optional[Path] = None
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w",
                delete=False,
                dir=file_path.parent,
                encoding="utf-8",
                suffix=".tmp",
            ) as handle:
                temp_path = Path(handle.name)
                json.dump(data, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, file_path)
            return True
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("Failed to write %s: %s", file_path, exc)
            return False
        finally:
            if temp_path is not None and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    def _delete_file(self, file_path: Path) -> bool:
        """Delete a file if it exists."""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("Failed to delete %s: %s", file_path, exc)
            return False

    def iter_json_files(self, directory: Optional[Path] = None) -> Iterator[Path]:
        """Yield JSON files for the configured store."""
        dir_path = directory or self.base_dir
        if not dir_path.exists():
            return iter(())
        return (path for path in dir_path.glob("*.json") if path.is_file())
