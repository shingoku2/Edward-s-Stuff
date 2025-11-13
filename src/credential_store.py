"""Encrypted credential storage utilities for the Gaming AI Assistant."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Union

from cryptography.fernet import Fernet, InvalidToken
import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)

_DEFAULT_SERVICE_NAME = "gaming_ai_assistant"
_DEFAULT_CREDENTIAL_FILE = "credentials.enc"
_KEYRING_KEY = "encryption_key"
_FALLBACK_KEY_FILE = "master.key"


class CredentialStoreError(Exception):
    """Base exception for credential store errors."""


class CredentialDecryptionError(CredentialStoreError):
    """Raised when stored credentials cannot be decrypted."""


class CredentialStore:
    """Encrypted credential storage backed by the system keyring."""

    def __init__(
        self,
        base_dir: Optional[Union[Path, str]] = None,
        service_name: str = _DEFAULT_SERVICE_NAME,
        credential_filename: str = _DEFAULT_CREDENTIAL_FILE,
    ) -> None:
        self.service_name = service_name
        self.base_dir = Path(base_dir) if base_dir else Path.home() / ".gaming_ai_assistant"
        self.credential_path = self.base_dir / credential_filename
        self._cipher: Optional[Fernet] = None

        self._ensure_directories()

    def save_credentials(self, values: Dict[str, Optional[str]]) -> None:
        """Persist credentials securely."""
        data = self._load_raw()
        for key, value in values.items():
            if value:
                data[key] = value
            elif key in data:
                del data[key]

        payload = json.dumps(data).encode("utf-8")
        ciphertext = self._get_cipher().encrypt(payload)
        with open(self.credential_path, "wb") as fh:
            fh.write(ciphertext)
        self._set_permissions(self.credential_path, 0o600)
        logger.debug("Stored %d credential(s) in encrypted vault", len(values))

    def load_credentials(self) -> Dict[str, str]:
        """Load all credentials stored in the vault."""
        return self._load_raw()

    def get(self, key: str) -> Optional[str]:
        """Fetch a single credential by key."""
        return self._load_raw().get(key)

    def delete(self, key: str) -> None:
        """Remove a credential from the vault."""
        data = self._load_raw()
        if key in data:
            del data[key]
            payload = json.dumps(data).encode("utf-8")
            ciphertext = self._get_cipher().encrypt(payload)
            with open(self.credential_path, "wb") as fh:
                fh.write(ciphertext)
            self._set_permissions(self.credential_path, 0o600)
            logger.debug("Removed credential %s from vault", key)

    def _load_raw(self) -> Dict[str, str]:
        if not self.credential_path.exists():
            return {}

        try:
            blob = self.credential_path.read_bytes()
        except FileNotFoundError:
            return {}

        if not blob:
            return {}

        try:
            plaintext = self._get_cipher().decrypt(blob)
        except InvalidToken as exc:
            raise CredentialDecryptionError("Failed to decrypt credentials") from exc

        try:
            return json.loads(plaintext.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise CredentialStoreError("Credential store contains invalid JSON") from exc

    def _ensure_directories(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._set_permissions(self.base_dir, 0o700)
        if not self.credential_path.exists():
            self.credential_path.touch()
            self._set_permissions(self.credential_path, 0o600)

    def _get_cipher(self) -> Fernet:
        if self._cipher is None:
            key = self._load_or_create_key()
            self._cipher = Fernet(key)
        return self._cipher

    def _load_or_create_key(self) -> bytes:
        key = self._read_keyring_key()
        if key:
            return key

        key_bytes = Fernet.generate_key()
        key_string = key_bytes.decode("utf-8")

        try:
            keyring.set_password(self.service_name, _KEYRING_KEY, key_string)
            logger.debug("Generated new encryption key and stored it in keyring")
            return key_bytes
        except KeyringError as exc:
            logger.warning("Keyring unavailable (%s); falling back to local key file", exc)
            return self._fallback_store_key(key_bytes)

    def _read_keyring_key(self) -> Optional[bytes]:
        try:
            value = keyring.get_password(self.service_name, _KEYRING_KEY)
        except KeyringError as exc:
            logger.warning("Unable to access keyring: %s", exc)
            return self._load_fallback_key()

        if value:
            return value.encode("utf-8")

        # key not in keyring; try fallback if present
        fallback = self._load_fallback_key()
        if fallback:
            return fallback

        return None

    def _fallback_store_key(self, key_bytes: bytes) -> bytes:
        fallback_path = self.base_dir / _FALLBACK_KEY_FILE
        with open(fallback_path, "wb") as fh:
            fh.write(key_bytes)
        self._set_permissions(fallback_path, 0o600)
        logger.debug("Stored encryption key in fallback key file %s", fallback_path)
        return key_bytes

    def _load_fallback_key(self) -> Optional[bytes]:
        fallback_path = self.base_dir / _FALLBACK_KEY_FILE
        if fallback_path.exists():
            return fallback_path.read_bytes()
        return None

    @staticmethod
    def _set_permissions(path: Path, mode: int) -> None:
        try:
            os.chmod(path, mode)
        except PermissionError:
            logger.debug("Insufficient permissions to set mode %o on %s", mode, path)
        except NotImplementedError:
            logger.debug("chmod not implemented on this platform for %s", path)
        except OSError as exc:
            logger.debug("Failed to set permissions on %s: %s", path, exc)
