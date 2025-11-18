"""Tests for text API endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from fastapi import status


class TestTextAPI:
    """Test text generation API."""

    @pytest.mark.asyncio
    async def test_completion_success(self, client: AsyncClient, api_key: str):
        """Test successful text completion."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            # Mock Claude response
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=AsyncMock(
                content=[AsyncMock(text="This is a test response")],
                usage=AsyncMock(input_tokens=10, output_tokens=20)
            ))
            mock_anthropic.return_value = mock_client

            response = await client.post(
                "/api/v1/text/completions",
                headers={"X-API-Key": api_key},
                json={
                    "prompt": "Hello, world!",
                    "model": "claude-3-sonnet",
                    "max_tokens": 100
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "text" in data
            assert "tokens_used" in data
            assert "cost" in data

    @pytest.mark.asyncio
    async def test_completion_invalid_model(self, client: AsyncClient, api_key: str):
        """Test completion with invalid model."""
        response = await client.post(
            "/api/v1/text/completions",
            headers={"X-API-Key": api_key},
            json={
                "prompt": "Hello",
                "model": "invalid-model",
                "max_tokens": 100
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_completion_missing_api_key(self, client: AsyncClient):
        """Test completion without API key."""
        response = await client.post(
            "/api/v1/text/completions",
            json={
                "prompt": "Hello",
                "model": "claude-3-sonnet",
                "max_tokens": 100
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_completion_rate_limit(self, client: AsyncClient, api_key: str):
        """Test rate limiting."""
        # Make multiple rapid requests
        for i in range(15):
            response = await client.post(
                "/api/v1/text/completions",
                headers={"X-API-Key": api_key},
                json={
                    "prompt": f"Request {i}",
                    "model": "claude-3-sonnet",
                    "max_tokens": 10
                }
            )

            # After rate limit, should get 429
            if i >= 10:
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_chat_completion(self, client: AsyncClient, api_key: str):
        """Test chat completion endpoint."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=AsyncMock(
                content=[AsyncMock(text="Hello! How can I help you?")],
                usage=AsyncMock(input_tokens=15, output_tokens=10)
            ))
            mock_anthropic.return_value = mock_client

            response = await client.post(
                "/api/v1/text/chat",
                headers={"X-API-Key": api_key},
                json={
                    "messages": [
                        {"role": "user", "content": "Hello!"}
                    ],
                    "model": "claude-3-sonnet"
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "tokens_used" in data

    @pytest.mark.asyncio
    async def test_completion_cost_tracking(self, client: AsyncClient, api_key: str, db_session):
        """Test that costs are properly tracked."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=AsyncMock(
                content=[AsyncMock(text="Response")],
                usage=AsyncMock(input_tokens=100, output_tokens=200)
            ))
            mock_anthropic.return_value = mock_client

            response = await client.post(
                "/api/v1/text/completions",
                headers={"X-API-Key": api_key},
                json={
                    "prompt": "Test",
                    "model": "claude-3-sonnet",
                    "max_tokens": 200
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify cost is calculated
            assert data["cost"] > 0
            assert data["tokens_used"] == 300  # 100 input + 200 output

    @pytest.mark.asyncio
    async def test_streaming_completion(self, client: AsyncClient, api_key: str):
        """Test streaming text completion."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            # Mock streaming response
            async def mock_stream():
                yield AsyncMock(delta=AsyncMock(text="Hello "))
                yield AsyncMock(delta=AsyncMock(text="world!"))

            mock_client = AsyncMock()
            mock_client.messages.stream = AsyncMock(return_value=mock_stream())
            mock_anthropic.return_value = mock_client

            async with client.stream(
                "POST",
                "/api/v1/streaming/text/completions",
                headers={"X-API-Key": api_key},
                json={
                    "prompt": "Say hello",
                    "model": "claude-3-sonnet",
                    "max_tokens": 50
                }
            ) as response:
                assert response.status_code == status.HTTP_200_OK
                assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

                # Read stream
                chunks = []
                async for chunk in response.aiter_text():
                    chunks.append(chunk)

                assert len(chunks) > 0
