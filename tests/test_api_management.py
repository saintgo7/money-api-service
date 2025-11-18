"""Tests for API key management."""
import pytest
from src.core.api_management import APIKeyManager, generate_api_key, hash_api_key


class TestAPIKeyGeneration:
    """Test API key generation."""

    def test_generate_api_key(self):
        """Test API key generation format."""
        key = generate_api_key()
        assert key.startswith("sk_")
        assert len(key) > 20

    def test_hash_api_key(self):
        """Test API key hashing."""
        key = "sk_test_key_123"
        hashed = hash_api_key(key)

        assert hashed != key
        assert len(hashed) == 64  # SHA-256 hex digest

        # Same key should produce same hash
        assert hash_api_key(key) == hashed


@pytest.mark.asyncio
class TestAPIKeyManager:
    """Test API key manager."""

    async def test_create_api_key(self, db_session, test_user):
        """Test creating API key."""
        manager = APIKeyManager(db_session)

        raw_key, api_key = await manager.create_api_key(
            user_id=str(test_user.id),
            name="Test Key",
            permissions=["text:*", "image:*"],
            rate_limit=100
        )

        assert raw_key.startswith("sk_")
        assert api_key.name == "Test Key"
        assert api_key.rate_limit == 100
        assert "text:*" in api_key.permissions

    async def test_verify_api_key(self, db_session, test_api_key):
        """Test verifying API key."""
        raw_key, _ = test_api_key
        manager = APIKeyManager(db_session)

        key_data = await manager.verify_api_key(raw_key)

        assert key_data is not None
        assert "user_id" in key_data
        assert "api_key_id" in key_data
        assert key_data["rate_limit"] == 60

    async def test_verify_invalid_key(self, db_session):
        """Test verifying invalid API key."""
        manager = APIKeyManager(db_session)

        key_data = await manager.verify_api_key("sk_invalid_key")

        assert key_data is None

    async def test_revoke_api_key(self, db_session, test_api_key):
        """Test revoking API key."""
        raw_key, api_key = test_api_key
        manager = APIKeyManager(db_session)

        await manager.revoke_api_key(str(api_key.id))

        # Key should no longer verify
        key_data = await manager.verify_api_key(raw_key)
        assert key_data is None
