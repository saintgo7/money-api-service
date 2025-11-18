"""Rate limiting using Redis sliding window."""
import time
from typing import Optional
from uuid import uuid4

from src.core.redis_client import get_redis


class RateLimiter:
    """Rate limiter using Redis sorted sets (sliding window)."""

    def __init__(self):
        self.window = 60  # 1 minute window

    async def check_rate_limit(
        self,
        api_key_id: str,
        endpoint: str,
        limit: int
    ) -> tuple[bool, dict]:
        """Check if request is within rate limit.

        Args:
            api_key_id: API key identifier
            endpoint: API endpoint being accessed
            limit: Maximum requests per minute

        Returns:
            Tuple of (allowed: bool, info: dict)
            info contains: limit, remaining, reset_at
        """
        redis = await get_redis()
        key = f"rate_limit:{api_key_id}:{endpoint}"
        current_time = time.time()
        window_start = current_time - self.window

        # Remove old entries outside the window
        await redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        request_count = await redis.zcard(key)

        # Rate limit info
        info = {
            "limit": limit,
            "remaining": max(0, limit - request_count),
            "reset_at": int(current_time + self.window)
        }

        if request_count >= limit:
            return False, info

        # Add new request
        await redis.zadd(key, {str(uuid4()): current_time})
        await redis.expire(key, self.window)

        info["remaining"] -= 1
        return True, info

    async def get_rate_limit_info(
        self,
        api_key_id: str,
        endpoint: str,
        limit: int
    ) -> dict:
        """Get current rate limit status without incrementing."""
        redis = await get_redis()
        key = f"rate_limit:{api_key_id}:{endpoint}"
        current_time = time.time()
        window_start = current_time - self.window

        # Clean up old entries
        await redis.zremrangebyscore(key, 0, window_start)

        # Count requests
        request_count = await redis.zcard(key)

        return {
            "limit": limit,
            "remaining": max(0, limit - request_count),
            "reset_at": int(current_time + self.window)
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
