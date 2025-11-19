"""Encrypted credential storage utilities for the Gaming AI Assistant."""

from __future__ import annotations

import base64
import getpass
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)

_DEFAULT_SERVICE_NAME = "gaming_ai_assistant"
_DEFAULT_CREDENTIAL_FILE = "credentials.enc"
_KEYRING_KEY = "encryption_key"
_FALLBACK_KEY_FILE = "master.key"  # Now stores encrypted key + salt, not plaintext
_PBKDF2_ITERATIONS = 480000  # OWASP recommended minimum (2023)
_SALT_LENGTH = 32  # 256 bits


class CredentialStoreError(Exception):
    """Base exception for credential store errors."""


class CredentialDecryptionError(CredentialStoreError):
    """Raised when stored credentials cannot be decrypted."""


class KeyringUnavailableError(CredentialStoreError):
    """Raised when keyring is unavailable and no password is provided."""


class CredentialStore:
    """Encrypted credential storage backed by the system keyring.

    Falls back to password-based encryption (PBKDF2) if keyring is unavailable.
    The fallback is secure but requires user to enter a master password.
    """

    def __init__(
        self,
        base_dir: Optional[Union[Path, str]] = None,
        service_name: str = _DEFAULT_SERVICE_NAME,
        credential_filename: str = _DEFAULT_CREDENTIAL_FILE,
        master_password: Optional[str] = None,
        allow_password_prompt: bool = True,
    ) -> None:
        """Initialize the credential store.

        Args:
            base_dir: Directory for storing encrypted credentials
            service_name: Service name for keyring
            credential_filename: Name of encrypted credentials file
            master_password: Master password for fallback encryption (if keyring unavailable)
            allow_password_prompt: If True, prompt for password when keyring fails

        Raises:
            KeyringUnavailableError: If keyring is unavailable and no password provided/allowed
        """
        self.service_name = service_name
        self.base_dir = Path(base_dir) if base_dir else Path.home() / ".gaming_ai_assistant"
        self.credential_path = self.base_dir / credential_filename
        self._cipher: Optional[Fernet] = None
        self._master_password = master_password
        self._allow_password_prompt = allow_password_prompt

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

    # Legacy API wrappers for backward compatibility with tests
    def set_credential(self, service: str, key: str, value: str) -> None:
        """Store a single credential (legacy API wrapper)."""
        full_key = f"{service}:{key}"
        self.save_credentials({full_key: value})

    def get_credential(self, service: str, key: str) -> Optional[str]:
        """Retrieve a single credential (legacy API wrapper)."""
        full_key = f"{service}:{key}"
        return self.get(full_key)

    def delete_credential(self, service: str, key: str) -> None:
        """Delete a single credential (legacy API wrapper)."""
        full_key = f"{service}:{key}"
        self.delete(full_key)

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
        """Load or create the Fernet encryption key.

        First tries the system keyring. If unavailable, falls back to
        password-based encryption with PBKDF2.

        Returns:
            Fernet encryption key (32 bytes, base64-encoded)

        Raises:
            KeyringUnavailableError: If keyring fails and no password available
        """
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
            logger.warning("Keyring unavailable (%s); using password-based fallback", exc)
            return self._fallback_store_key(key_bytes)

    def _read_keyring_key(self) -> Optional[bytes]:
        """Read encryption key from system keyring or password-based fallback."""
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
        """Store encryption key using password-based encryption (PBKDF2).

        SECURITY: This method uses PBKDF2 with 480,000 iterations (OWASP 2023)
        to derive an encryption key from a master password. The Fernet key is
        encrypted with this derived key and stored with its salt.

        This is MUCH more secure than storing the key in plaintext.

        Args:
            key_bytes: The Fernet key to encrypt and store

        Returns:
            The same key_bytes (for convenience)

        Raises:
            KeyringUnavailableError: If no password is available
        """
        password = self._get_master_password()
        if not password:
            raise KeyringUnavailableError(
                "System keyring is unavailable and no master password was provided. "
                "Cannot securely store credentials. Please fix your system keyring "
                "or provide a master password via environment variable OMNIX_MASTER_PASSWORD."
            )

        # Generate a random salt
        salt = os.urandom(_SALT_LENGTH)

        # Derive a key from the password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=_PBKDF2_ITERATIONS,
        )
        password_key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))

        # Encrypt the Fernet key with the password-derived key
        cipher = Fernet(password_key)
        encrypted_key = cipher.encrypt(key_bytes)

        # Store salt + encrypted key
        fallback_path = self.base_dir / _FALLBACK_KEY_FILE
        data = {
            "salt": base64.b64encode(salt).decode("utf-8"),
            "encrypted_key": base64.b64encode(encrypted_key).decode("utf-8"),
            "iterations": _PBKDF2_ITERATIONS,
        }
        with open(fallback_path, "w") as fh:
            json.dump(data, fh)

        self._set_permissions(fallback_path, 0o600)
        logger.info("Stored encryption key using password-based encryption (PBKDF2)")
        logger.warning(
            "WARNING: Keyring is unavailable. Credentials are protected by your master password. "
            "Do NOT lose this password or you will lose access to all stored credentials!"
        )
        return key_bytes

    def _load_fallback_key(self) -> Optional[bytes]:
        """Load encryption key from password-based fallback storage."""
        fallback_path = self.base_dir / _FALLBACK_KEY_FILE
        if not fallback_path.exists():
            return None

        try:
            with open(fallback_path, "r") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, IOError) as exc:
            logger.error("Failed to read fallback key file: %s", exc)
            return None

        # Check if this is an old plaintext key file (SECURITY ISSUE!)
        if not isinstance(data, dict) or "salt" not in data:
            logger.critical(
                "SECURITY WARNING: Found plaintext master.key file! "
                "This is a critical security vulnerability. The file will be removed and "
                "you will need to re-enter your API keys with a master password."
            )
            # Delete the insecure file
            fallback_path.unlink()
            return None

        password = self._get_master_password()
        if not password:
            raise KeyringUnavailableError(
                "Master password required to decrypt credentials. "
                "Please set OMNIX_MASTER_PASSWORD environment variable or enter it when prompted."
            )

        try:
            salt = base64.b64decode(data["salt"])
            encrypted_key = base64.b64decode(data["encrypted_key"])
            iterations = data.get("iterations", _PBKDF2_ITERATIONS)

            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
            )
            password_key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))

            # Decrypt the Fernet key
            cipher = Fernet(password_key)
            key_bytes = cipher.decrypt(encrypted_key)

            logger.debug("Successfully loaded encryption key from password-based storage")
            return key_bytes

        except (InvalidToken, KeyError) as exc:
            logger.error("Failed to decrypt fallback key (wrong password?): %s", exc)
            raise CredentialDecryptionError(
                "Failed to decrypt master key. Your password may be incorrect."
            ) from exc

    def _get_master_password(self) -> Optional[str]:
        """Get master password from various sources.

        Priority order:
        1. Instance variable (from constructor)
        2. Environment variable OMNIX_MASTER_PASSWORD
        3. Interactive prompt (if allowed)

        Returns:
            Master password or None if not available
        """
        # 1. Check instance variable
        if self._master_password:
            return self._master_password

        # 2. Check environment variable
        env_password = os.environ.get("OMNIX_MASTER_PASSWORD")
        if env_password:
            logger.debug("Using master password from OMNIX_MASTER_PASSWORD environment variable")
            return env_password

        # 3. Interactive prompt (only if allowed and stdin is a TTY)
        if self._allow_password_prompt and os.isatty(0):
            try:
                password = getpass.getpass(
                    "Enter master password for credential encryption: "
                )
                if password:
                    logger.debug("Using master password from interactive prompt")
                    return password
            except (EOFError, KeyboardInterrupt):
                logger.debug("Password prompt cancelled")
                return None

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
