"""
Cache Service using Redis
Provides caching decorators and utilities for API responses
"""

import logging
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
from datetime import timedelta

from app.redis_client import get_redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data using Redis"""

    def __init__(self):
        """Initialize cache service"""
        self.redis_client = None
        self.default_ttl = settings.CACHE_TTL_MEDIUM

    async def _get_redis(self):
        """Get Redis client"""
        if not self.redis_client:
            self.redis_client = await get_redis()
        return self.redis_client

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from function arguments

        Args:
            prefix: Cache key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Generated cache key
        """
        # Create a string representation of args and kwargs
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)

        # Hash if too long
        if len(key_string) > 100:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"

        return f"{prefix}:{key_string}" if key_string else prefix

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            redis = await self._get_redis()
            if not redis:
                return None

            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            redis = await self._get_redis()
            if not redis:
                return False

            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)

            await redis.set(key, serialized_value, ex=ttl)
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            redis = await self._get_redis()
            if not redis:
                return False

            await redis.delete(key)
            return True

        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "trends:*")

        Returns:
            Number of keys deleted
        """
        try:
            redis = await self._get_redis()
            if not redis:
                return 0

            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
                return len(keys)
            return 0

        except Exception as e:
            logger.error(f"Error clearing cache pattern: {e}")
            return 0

    def cached(
        self,
        prefix: str,
        ttl: Optional[int] = None
    ) -> Callable:
        """
        Decorator for caching function results

        Args:
            prefix: Cache key prefix
            ttl: Time to live in seconds

        Usage:
            @cache_service.cached("my_function", ttl=300)
            async def my_function(arg1, arg2):
                return expensive_operation(arg1, arg2)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    logger.info(f"Cache hit for {cache_key}")
                    return cached_value

                # Call original function
                logger.info(f"Cache miss for {cache_key}")
                result = await func(*args, **kwargs)

                # Store in cache
                if result is not None:
                    await self.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator


# Singleton instance
_cache_service = None


def get_cache_service() -> CacheService:
    """Get or create cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


# Convenience function for caching decorator
def cached(prefix: str, ttl: Optional[int] = None):
    """
    Convenience decorator for caching

    Usage:
        from app.services.cache_service import cached

        @cached("my_function", ttl=300)
        async def my_function(arg1, arg2):
            return expensive_operation(arg1, arg2)
    """
    cache_service = get_cache_service()
    return cache_service.cached(prefix, ttl)
