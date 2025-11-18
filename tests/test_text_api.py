"""Tests for Text AI API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
class TestTextAPI:
    """Test text AI endpoints."""

    @patch('src.api.v1.text.call_claude')
    async def test_text_completion(self, mock_claude, client, auth_headers):
        """Test text completion endpoint."""
        # Mock Claude API response
        mock_claude.return_value = ("Generated text response", 150)

        response = client.post(
            "/api/v1/text/completions",
            headers=auth_headers,
            json={
                "prompt": "Write a haiku",
                "model": "claude-sonnet",
                "max_tokens": 100
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "cost" in data
        assert data["model"] == "claude-3-5-sonnet"

    @patch('src.api.v1.text.call_claude')
    async def test_summarize(self, mock_claude, client, auth_headers):
        """Test text summarization."""
        mock_claude.return_value = ("This is a summary", 50)

        response = client.post(
            "/api/v1/text/summarize",
            headers=auth_headers,
            json={
                "text": "Long text to summarize...",
                "length": "short"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "cost" in data

    @patch('src.api.v1.text.call_claude')
    async def test_translate(self, mock_claude, client, auth_headers):
        """Test translation."""
        mock_claude.return_value = ("Hola, ¿cómo estás?", 20)

        response = client.post(
            "/api/v1/text/translate",
            headers=auth_headers,
            json={
                "text": "Hello, how are you?",
                "source_lang": "en",
                "target_lang": "es"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["source_lang"] == "en"
        assert data["target_lang"] == "es"

    async def test_unauthorized_request(self, client):
        """Test request without API key."""
        response = client.post(
            "/api/v1/text/completions",
            json={"prompt": "test"}
        )

        assert response.status_code == 403  # Forbidden (no auth)

    async def test_invalid_model(self, client, auth_headers):
        """Test with invalid model."""
        response = client.post(
            "/api/v1/text/completions",
            headers=auth_headers,
            json={
                "prompt": "test",
                "model": "invalid-model"
            }
        )

        assert response.status_code in [400, 500]
