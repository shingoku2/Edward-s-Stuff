"""
Unit tests for licensing validation.

Tests LicenseValidator for valid/invalid keys and offline grace period.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from src.licensing import LicenseValidator, get_machine_id


@pytest.mark.unit
class TestLicenseValidator:
    """Test LicenseValidator class."""

    def test_validator_initialization(self):
        """Test validator initializes with URL and key."""
        validator = LicenseValidator("https://example.supabase.co", "test-anon-key")
        assert validator.url == "https://example.supabase.co"
        assert validator.anon_key == "test-anon-key"
        assert validator._last_valid is None

    def test_validator_url_rstrip(self):
        """Test URL is properly stripped of trailing slashes."""
        validator = LicenseValidator("https://example.supabase.co/", "key")
        assert validator.url == "https://example.supabase.co"

    def test_grace_period_hours_constant(self):
        """Test grace period is set correctly."""
        assert LicenseValidator.GRACE_PERIOD_HOURS == 72


@pytest.mark.unit
class TestLicenseValidation:
    """Test license key validation logic."""

    def test_validate_valid_license_key(self):
        """Test validation passes with valid active license from Supabase."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        # Mock successful response with active status
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"status": "active", "expires_at": "2030-12-31T23:59:59Z"}
        ]

        with patch('requests.get', return_value=mock_response):
            is_valid, message = validator.validate("valid-license-key")

        assert is_valid is True
        assert "valid" in message.lower()
        # _last_valid should be set
        assert validator._last_valid is not None

    def test_validate_invalid_license_key_not_found(self):
        """Test validation fails when key not found in database."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        # Mock empty response (key not found)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch('requests.get', return_value=mock_response):
            is_valid, message = validator.validate("nonexistent-key")

        assert is_valid is False
        assert "not found" in message.lower()

    def test_validate_expired_license(self):
        """Test validation fails for expired license."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        # Mock response with expired status
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"status": "active", "expires_at": "2020-01-01T00:00:00Z"}
        ]

        with patch('requests.get', return_value=mock_response):
            is_valid, message = validator.validate("expired-key")

        assert is_valid is False
        assert "expired" in message.lower()

    def test_validate_cancelled_license(self):
        """Test validation fails for cancelled license."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"status": "cancelled", "expires_at": None}
        ]

        with patch('requests.get', return_value=mock_response):
            is_valid, message = validator.validate("cancelled-key")

        assert is_valid is False
        assert "cancelled" in message.lower()

    def test_validate_non_200_response(self):
        """Test validation falls back to grace period on non-200 response."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch('requests.get', return_value=mock_response):
            is_valid, message = validator.validate("some-key")

        # Should fall back to grace period
        assert is_valid is False
        assert "cannot verify" in message.lower()

    def test_validate_network_error_triggers_grace_fallback(self):
        """Test network error triggers grace period fallback."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        with patch('requests.get', side_effect=Exception("Network unavailable")):
            is_valid, message = validator.validate("some-key")

        # Should return False (no prior valid check)
        assert is_valid is False


@pytest.mark.unit
class TestLicenseGracePeriod:
    """Test offline grace period functionality."""

    def test_grace_period_active_after_prior_valid_check(self):
        """Test grace period allows validation after recent successful check."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        # Set _last_valid to recent time (within grace period)
        validator._last_valid = time.time() - (24 * 3600)  # 24 hours ago

        # Network error - but should pass due to grace period
        with patch('requests.get', side_effect=Exception("Offline")):
            is_valid, message = validator.validate("offline-key")

        assert is_valid is True
        assert "offline" in message.lower() or "grace" in message.lower()

    def test_grace_period_expired_after_long_offline(self):
        """Test grace period expires after 72 hours."""
        validator = LicenseValidator("https://example.supabase.co", "test-key")

        # Set _last_valid to 73 hours ago (beyond grace period)
        validator._last_valid = time.time() - (73 * 3600)

        with patch('requests.get', side_effect=Exception("Offline")):
            is_valid, message = validator.validate("old-key")

        assert is_valid is False
        assert "cannot verify" in message.lower()


@pytest.mark.unit
class TestMachineId:
    """Test machine ID generation."""

    def test_machine_id_returns_string(self):
        """Test get_machine_id returns a string."""
        machine_id = get_machine_id()
        assert isinstance(machine_id, str)

    def test_machine_id_has_fixed_length(self):
        """Test machine ID has expected length (32 chars)."""
        machine_id = get_machine_id()
        assert len(machine_id) == 32

    def test_machine_id_deterministic(self):
        """Test machine ID is deterministic (same on multiple calls)."""
        id1 = get_machine_id()
        id2 = get_machine_id()
        assert id1 == id2


@pytest.mark.unit
class TestLicenseValidatorSingleton:
    """Test validator singleton behavior."""

    def test_get_validator_returns_instance(self):
        """Test get_validator returns a LicenseValidator instance."""
        from src.licensing import get_validator

        # Clear any existing singleton
        import src.licensing
        src.licensing._validator = None

        validator = get_validator("https://example.supabase.co", "test-key")
        assert isinstance(validator, LicenseValidator)

    def test_get_validator_returns_same_instance(self):
        """Test get_validator returns the same instance on subsequent calls."""
        from src.licensing import get_validator

        # Clear any existing singleton
        import src.licensing
        src.licensing._validator = None

        validator1 = get_validator("https://example.supabase.co", "test-key")
        validator2 = get_validator()

        assert validator1 is validator2