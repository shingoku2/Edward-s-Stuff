import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import config
from config import Config
from credential_store import CredentialStore
from game_detector import GameDetector


class DummyCredentialStore:
    def __init__(self, *args, **kwargs):
        self._data = {}

    def load_credentials(self):
        return dict(self._data)

    def save_credentials(self, values):
        for key, value in values.items():
            if value:
                self._data[key] = value
            elif key in self._data:
                del self._data[key]

    def delete(self, key):
        self._data.pop(key, None)


@pytest.mark.unit
def test_config_loads_env_and_defaults(tmp_path, monkeypatch):
    env_file = tmp_path / "test.env"
    env_file.write_text(
        "\n".join(
            [
                "AI_PROVIDER=openai",
                "OVERLAY_HOTKEY=ctrl+alt+z",
                "CHECK_INTERVAL=7",
                "OPENAI_API_KEY=sk-env-123",
            ]
        )
    )

    monkeypatch.setenv("OMNIX_MASTER_PASSWORD", "test-pass")
    monkeypatch.setattr(config, "CredentialStore", lambda *args, **kwargs: DummyCredentialStore())

    cfg = Config(env_file=str(env_file), config_path=str(tmp_path / "cfg.json"), require_keys=False)

    assert cfg.ai_provider == "openai"
    assert cfg.overlay_hotkey == "ctrl+alt+z"
    assert cfg.check_interval == 7
    assert cfg.openai_api_key == "sk-env-123"


@pytest.mark.unit
def test_config_save_and_recovers_from_corrupted_json(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIX_MASTER_PASSWORD", "test-pass")
    monkeypatch.delenv("OVERLAY_HOTKEY", raising=False)
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.setattr(config, "CredentialStore", lambda *args, **kwargs: DummyCredentialStore())

    cfg_path = tmp_path / "config.json"
    cfg = Config(config_path=str(cfg_path), require_keys=False)
    cfg.overlay_hotkey = "ctrl+alt+p"

    assert cfg.save()
    saved = json.loads(cfg_path.read_text())
    assert saved["overlay_hotkey"] == "ctrl+alt+p"

    cfg_path.write_text("{bad json")
    cfg_reloaded = Config(config_path=str(cfg_path), require_keys=False)
    assert cfg_reloaded.overlay_hotkey == "ctrl+shift+g"


@pytest.mark.unit
def test_credential_store_encrypts_and_decrypts(tmp_path, monkeypatch, mock_keyring):
    monkeypatch.setenv("OMNIX_MASTER_PASSWORD", "unit-pass")

    store = CredentialStore(base_dir=tmp_path, master_password="unit-pass", allow_password_prompt=False)
    store.save_credentials({"TEST_KEY": "super-secret"})

    loaded = store.load_credentials()
    assert loaded["TEST_KEY"] == "super-secret"
    assert store.get("TEST_KEY") == "super-secret"


@pytest.mark.unit
def test_credential_store_keyring_fallback_uses_master_password(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIX_MASTER_PASSWORD", "fallback-pass")

    with patch("credential_store.keyring.get_keyring", side_effect=Exception("no keyring")):
        store = CredentialStore(base_dir=tmp_path, allow_password_prompt=False)

    store.save_credentials({"API": "value"})
    assert (Path(tmp_path) / "master.key").exists()
    assert store.load_credentials()["API"] == "value"


@pytest.mark.unit
def test_game_detector_identifies_running_game(monkeypatch):
    import game_detector as gd

    fake_proc = MagicMock()
    fake_proc.info = {"name": "eldenring.exe", "pid": 42, "exe": "/games/eldenring.exe"}
    fake_proc.as_dict.return_value = fake_proc.info

    monkeypatch.setattr(gd.psutil, "process_iter", lambda attrs=None: [fake_proc])

    detector = gd.GameDetector()
    result = detector.detect_running_game()

    assert result is not None
    assert result["name"] == "Elden Ring"
    assert result["pid"] == 42
