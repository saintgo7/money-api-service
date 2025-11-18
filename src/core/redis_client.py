"""Redis client for caching and rate limiting."""
import redis.asyncio as redis
from typing import Optional

from src.config import get_settings

settings = get_settings()

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def init_redis():
    """Initialize Redis connection."""
    global redis_client
    redis_client = await redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
