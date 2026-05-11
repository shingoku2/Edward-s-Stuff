"""
Omnix License Validator
Checks Supabase for a valid active subscription.
Runs on startup and every 24h.
"""
from __future__ import annotations

import logging
import os
import time
import hashlib
import platform
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


def get_machine_id() -> str:
    """Deterministic per-machine fingerprint (no PII)."""
    node = platform.node()
    proc = platform.processor()
    raw = f"{node}:{proc}:{platform.machine()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


class LicenseValidator:
    """
    Validates license key against Supabase `licenses` table.

    Table schema expected:
        licenses (
            id          uuid primary key,
            key         text unique not null,
            email       text,
            status      text,           -- 'active' | 'expired' | 'cancelled'
            expires_at  timestamptz,
            seat_limit  int default 1,
            created_at  timestamptz
        )
    """

    GRACE_PERIOD_HOURS = 72   # Offline grace period

    def __init__(self, supabase_url: str, anon_key: str):
        self.url = supabase_url.rstrip("/")
        self.anon_key = anon_key
        self._last_valid: Optional[float] = None

    def validate(self, license_key: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, message).
        Falls back to grace period if Supabase is unreachable.
        """
        try:
            import requests
            resp = requests.get(
                f"{self.url}/rest/v1/licenses",
                params={"key": f"eq.{license_key}", "select": "status,expires_at"},
                headers={
                    "apikey": self.anon_key,
                    "Authorization": f"Bearer {self.anon_key}",
                },
                timeout=8,
            )
            if resp.status_code != 200:
                return self._grace_fallback("Supabase returned non-200")

            data = resp.json()
            if not data:
                return False, "License key not found."

            record = data[0]
            if record.get("status") != "active":
                return False, f"License is {record.get('status', 'unknown')}."

            # Check expiry
            expires_at = record.get("expires_at")
            if expires_at:
                from datetime import datetime, timezone
                exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if exp < datetime.now(timezone.utc):
                    return False, "License expired."

            self._last_valid = time.time()
            return True, "License valid."

        except Exception as e:
            logger.warning(f"License check failed: {e}")
            return self._grace_fallback(str(e))

    def _grace_fallback(self, reason: str) -> Tuple[bool, str]:
        if self._last_valid and (time.time() - self._last_valid) < self.GRACE_PERIOD_HOURS * 3600:
            logger.info("License: offline grace period active")
            return True, "Offline mode (grace period)."
        return False, f"Cannot verify license: {reason}"


# Singleton
_validator: Optional[LicenseValidator] = None


def get_validator(supabase_url: str = "", anon_key: str = "") -> LicenseValidator:
    global _validator
    if _validator is None:
        _validator = LicenseValidator(supabase_url, anon_key)
    return _validator