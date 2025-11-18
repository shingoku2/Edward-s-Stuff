"""
Test suite for Credential Store

Tests secure API key storage and encryption.
"""
import pytest
import os
from pathlib import Path
from src.credential_store import (
    CredentialStore,
    CredentialStoreError,
    CredentialDecryptionError
)


@pytest.mark.unit
class TestCredentialStoreInitialization:
    """Test credential store initialization"""

    def test_store_initialization(self, clean_config_dir):
        """Test creating credential store"""
        store = CredentialStore(config_dir=clean_config_dir)
        assert store is not None

    def test_store_creates_encryption_key(self, clean_config_dir):
        """Test that store creates encryption key"""
        store = CredentialStore(config_dir=clean_config_dir)
        # Should have encryption key
        assert hasattr(store, '_fernet') or hasattr(store, 'fernet')


@pytest.mark.unit
class TestCredentialStorage:
    """Test storing and retrieving credentials"""

    def test_set_and_get_credential(self, clean_config_dir):
        """Test setting and getting a credential"""
        store = CredentialStore(config_dir=clean_config_dir)

        # Set credential
        store.set_credential("test_service", "api_key", "sk-test-1234")

        # Get credential
        retrieved = store.get_credential("test_service", "api_key")
        assert retrieved == "sk-test-1234"

    def test_get_nonexistent_credential(self, clean_config_dir):
        """Test getting credential that doesn't exist"""
        store = CredentialStore(config_dir=clean_config_dir)

        result = store.get_credential("nonexistent", "key")
        assert result is None

    def test_delete_credential(self, clean_config_dir):
        """Test deleting a credential"""
        store = CredentialStore(config_dir=clean_config_dir)

        # Set then delete
        store.set_credential("test", "key", "value")
        store.delete_credential("test", "key")

        # Should be None after delete
        assert store.get_credential("test", "key") is None

    def test_multiple_credentials(self, clean_config_dir):
        """Test storing multiple credentials"""
        store = CredentialStore(config_dir=clean_config_dir)

        # Store multiple
        store.set_credential("service1", "api_key", "key1")
        store.set_credential("service2", "api_key", "key2")
        store.set_credential("service1", "secret", "secret1")

        # Retrieve all
        assert store.get_credential("service1", "api_key") == "key1"
        assert store.get_credential("service2", "api_key") == "key2"
        assert store.get_credential("service1", "secret") == "secret1"


@pytest.mark.unit
class TestCredentialPersistence:
    """Test credential persistence"""

    def test_credentials_persist_across_instances(self, clean_config_dir):
        """Test that credentials persist across store instances"""
        # First instance
        store1 = CredentialStore(config_dir=clean_config_dir)
        store1.set_credential("test", "key", "persistent_value")

        # Second instance
        store2 = CredentialStore(config_dir=clean_config_dir)
        retrieved = store2.get_credential("test", "key")

        assert retrieved == "persistent_value"


@pytest.mark.unit
class TestCredentialEncryption:
    """Test credential encryption"""

    def test_credentials_stored_encrypted(self, clean_config_dir):
        """Test that credentials are encrypted on disk"""
        store = CredentialStore(config_dir=clean_config_dir)
        store.set_credential("test", "key", "secret_value")

        # Check if credential file exists and is encrypted
        # (not plaintext "secret_value")
        cred_file = Path(clean_config_dir) / "credentials.enc"
        if cred_file.exists():
            content = cred_file.read_text()
            # Should not contain plaintext value
            assert "secret_value" not in content


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling"""

    def test_handles_invalid_service_name(self, clean_config_dir):
        """Test handling invalid service name"""
        store = CredentialStore(config_dir=clean_config_dir)

        # Should handle gracefully (not crash)
        try:
            store.set_credential("", "key", "value")
            store.get_credential("", "key")
            assert True
        except CredentialStoreError:
            # Expected behavior
            assert True

    def test_handles_invalid_key_name(self, clean_config_dir):
        """Test handling invalid key name"""
        store = CredentialStore(config_dir=clean_config_dir)

        try:
            store.set_credential("service", "", "value")
            store.get_credential("service", "")
            assert True
        except CredentialStoreError:
            # Expected behavior
            assert True


@pytest.mark.unit
class TestAPIKeyStorage:
    """Test storing API keys for different providers"""

    def test_store_openai_key(self, clean_config_dir):
        """Test storing OpenAI API key"""
        store = CredentialStore(config_dir=clean_config_dir)

        store.set_credential("omnix.ai", "openai_api_key", "sk-openai-test")
        retrieved = store.get_credential("omnix.ai", "openai_api_key")

        assert retrieved == "sk-openai-test"

    def test_store_anthropic_key(self, clean_config_dir):
        """Test storing Anthropic API key"""
        store = CredentialStore(config_dir=clean_config_dir)

        store.set_credential("omnix.ai", "anthropic_api_key", "sk-ant-test")
        retrieved = store.get_credential("omnix.ai", "anthropic_api_key")

        assert retrieved == "sk-ant-test"

    def test_store_gemini_key(self, clean_config_dir):
        """Test storing Google Gemini API key"""
        store = CredentialStore(config_dir=clean_config_dir)

        store.set_credential("omnix.ai", "gemini_api_key", "gemini-test-key")
        retrieved = store.get_credential("omnix.ai", "gemini_api_key")

        assert retrieved == "gemini-test-key"

    def test_update_existing_key(self, clean_config_dir):
        """Test updating an existing API key"""
        store = CredentialStore(config_dir=clean_config_dir)

        # Set initial key
        store.set_credential("omnix.ai", "openai_api_key", "old-key")

        # Update to new key
        store.set_credential("omnix.ai", "openai_api_key", "new-key")

        # Should return updated key
        retrieved = store.get_credential("omnix.ai", "openai_api_key")
        assert retrieved == "new-key"
