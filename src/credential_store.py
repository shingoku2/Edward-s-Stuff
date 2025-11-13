"""Credential storage and retrieval utilities."""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CredentialStore:
    """Manage encrypted session tokens for AI providers."""

    DEFAULT_STORE = Path.home() / ".gaming_ai_assistant" / "credentials.json"

    def __init__(
        self,
        storage_path: Optional[str] = None,
        encryption_key: Optional[str] = None,
    ) -> None:
        self.storage_path = Path(
            storage_path
            or os.getenv("CREDENTIAL_STORE_PATH", str(self.DEFAULT_STORE))
        )
        self.storage_path = self.storage_path.expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.encryption_key = encryption_key or os.getenv("CREDENTIAL_SECRET_KEY")
        self._derived_key: Optional[bytes] = None
        self._cache: Optional[Dict[str, Dict[str, str]]] = None

        if self.encryption_key:
            self._derived_key = self._derive_key(self.encryption_key)

    @staticmethod
    def _derive_key(secret: str) -> bytes:
        import hashlib

        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        return digest

    def _decrypt_value(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        # Plain text
        if not value.startswith("enc:") and not value.startswith("b64:"):
            return value

        # Base64 encoded plain text
        if value.startswith("b64:"):
            try:
                decoded = base64.b64decode(value[4:].encode("utf-8"))
                return decoded.decode("utf-8")
            except Exception as exc:  # noqa: BLE001 - want to surface exact issue
                logger.error("Failed to decode base64 credential: %s", exc, exc_info=True)
                return None

        if not self._derived_key:
            logger.warning(
                "Encrypted credential encountered but no encryption key is configured"
            )
            return None

        try:
            payload = base64.b64decode(value[4:].encode("utf-8"))
            decrypted_bytes = bytes(
                b ^ self._derived_key[i % len(self._derived_key)]
                for i, b in enumerate(payload)
            )
            return decrypted_bytes.decode("utf-8")
        except Exception as exc:  # noqa: BLE001 - log actual error
            logger.error("Failed to decrypt credential: %s", exc, exc_info=True)
            return None

    def load_tokens(self, force: bool = False) -> Dict[str, Dict[str, str]]:
        if self._cache is not None and not force:
            return self._cache

        if not self.storage_path.exists():
            logger.info("Credential store not found at %s", self.storage_path)
            self._cache = {}
            return self._cache

        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                raw_data = json.load(handle)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to read credential store: %s", exc, exc_info=True)
            self._cache = {}
            return self._cache

        decrypted: Dict[str, Dict[str, str]] = {}
        for provider, provider_payload in raw_data.items():
            if not isinstance(provider_payload, dict):
                continue

            lower_provider = provider.lower()
            decrypted[lower_provider] = {}
            for token_name, token_value in provider_payload.items():
                decrypted_value = self._decrypt_value(token_value)
                if decrypted_value:
                    decrypted[lower_provider][token_name] = decrypted_value

        self._cache = decrypted
        return self._cache

    def get_provider_tokens(self, provider: str) -> Dict[str, str]:
        tokens = self.load_tokens()
        return tokens.get(provider.lower(), {}).copy()

    def cache_tokens(self, provider: str, tokens: Dict[str, str]) -> None:
        provider_key = provider.lower()
        cache = self.load_tokens(force=True)
        cache[provider_key] = tokens
        self._cache = cache

    def clear_cache(self) -> None:
        self._cache = None


__all__ = ["CredentialStore"]
