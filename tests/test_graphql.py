"""Tests for GraphQL API."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


class TestGraphQLQueries:
    """Test GraphQL queries."""

    @pytest.mark.asyncio
    async def test_me_query(self, client: AsyncClient, api_key: str):
        """Test 'me' query to get current user."""
        query = """
            query {
                me {
                    id
                    email
                    name
                    plan
                    balance
                }
            }
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": query}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "me" in data["data"]
        assert data["data"]["me"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_api_keys_query(self, client: AsyncClient, api_key: str):
        """Test 'apiKeys' query."""
        query = """
            query {
                apiKeys {
                    id
                    name
                    isActive
                    rateLimit
                }
            }
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": query}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "apiKeys" in data["data"]
        assert len(data["data"]["apiKeys"]) > 0

    @pytest.mark.asyncio
    async def test_usage_stats_query(self, client: AsyncClient, api_key: str):
        """Test 'usageStats' query."""
        query = """
            query {
                usageStats(period: "7d") {
                    totalRequests
                    totalCost
                    avgLatency
                }
            }
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": query}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "usageStats" in data["data"]
        stats = data["data"]["usageStats"]
        assert "totalRequests" in stats
        assert "totalCost" in stats

    @pytest.mark.asyncio
    async def test_recent_usage_query(self, client: AsyncClient, api_key: str):
        """Test 'recentUsage' query."""
        query = """
            query {
                recentUsage(limit: 10) {
                    endpoint
                    timestamp
                    cost
                    statusCode
                }
            }
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": query}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "recentUsage" in data["data"]


class TestGraphQLMutations:
    """Test GraphQL mutations."""

    @pytest.mark.asyncio
    async def test_create_completion_mutation(self, client: AsyncClient, api_key: str):
        """Test 'createCompletion' mutation."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=AsyncMock(
                content=[AsyncMock(text="GraphQL test response")],
                usage=AsyncMock(input_tokens=10, output_tokens=20)
            ))
            mock_anthropic.return_value = mock_client

            mutation = """
                mutation {
                    createCompletion(input: {
                        prompt: "Test prompt"
                        model: "claude-3-sonnet"
                        maxTokens: 100
                    }) {
                        text
                        tokensUsed
                        cost
                    }
                }
            """

            response = await client.post(
                "/graphql",
                headers={"X-API-Key": api_key},
                json={"query": mutation}
            )

            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "createCompletion" in data["data"]
            result = data["data"]["createCompletion"]
            assert result["text"] == "GraphQL test response"
            assert result["tokensUsed"] == 30

    @pytest.mark.asyncio
    async def test_create_api_key_mutation(self, client: AsyncClient, api_key: str):
        """Test 'createApiKey' mutation."""
        mutation = """
            mutation {
                createApiKey(input: {
                    name: "Test GraphQL Key"
                    rateLimit: 100
                }) {
                    id
                    name
                    key
                    rateLimit
                }
            }
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": mutation}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createApiKey" in data["data"]
        result = data["data"]["createApiKey"]
        assert result["name"] == "Test GraphQL Key"
        assert "key" in result

    @pytest.mark.asyncio
    async def test_revoke_api_key_mutation(self, client: AsyncClient, api_key: str):
        """Test 'revokeApiKey' mutation."""
        # First create a key to revoke
        create_mutation = """
            mutation {
                createApiKey(input: {
                    name: "Key to Revoke"
                    rateLimit: 50
                }) {
                    id
                }
            }
        """

        create_response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": create_mutation}
        )

        key_id = create_response.json()["data"]["createApiKey"]["id"]

        # Now revoke it
        revoke_mutation = f"""
            mutation {{
                revokeApiKey(keyId: "{key_id}") {{
                    success
                    message
                }}
            }}
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": revoke_mutation}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["revokeApiKey"]["success"] is True

    @pytest.mark.asyncio
    async def test_unauthorized_graphql(self, client: AsyncClient):
        """Test GraphQL without authentication."""
        query = """
            query {
                me {
                    id
                }
            }
        """

        response = await client.post(
            "/graphql",
            json={"query": query}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_graphql_error_handling(self, client: AsyncClient, api_key: str):
        """Test GraphQL error handling."""
        query = """
            query {
                nonExistentField
            }
        """

        response = await client.post(
            "/graphql",
            headers={"X-API-Key": api_key},
            json={"query": query}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
