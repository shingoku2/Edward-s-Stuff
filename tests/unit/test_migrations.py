import json

import pytest

from omnix.migrations import CURRENT_SCHEMA_VERSION, MigrationError, MigrationManager


@pytest.mark.unit
def test_migration_preserves_backup_and_normalizes_legacy_data(tmp_path):
    (tmp_path / "macros.json").write_text(
        json.dumps([{"id": "heal", "name": "Heal"}]), encoding="utf-8"
    )
    (tmp_path / "config.json").write_text(
        json.dumps({"ai_provider": "openai", "overlay_x": 40}), encoding="utf-8"
    )

    result = MigrationManager(tmp_path).migrate()

    assert result.changed
    assert result.current_version == CURRENT_SCHEMA_VERSION
    assert result.backup_dir is not None
    assert (result.backup_dir / "macros.json").exists()
    assert json.loads((tmp_path / "macros.json").read_text())["heal"]["name"] == "Heal"
    config = json.loads((tmp_path / "config.json").read_text())
    assert config == {
        "ai_provider": "ollama",
        "overlay_x": 40,
        "schema_version": CURRENT_SCHEMA_VERSION,
    }


@pytest.mark.unit
def test_migration_is_idempotent(tmp_path):
    first = MigrationManager(tmp_path).migrate()
    second = MigrationManager(tmp_path).migrate()

    assert first.changed
    assert not second.changed
    assert second.backup_dir is None


@pytest.mark.unit
def test_newer_profile_is_rejected(tmp_path):
    (tmp_path / ".migration-state.json").write_text(
        json.dumps({"schema_version": CURRENT_SCHEMA_VERSION + 1}), encoding="utf-8"
    )

    with pytest.raises(MigrationError, match="newer"):
        MigrationManager(tmp_path).migrate()
