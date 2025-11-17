"""
=============================================================================
AI Hub - Redis Cache Client
=============================================================================
Provides Redis caching for API responses and rate limiting.

Features:
- Connection pooling
- Automatic retry
- Fallback to in-memory cache if Redis unavailable
=============================================================================
"""

from typing import Optional, Any
import redis
from redis.exceptions import RedisError
import json
import structlog
from core.config import settings

logger = structlog.get_logger()


class RedisCache:
    """
    Redis cache client with fallback to in-memory cache.
    
    Provides thread-safe caching for API responses, reducing
    external API calls and improving performance.
    """
    
    def __init__(self):
        """Initialize Redis connection with pool."""
        try:
            self.redis_client = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("redis_connected", host=settings.REDIS_HOST)
        except RedisError as e:
            logger.warning("redis_connection_failed", error=str(e))
            self.available = False
            self._fallback_cache = {}  # In-memory fallback
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            if self.available:
                value = self.redis_client.get(key)
                if value:
                    logger.debug("cache_hit", key=key)
                    return json.loads(value)
                logger.debug("cache_miss", key=key)
                return None
            else:
                # Fallback to in-memory cache
                return self._fallback_cache.get(key)
        except Exception as e:
            logger.error("cache_get_failed", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.available:
                serialized = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
                logger.debug("cache_set", key=key, ttl=ttl)
                return True
            else:
                # Fallback to in-memory cache (no TTL)
                self._fallback_cache[key] = value
                return True
        except Exception as e:
            logger.error("cache_set_failed", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.available:
                self.redis_client.delete(key)
            else:
                self._fallback_cache.pop(key, None)
            logger.debug("cache_deleted", key=key)
            return True
        except Exception as e:
            logger.error("cache_delete_failed", key=key, error=str(e))
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Redis pattern (e.g., "stock:*")
        
        Returns:
            Number of keys deleted
        """
        try:
            if self.available:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
                    logger.info("cache_pattern_cleared", pattern=pattern, count=count)
                    return count
            return 0
        except Exception as e:
            logger.error("cache_clear_pattern_failed", pattern=pattern, error=str(e))
            return 0


# Global cache instance
cache = RedisCache()
