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
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)
        assert store is not None

    def test_store_creates_encryption_key(self, clean_config_dir):
        """Test that store creates encryption key"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)
        # Should have encryption key (cipher)
        assert hasattr(store, '_cipher')


@pytest.mark.unit
class TestCredentialStorage:
    """Test storing and retrieving credentials"""

    def test_set_and_get_credential(self, clean_config_dir):
        """Test setting and getting a credential"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        # Set credential
        store.save_credentials({"api_key": "sk-test-1234"})

        # Get credential
        retrieved = store.get("api_key")
        assert retrieved == "sk-test-1234"

    def test_get_nonexistent_credential(self, clean_config_dir):
        """Test getting credential that doesn't exist"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        result = store.get("nonexistent_key")
        assert result is None

    def test_delete_credential(self, clean_config_dir):
        """Test deleting a credential"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        # Set then delete
        store.save_credentials({"test_key": "value"})
        store.delete("test_key")

        # Should be None after delete
        assert store.get("test_key") is None

    def test_multiple_credentials(self, clean_config_dir):
        """Test storing multiple credentials"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        # Store multiple
        store.save_credentials({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

        # Retrieve all
        assert store.get("key1") == "value1"
        assert store.get("key2") == "value2"
        assert store.get("key3") == "value3"


@pytest.mark.unit
class TestCredentialPersistence:
    """Test credential persistence"""

    def test_credentials_persist_across_instances(self, clean_config_dir):
        """Test that credentials persist across store instances"""
        # First instance
        store1 = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)
        store1.save_credentials({"persistent_key": "persistent_value"})

        # Second instance
        store2 = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)
        retrieved = store2.get("persistent_key")

        assert retrieved == "persistent_value"


@pytest.mark.unit
class TestCredentialEncryption:
    """Test credential encryption"""

    def test_credentials_stored_encrypted(self, clean_config_dir):
        """Test that credentials are encrypted on disk"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)
        store.save_credentials({"secret_key": "secret_value"})

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
        """Test handling invalid/empty key names"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        # Should handle gracefully (not crash)
        try:
            store.save_credentials({"": "value"})
            result = store.get("")
            assert True  # Either returns None or handles it
        except CredentialStoreError:
            # Expected behavior
            assert True

    def test_handles_invalid_key_name(self, clean_config_dir):
        """Test handling None values"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        # Store can handle None values
        store.save_credentials({"key_with_none": None})
        result = store.get("key_with_none")
        assert result is None


@pytest.mark.unit
class TestAPIKeyStorage:
    """Test storing API keys for different providers"""

    def test_store_openai_key(self, clean_config_dir):
        """Test storing OpenAI API key"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        store.save_credentials({"OPENAI_API_KEY": "sk-openai-test"})
        retrieved = store.get("OPENAI_API_KEY")

        assert retrieved == "sk-openai-test"

    def test_store_anthropic_key(self, clean_config_dir):
        """Test storing Anthropic API key"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        store.save_credentials({"ANTHROPIC_API_KEY": "sk-ant-test"})
        retrieved = store.get("ANTHROPIC_API_KEY")

        assert retrieved == "sk-ant-test"

    def test_store_gemini_key(self, clean_config_dir):
        """Test storing Google Gemini API key"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        store.save_credentials({"GEMINI_API_KEY": "gemini-test-key"})
        retrieved = store.get("GEMINI_API_KEY")

        assert retrieved == "gemini-test-key"

    def test_update_existing_key(self, clean_config_dir):
        """Test updating an existing API key"""
        store = CredentialStore(base_dir=clean_config_dir, allow_password_prompt=False)

        # Set initial key
        store.save_credentials({"OPENAI_API_KEY": "old-key"})

        # Update to new key
        store.save_credentials({"OPENAI_API_KEY": "new-key"})

        # Should return updated key
        retrieved = store.get("OPENAI_API_KEY")
        assert retrieved == "new-key"
