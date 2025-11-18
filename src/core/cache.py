"""Redis caching layer."""
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
import hashlib

from src.core.redis_client import get_redis

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage Redis caching."""

    def __init__(self, default_ttl: int = 300):
        """Initialize cache manager.

        Args:
            default_ttl: Default TTL in seconds (5 minutes)
        """
        self.default_ttl = default_ttl

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            redis = await get_redis()
            value = await redis.get(key)

            if value:
                return json.loads(value)

            return None

        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            Success status
        """
        try:
            redis = await get_redis()
            serialized = json.dumps(value)

            if ttl is None:
                ttl = self.default_ttl

            await redis.setex(key, ttl, serialized)
            return True

        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            Success status
        """
        try:
            redis = await get_redis()
            await redis.delete(key)
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        try:
            redis = await get_redis()
            keys = await redis.keys(pattern)

            if keys:
                deleted = await redis.delete(*keys)
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return 0

    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key
        """
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_str = ":".join(key_parts)

        # Hash long keys
        if len(key_str) > 200:
            key_str = hashlib.md5(key_str.encode()).hexdigest()

        return key_str


# Global cache instance
cache = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results.

    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key

    Example:
        @cached(ttl=600, key_prefix="user")
        async def get_user(user_id: str):
            # Expensive database query
            return user_data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache.generate_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Call function
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator
