"""Tests for Management API endpoints."""
import pytest


@pytest.mark.asyncio
class TestManagementAPI:
    """Test management endpoints."""

    async def test_create_user(self, client):
        """Test user creation."""
        response = client.post(
            "/api/v1/manage/users",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["plan"] == "free"
        assert data["credit_balance"] == 5.0

    async def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get(
            "/api/v1/manage/users/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "credit_balance" in data
        assert "plan" in data

    async def test_create_api_key(self, client, auth_headers):
        """Test creating API key."""
        response = client.post(
            "/api/v1/manage/api-keys",
            headers=auth_headers,
            json={
                "name": "Production Key",
                "permissions": ["text:*"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Production Key"
        assert "key" in data  # Raw key only shown once
        assert data["key"].startswith("sk_")

    async def test_list_api_keys(self, client, auth_headers):
        """Test listing API keys."""
        response = client.get(
            "/api/v1/manage/api-keys",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test key

    async def test_get_usage_stats(self, client, auth_headers):
        """Test getting usage statistics."""
        response = client.get(
            "/api/v1/manage/usage?period=30d",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_cost" in data
        assert "by_endpoint" in data
        assert data["period"] == "30d"

    async def test_add_credits(self, client, auth_headers):
        """Test adding credits."""
        response = client.post(
            "/api/v1/manage/credits",
            headers=auth_headers,
            json={"amount": 50.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert "new_balance" in data
        assert data["new_balance"] >= 50.0
