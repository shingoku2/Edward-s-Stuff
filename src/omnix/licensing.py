"""License validation through a narrow Supabase Edge Function."""

from __future__ import annotations

import hashlib
import logging
import platform
import time
import uuid
from typing import Optional, Protocol, Tuple

import requests

logger = logging.getLogger(__name__)


class CredentialBackend(Protocol):
    def get_credential(self, service: str, key: str) -> Optional[str]: ...

    def set_credential(self, service: str, key: str, value: Optional[str]) -> None: ...


def get_machine_id() -> str:
    """Legacy non-PII fingerprint retained for API compatibility."""
    raw = f"{platform.node()}:{platform.processor()}:{platform.machine()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def get_installation_id(store: CredentialBackend | None = None) -> str:
    """Return a random installation identifier, persisted in the secure vault."""
    if store:
        existing = store.get_credential("omnix", "installation_id")
        if existing:
            return existing
    installation_id = str(uuid.uuid4())
    if store:
        store.set_credential("omnix", "installation_id", installation_id)
    return installation_id


class LicenseValidator:
    """Validate entitlements without granting the desktop client table access."""

    GRACE_PERIOD_HOURS = 72

    def __init__(
        self, supabase_url: str, anon_key: str, credential_store: CredentialBackend | None = None
    ):
        self.url = supabase_url.rstrip("/")
        self.anon_key = anon_key
        self.credential_store = credential_store
        self.installation_id = get_installation_id(credential_store)
        self._last_valid = self._load_last_valid()

    @property
    def endpoint(self) -> str:
        return f"{self.url}/functions/v1/validate-license"

    def validate(self, license_key: str) -> Tuple[bool, str]:
        """Return whether the server grants this installation an entitlement."""
        if not self.url or not self.anon_key:
            return self._grace_fallback("Licensing service is not configured")
        if not license_key.strip():
            return False, "License key is required."

        try:
            response = requests.post(
                self.endpoint,
                json={
                    "license_key": license_key.strip(),
                    "installation_id": self.installation_id,
                    "app_version": "3.0.0",
                },
                headers={
                    "apikey": self.anon_key,
                    "Authorization": f"Bearer {self.anon_key}",
                    "Content-Type": "application/json",
                },
                timeout=8,
            )
        except requests.RequestException as exc:
            logger.warning("License service unavailable: %s", exc)
            return self._grace_fallback(str(exc))

        if response.status_code >= 500:
            return self._grace_fallback(f"Licensing service returned {response.status_code}")
        try:
            payload = response.json()
        except ValueError:
            return self._grace_fallback("Licensing service returned invalid data")

        if response.status_code != 200:
            return False, str(payload.get("message", "License validation failed."))
        if not payload.get("valid"):
            return False, str(payload.get("message", "License is not active."))

        self._last_valid = time.time()
        self._save_last_valid(self._last_valid)
        return True, str(payload.get("message", "License valid."))

    def _load_last_valid(self) -> Optional[float]:
        if not self.credential_store:
            return None
        raw = self.credential_store.get_credential("omnix", "license_last_valid")
        try:
            return float(raw) if raw else None
        except ValueError:
            logger.warning("Ignoring invalid cached license validation timestamp")
            return None

    def _save_last_valid(self, timestamp: float) -> None:
        if self.credential_store:
            self.credential_store.set_credential("omnix", "license_last_valid", str(timestamp))

    def _grace_fallback(self, reason: str) -> Tuple[bool, str]:
        if self._last_valid and time.time() - self._last_valid < self.GRACE_PERIOD_HOURS * 3600:
            logger.info("License: offline grace period active")
            return True, "Offline mode (grace period)."
        return False, f"Cannot verify license: {reason}"


_validator: Optional[LicenseValidator] = None


def get_validator(
    supabase_url: str = "",
    anon_key: str = "",
    credential_store: CredentialBackend | None = None,
) -> LicenseValidator:
    global _validator
    if _validator is None:
        _validator = LicenseValidator(supabase_url, anon_key, credential_store)
    return _validator
