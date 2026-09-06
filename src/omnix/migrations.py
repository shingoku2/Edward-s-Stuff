"""Versioned, crash-safe migrations for Omnix user data."""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 3
STATE_FILE = ".migration-state.json"


class MigrationError(RuntimeError):
    """Raised when user data cannot be migrated safely."""


@dataclass(frozen=True)
class MigrationResult:
    previous_version: int
    current_version: int
    backup_dir: Path | None

    @property
    def changed(self) -> bool:
        return self.previous_version != self.current_version


def _atomic_json(path: Path, value: Any) -> None:
    """Write JSON without exposing a partially-written destination file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


class MigrationManager:
    """Upgrade one Omnix profile directory while retaining a recovery copy."""

    _USER_ENTRIES = (
        "config.json",
        "keybinds.json",
        "macros.json",
        "theme.json",
        "game_profiles.json",
        "knowledge_packs.json",
        "credentials.enc",
        "macros",
        "knowledge_packs",
        "knowledge_sources",
        "knowledge_index",
        "session_logs",
    )

    def __init__(self, config_dir: str | Path, target_version: int = CURRENT_SCHEMA_VERSION):
        self.config_dir = Path(config_dir).expanduser()
        self.target_version = target_version
        self.state_path = self.config_dir / STATE_FILE
        self._steps: dict[int, Callable[[], None]] = {
            1: self._initialize_profile,
            2: self._normalize_macros,
            3: self._normalize_config,
        }

    def migrate(self) -> MigrationResult:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        previous = self._read_version()
        if previous > self.target_version:
            raise MigrationError(
                f"Profile schema {previous} is newer than this app supports "
                f"({self.target_version})."
            )
        if previous == self.target_version:
            return MigrationResult(previous, previous, None)

        backup = self._backup(previous)
        try:
            for version in range(previous + 1, self.target_version + 1):
                step = self._steps.get(version)
                if step is None:
                    raise MigrationError(f"Missing migration step for schema {version}")
                step()
                self._write_state(version)
        except Exception as exc:
            logger.exception("Profile migration failed; backup retained at %s", backup)
            raise MigrationError(f"Could not upgrade Omnix profile: {exc}") from exc

        logger.info("Migrated Omnix profile from schema %s to %s", previous, self.target_version)
        return MigrationResult(previous, self.target_version, backup)

    def _read_version(self) -> int:
        if not self.state_path.exists():
            return 0
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            return int(state.get("schema_version", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise MigrationError(f"Invalid migration state at {self.state_path}: {exc}") from exc

    def _backup(self, previous_version: int) -> Path | None:
        sources = [self.config_dir / name for name in self._USER_ENTRIES]
        sources.append(self.state_path)
        sources = [path for path in sources if path.exists()]
        if not sources:
            return None

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = self.config_dir / "backups" / f"schema-{previous_version}-{stamp}"
        destination.mkdir(parents=True, exist_ok=False)
        for source in sources:
            target = destination / source.name
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        return destination

    def _write_state(self, version: int) -> None:
        _atomic_json(
            self.state_path,
            {
                "schema_version": version,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _initialize_profile(self) -> None:
        """Schema 1 records existing profiles without changing their contents."""

    def _normalize_macros(self) -> None:
        path = self.config_dir / "macros.json"
        if not path.exists():
            return
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            normalized = {
                str(item.get("id", f"macro-{index}")): item
                for index, item in enumerate(value)
                if isinstance(item, dict)
            }
            _atomic_json(path, normalized)

    def _normalize_config(self) -> None:
        path = self.config_dir / "config.json"
        if not path.exists():
            return
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise MigrationError("config.json must contain a JSON object")
        value["schema_version"] = CURRENT_SCHEMA_VERSION
        if value.get("ai_provider") in {"openai", "anthropic", "gemini"}:
            value["ai_provider"] = "ollama"
        _atomic_json(path, value)


def migrate_user_data(config_dir: str | Path) -> MigrationResult:
    """Run every pending migration for a profile directory."""
    return MigrationManager(config_dir).migrate()
