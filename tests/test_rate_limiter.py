"""Tests for rate limiting."""
import pytest
import asyncio
from src.core.rate_limiter import RateLimiter


@pytest.mark.asyncio
class TestRateLimiter:
    """Test rate limiter."""

    async def test_within_limit(self):
        """Test requests within rate limit."""
        limiter = RateLimiter()

        # First request should be allowed
        allowed, info = await limiter.check_rate_limit(
            api_key_id="test_key",
            endpoint="/test",
            limit=10
        )

        assert allowed is True
        assert info["limit"] == 10
        assert info["remaining"] == 9

    async def test_exceed_limit(self):
        """Test exceeding rate limit."""
        limiter = RateLimiter()

        # Make requests up to limit
        for _ in range(5):
            allowed, _ = await limiter.check_rate_limit(
                api_key_id="test_key_2",
                endpoint="/test",
                limit=5
            )
            assert allowed is True

        # Next request should be denied
        allowed, info = await limiter.check_rate_limit(
            api_key_id="test_key_2",
            endpoint="/test",
            limit=5
        )

        assert allowed is False
        assert info["remaining"] == 0

    async def test_get_rate_limit_info(self):
        """Test getting rate limit info without incrementing."""
        limiter = RateLimiter()

        # Make some requests
        for _ in range(3):
            await limiter.check_rate_limit(
                api_key_id="test_key_3",
                endpoint="/test",
                limit=10
            )

        # Get info without incrementing
        info1 = await limiter.get_rate_limit_info(
            api_key_id="test_key_3",
            endpoint="/test",
            limit=10
        )

        info2 = await limiter.get_rate_limit_info(
            api_key_id="test_key_3",
            endpoint="/test",
            limit=10
        )

        # Both should show same remaining count
        assert info1["remaining"] == info2["remaining"]
