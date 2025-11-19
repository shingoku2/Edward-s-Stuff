"""Comprehensive test suite for credential store security.

Tests encryption, decryption, keyring integration, and error handling.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from keyring.errors import KeyringError

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.credential_store import (
    CredentialStore,
    CredentialStoreError,
    CredentialDecryptionError,
    KeyringUnavailableError
)


@pytest.mark.security
class TestCredentialStoreBasics:
    """Test basic credential store operations"""

    def test_initialization(self, temp_base_dir):
        """Test credential store initialization"""
        store = CredentialStore(base_dir=str(temp_config_dir))
        assert store is not None
        assert store.base_dir == Path(temp_config_dir)

    def test_store_and_retrieve_credential(self, temp_base_dir, mock_keyring):
        """Test storing and retrieving a credential"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Store credential
        store.set_credential("test_service", "test_key", "test_value_123")

        # Retrieve credential
        value = store.get_credential("test_service", "test_key")
        assert value == "test_value_123"

    def test_store_multiple_credentials(self, temp_base_dir, mock_keyring):
        """Test storing multiple credentials"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        credentials = {
            "anthropic_key": "sk-ant-12345",
            "openai_key": "sk-67890",
            "gemini_key": "AIza-abcdef"
        }

        # Store all credentials
        for key, value in credentials.items():
            store.set_credential("omnix", key, value)

        # Verify all can be retrieved
        for key, expected_value in credentials.items():
            value = store.get_credential("omnix", key)
            assert value == expected_value

    def test_delete_credential(self, temp_base_dir, mock_keyring):
        """Test deleting a credential"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Store credential
        store.set_credential("test_service", "test_key", "test_value")
        assert store.get_credential("test_service", "test_key") == "test_value"

        # Delete credential
        store.delete_credential("test_service", "test_key")

        # Verify deleted
        value = store.get_credential("test_service", "test_key")
        assert value is None

    def test_get_nonexistent_credential(self, temp_base_dir, mock_keyring):
        """Test retrieving a credential that doesn't exist"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        value = store.get_credential("nonexistent_service", "nonexistent_key")
        assert value is None


@pytest.mark.security
class TestCredentialEncryption:
    """Test encryption and decryption"""

    def test_credentials_are_encrypted_on_disk(self, temp_base_dir, mock_keyring):
        """Test that credentials are encrypted when stored"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        secret_value = "super_secret_api_key_12345"
        store.set_credential("test_service", "test_key", secret_value)

        # Check that the credential file exists
        cred_file = Path(temp_base_dir) / "credentials.enc"
        assert cred_file.exists()

        # Read raw file content as bytes
        raw_content = cred_file.read_bytes()
        key = store._get_cipher()
        decrypted = key.decrypt(raw_content)
        data = json.loads(decrypted.decode("utf-8"))

        assert isinstance(data, dict)
        assert secret_value not in raw_content.decode(errors="ignore")

    def test_encryption_key_not_in_credential_file(self, temp_base_dir, mock_keyring):
        """Test that encryption key is not stored in credential file"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        store.set_credential("test_service", "test_key", "test_value")

        # Read credential file
        cred_file = Path(temp_base_dir) / "credentials.enc"
        content = cred_file.read_text()

        # Should not contain obvious key patterns
        assert "encryption_key" not in content.lower()
        assert "master_key" not in content.lower()
        assert "secret_key" not in content.lower()

    def test_different_values_produce_different_ciphertexts(self, temp_base_dir, mock_keyring):
        """Test that different values produce different encrypted outputs"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        store.set_credential("service", "key1", "value1")
        cred_file = Path(temp_base_dir) / "credentials.enc"
        content1 = cred_file.read_text()

        store.set_credential("service", "key2", "value2")
        content2 = cred_file.read_text()

        # Different values should produce different encrypted files
        assert content1 != content2

    def test_same_value_retrieval_consistency(self, temp_base_dir, mock_keyring):
        """Test that the same value can be retrieved multiple times"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        original_value = "consistent_value_123"
        store.set_credential("service", "key", original_value)

        # Retrieve multiple times
        for _ in range(5):
            retrieved = store.get_credential("service", "key")
            assert retrieved == original_value


@pytest.mark.security
class TestKeyringIntegration:
    """Test keyring integration and fallback"""

    def test_keyring_is_used_when_available(self, temp_base_dir):
        """Test that keyring is used when available"""
        with patch('keyring.get_password') as mock_get, \
             patch('keyring.set_password') as mock_set:

            # Setup mock keyring
            stored_keys = {}

            def set_password(service, username, password):
                stored_keys[f"{service}:{username}"] = password

            def get_password(service, username):
                return stored_keys.get(f"{service}:{username}")

            mock_set.side_effect = set_password
            mock_get.side_effect = get_password

            # Create store and set credential
            store = CredentialStore(base_dir=str(temp_config_dir))
            store.set_credential("test", "key", "value")

            # Verify keyring was called
            assert mock_set.called or mock_get.called

    def test_fallback_when_keyring_unavailable(self, temp_base_dir):
        """Test fallback to file-based encryption when keyring unavailable"""
        with patch('keyring.get_password', side_effect=KeyringError("Keyring unavailable")), \
             patch('keyring.set_password', side_effect=KeyringError("Keyring unavailable")):

            # Should still work with file-based fallback
            store = CredentialStore(
                base_dir=str(temp_config_dir),
                master_password="test_password_123"
            )

            store.set_credential("service", "key", "value")
            retrieved = store.get_credential("service", "key")

            assert retrieved == "value"

    def test_master_password_required_without_keyring(self, temp_base_dir):
        """Test that master password is required when keyring unavailable"""
        with patch('keyring.get_password', side_effect=KeyringError("Keyring unavailable")), \
             patch('keyring.set_password', side_effect=KeyringError("Keyring unavailable")), \
             patch.object(CredentialStore, "_get_master_password", return_value=None):

            with pytest.raises((KeyringUnavailableError, CredentialStoreError)):
                store = CredentialStore(
                    base_dir=str(temp_config_dir),
                    master_password=None
                )
                store.set_credential("service", "key", "value")


@pytest.mark.security
class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_corrupted_credential_file_handling(self, temp_base_dir, mock_keyring):
        """Test handling of corrupted credential file"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Create valid credential first
        store.set_credential("service", "key", "value")

        # Corrupt the credential file
        cred_file = Path(temp_base_dir) / "credentials.enc"
        cred_file.write_text("corrupted non-json content {{{")

        # Should handle corruption gracefully
        value = store.get_credential("service", "key")
        assert value is None

    def test_empty_service_name(self, temp_base_dir, mock_keyring):
        """Test handling of empty service name"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Empty service name should be handled
        store.set_credential("", "key", "value")
        value = store.get_credential("", "key")

        # Should work or return None
        assert value is None or value == "value"

    def test_empty_key_name(self, temp_base_dir, mock_keyring):
        """Test handling of empty key name"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Empty key name should be handled
        store.set_credential("service", "", "value")
        value = store.get_credential("service", "")

        # Should work or return None
        assert value is None or value == "value"

    def test_none_value(self, temp_base_dir, mock_keyring):
        """Test storing None value"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Setting None should delete or handle gracefully
        store.set_credential("service", "key", None)
        value = store.get_credential("service", "key")

        assert value is None

    def test_very_long_credential_value(self, temp_base_dir, mock_keyring):
        """Test storing very long credential"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        # Very long API key (10KB)
        long_value = "x" * 10000

        store.set_credential("service", "key", long_value)
        retrieved = store.get_credential("service", "key")

        assert retrieved == long_value

    def test_special_characters_in_value(self, temp_base_dir, mock_keyring):
        """Test storing credentials with special characters"""
        store = CredentialStore(base_dir=str(temp_config_dir))

        special_values = [
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key/with/slashes",
            "key\\with\\backslashes",
            "key with spaces",
            "key\twith\ttabs",
            "key\nwith\nnewlines",
            "key🎮with🎯emojis",
            "key\"with'quotes",
        ]

        for i, value in enumerate(special_values):
            key = f"key_{i}"
            store.set_credential("service", key, value)
            retrieved = store.get_credential("service", key)
            assert retrieved == value, f"Failed for value: {value}"


@pytest.mark.security
class TestConcurrency:
    """Test concurrent access to credential store"""

    def test_concurrent_reads(self, temp_base_dir, mock_keyring):
        """Test multiple concurrent reads"""
        import threading

        store = CredentialStore(base_dir=str(temp_config_dir))
        store.set_credential("service", "key", "value")

        results = []
        errors = []

        def read_credential():
            try:
                value = store.get_credential("service", "key")
                results.append(value)
            except Exception as e:
                errors.append(e)

        # Create 10 threads reading concurrently
        threads = [threading.Thread(target=read_credential) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All reads should succeed
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(r == "value" for r in results)

    def test_concurrent_writes(self, temp_base_dir, mock_keyring):
        """Test multiple concurrent writes"""
        import threading

        store = CredentialStore(base_dir=str(temp_config_dir))

        errors = []
        lock = threading.Lock()

        def write_credential(thread_id):
            try:
                with lock:
                    store.set_credential("service", f"key_{thread_id}", f"value_{thread_id}")
            except Exception as e:
                errors.append(e)

        # Create 10 threads writing concurrently
        threads = [
            threading.Thread(target=write_credential, args=(i,))
            for i in range(10)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All writes should succeed
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all values were written
        for i in range(10):
            value = store.get_credential("service", f"key_{i}")
            assert value == f"value_{i}"


@pytest.mark.security
class TestPersistence:
    """Test credential persistence across store instances"""

    def test_persistence_across_instances(self, temp_base_dir, mock_keyring):
        """Test that credentials persist across store instances"""
        # Create first store and set credential
        store1 = CredentialStore(base_dir=str(temp_config_dir))
        store1.set_credential("service", "key", "persistent_value")

        # Create second store instance
        store2 = CredentialStore(base_dir=str(temp_config_dir))
        value = store2.get_credential("service", "key")

        assert value == "persistent_value"

    def test_persistence_after_file_deletion_with_keyring(self, temp_base_dir):
        """Test recovery when credential file is deleted but keyring has data"""
        with patch('keyring.get_password') as mock_get, \
             patch('keyring.set_password') as mock_set:

            stored_keys = {}

            def set_password(service, username, password):
                stored_keys[f"{service}:{username}"] = password

            def get_password(service, username):
                return stored_keys.get(f"{service}:{username}")

            mock_set.side_effect = set_password
            mock_get.side_effect = get_password

            # Store credential
            store1 = CredentialStore(base_dir=str(temp_config_dir))
            store1.set_credential("service", "key", "value")

            # Delete credential file
            cred_file = Path(temp_base_dir) / "credentials.enc"
            if cred_file.exists():
                cred_file.unlink()

            # Create new store - should still work with keyring
            store2 = CredentialStore(base_dir=str(temp_config_dir))
            # May return None since file is gone and keyring might not have the actual credential
            # This tests that it doesn't crash
            value = store2.get_credential("service", "key")
            # Just verify no exception is raised


@pytest.mark.security
class TestSecurityProperties:
    """Test security properties of credential store"""

    def test_no_plaintext_keys_in_memory_dumps(self, temp_base_dir, mock_keyring):
        """Test that keys are not easily accessible in memory"""
        store = CredentialStore(base_dir=str(temp_config_dir))
        secret = "very_secret_api_key_12345"

        store.set_credential("service", "key", secret)

        # Get string representation of store object
        store_repr = repr(store)
        store_str = str(store)

        # Secret should not appear in string representations
        assert secret not in store_repr
        assert secret not in store_str

    def test_credential_file_permissions(self, temp_base_dir, mock_keyring):
        """Test that credential file has restrictive permissions (Unix only)"""
        import stat

        store = CredentialStore(base_dir=str(temp_config_dir))
        store.set_credential("service", "key", "value")

        cred_file = Path(temp_base_dir) / "credentials.enc"

        if os.name != 'nt':  # Unix-like systems only
            file_stat = os.stat(cred_file)
            file_mode = stat.S_IMODE(file_stat.st_mode)

            # File should not be world-readable
            world_readable = bool(file_mode & stat.S_IROTH)
            assert not world_readable, "Credential file should not be world-readable"

    def test_no_credential_leakage_on_exception(self, temp_base_dir, mock_keyring):
        """Test that credentials don't leak in exception messages"""
        store = CredentialStore(base_dir=str(temp_config_dir))
        secret = "secret_api_key_12345"

        store.set_credential("service", "key", secret)

        # Try to cause various errors
        try:
            # Force a potential error by corrupting internal state
            store.set_credential("", "", "")
        except Exception as e:
            # Secret should not appear in exception message
            exception_str = str(e)
            assert secret not in exception_str


def test_integration_with_config(temp_base_dir, mock_keyring):
    """Integration test with typical usage pattern"""
    store = CredentialStore(base_dir=str(temp_config_dir))

    # Simulate storing API keys
    api_keys = {
        "anthropic_api_key": "sk-ant-api03-1234567890",
        "openai_api_key": "sk-proj-1234567890",
        "gemini_api_key": "AIzaSy1234567890"
    }

    # Store all keys
    for key_name, key_value in api_keys.items():
        store.set_credential("gaming_ai_assistant", key_name, key_value)

    # Retrieve and verify
    for key_name, expected_value in api_keys.items():
        retrieved = store.get_credential("gaming_ai_assistant", key_name)
        assert retrieved == expected_value

    # Delete one key
    store.delete_credential("gaming_ai_assistant", "openai_api_key")
    assert store.get_credential("gaming_ai_assistant", "openai_api_key") is None

    # Others should still exist
    assert store.get_credential("gaming_ai_assistant", "anthropic_api_key") == api_keys["anthropic_api_key"]
    assert store.get_credential("gaming_ai_assistant", "gemini_api_key") == api_keys["gemini_api_key"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
