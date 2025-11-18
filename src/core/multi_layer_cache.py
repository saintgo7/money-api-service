"""Multi-layer caching system (L1: Memory, L2: Redis)."""
import asyncio
import logging
from typing import Any, Optional, Dict
from functools import lru_cache, wraps
import json
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LRUCache:
    """
    Thread-safe LRU cache implementation.
    L1 cache (in-memory).
    """

    def __init__(self, maxsize: int = 1000):
        """
        Initialize LRU cache.

        Args:
            maxsize: Maximum number of items to cache
        """
        self.maxsize = maxsize
        self.cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self.access_order: list = []  # LRU tracking
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]

                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)

                logger.debug(f"L1 cache hit: {key}")
                return value

            logger.debug(f"L1 cache miss: {key}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        async with self.lock:
            # Evict if at capacity
            if len(self.cache) >= self.maxsize and key not in self.cache:
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
                logger.debug(f"L1 cache evicted: {oldest_key}")

            # Calculate expiration
            timestamp = datetime.utcnow()
            if ttl:
                timestamp = timestamp + timedelta(seconds=ttl)

            self.cache[key] = (value, timestamp)

            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)

    async def delete(self, key: str):
        """Delete value from cache."""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)

    async def clear(self):
        """Clear all cache."""
        async with self.lock:
            self.cache.clear()
            self.access_order.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class MultiLayerCache:
    """
    Multi-layer cache with L1 (memory) and L2 (Redis).

    Features:
    - Fast L1 in-memory cache
    - Persistent L2 Redis cache
    - Automatic promotion/demotion
    - TTL support
    - Cache warming
    """

    def __init__(
        self,
        l1_maxsize: int = 1000,
        default_ttl: int = 300,
        prefix: str = "mlcache"
    ):
        """
        Initialize multi-layer cache.

        Args:
            l1_maxsize: Maximum L1 cache size
            default_ttl: Default TTL in seconds
            prefix: Cache key prefix
        """
        self.l1 = LRUCache(maxsize=l1_maxsize)
        self.default_ttl = default_ttl
        self.prefix = prefix

        # Statistics
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "sets": 0,
            "deletes": 0
        }

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (L1 first, then L2).

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        full_key = self._make_key(key)

        # Try L1 first
        value = await self.l1.get(full_key)
        if value is not None:
            self.stats["l1_hits"] += 1
            return value

        self.stats["l1_misses"] += 1

        # Try L2 (Redis)
        try:
            from src.core.redis_client import get_redis
            redis = await get_redis()
            value_str = await redis.get(full_key)

            if value_str:
                self.stats["l2_hits"] += 1
                value = json.loads(value_str)

                # Promote to L1
                await self.l1.set(full_key, value)
                logger.debug(f"L2 hit, promoted to L1: {key}")

                return value

            self.stats["l2_misses"] += 1
            logger.debug(f"L2 miss: {key}")

        except Exception as e:
            logger.error(f"L2 cache error: {e}")

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        l1_only: bool = False
    ):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            l1_only: Only cache in L1 (for very hot data)
        """
        full_key = self._make_key(key)
        ttl = ttl or self.default_ttl

        # Set in L1
        await self.l1.set(full_key, value, ttl)

        # Set in L2 unless l1_only
        if not l1_only:
            try:
                from src.core.redis_client import get_redis
                redis = await get_redis()
                value_str = json.dumps(value, default=str)
                await redis.setex(full_key, ttl, value_str)
            except Exception as e:
                logger.error(f"Failed to set L2 cache: {e}")

        self.stats["sets"] += 1

    async def delete(self, key: str):
        """
        Delete value from all cache layers.

        Args:
            key: Cache key
        """
        full_key = self._make_key(key)

        # Delete from L1
        await self.l1.delete(full_key)

        # Delete from L2
        try:
            from src.core.redis_client import get_redis
            redis = await get_redis()
            await redis.delete(full_key)
        except Exception as e:
            logger.error(f"Failed to delete from L2: {e}")

        self.stats["deletes"] += 1

    async def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "user:*")
        """
        full_pattern = self._make_key(pattern)

        # Clear L1 (no pattern matching, clear all)
        await self.l1.clear()

        # Clear L2 by pattern
        try:
            from src.core.redis_client import get_redis
            redis = await get_redis()
            keys = await redis.keys(full_pattern)
            if keys:
                await redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} keys matching {pattern}")
        except Exception as e:
            logger.error(f"Failed to invalidate pattern: {e}")

    async def warm_cache(self, keys_and_values: Dict[str, Any], ttl: Optional[int] = None):
        """
        Warm cache with multiple values.

        Args:
            keys_and_values: Dictionary of keys and values
            ttl: Time to live in seconds
        """
        logger.info(f"Warming cache with {len(keys_and_values)} items")

        for key, value in keys_and_values.items():
            await self.set(key, value, ttl)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = (
            self.stats["l1_hits"] +
            self.stats["l1_misses"]
        )

        return {
            **self.stats,
            "l1_size": self.l1.size(),
            "l1_hit_rate": (
                self.stats["l1_hits"] / total_requests
                if total_requests > 0 else 0
            ),
            "l2_hit_rate": (
                self.stats["l2_hits"] / self.stats["l1_misses"]
                if self.stats["l1_misses"] > 0 else 0
            ),
            "total_hit_rate": (
                (self.stats["l1_hits"] + self.stats["l2_hits"]) / total_requests
                if total_requests > 0 else 0
            )
        }

    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "sets": 0,
            "deletes": 0
        }


# Global cache instance
multi_cache = MultiLayerCache()


def cached_multi_layer(
    ttl: int = 300,
    key_prefix: str = "",
    l1_only: bool = False
):
    """
    Decorator for multi-layer caching.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        l1_only: Only use L1 cache

    Example:
        @cached_multi_layer(ttl=600, key_prefix="user")
        async def get_user(user_id: str):
            # Expensive operation
            return user_data
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                "func": func.__name__,
                "args": [str(arg) for arg in args],
                "kwargs": {k: str(v) for k, v in sorted(kwargs.items())}
            }
            key_str = json.dumps(key_data, sort_keys=True)
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            cache_key = f"{key_prefix}:{func.__name__}:{key_hash}" if key_prefix else f"{func.__name__}:{key_hash}"

            # Try to get from cache
            result = await multi_cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return result

            # Execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await multi_cache.set(cache_key, result, ttl, l1_only=l1_only)

            return result

        return wrapper
    return decorator
