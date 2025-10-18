"""
Cache layer with Redis primary and file system fallback
"""
import json
import asyncio
from typing import Optional, Any
from pathlib import Path
from datetime import datetime, timedelta

import redis.asyncio as aioredis
from redis.exceptions import RedisError

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("cache")


class CacheManager:
    """
    Unified cache manager with Redis primary and file fallback
    """

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_redis = settings.USE_REDIS
        self._connected = False

    async def connect(self) -> None:
        """Connect to Redis if enabled"""
        if not self.use_redis:
            logger.info("Redis disabled, using file cache only")
            return

        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            logger.info("Connected to Redis successfully")
        except (RedisError, Exception) as e:
            logger.warning(f"Failed to connect to Redis: {e}. Falling back to file cache")
            self.redis_client = None
            self._connected = False

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try Redis first
        if self._connected and self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache hit (Redis): {key}")
                    return value
            except RedisError as e:
                logger.warning(f"Redis get error: {e}, falling back to file")

        # Fallback to file cache
        return await self._get_from_file(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        success = False

        # Try Redis first
        if self._connected and self.redis_client:
            try:
                if ttl:
                    await self.redis_client.setex(key, ttl, value)
                else:
                    await self.redis_client.set(key, value)
                logger.debug(f"Cache set (Redis): {key}")
                success = True
            except RedisError as e:
                logger.warning(f"Redis set error: {e}, falling back to file")

        # Always write to file cache as backup
        file_success = await self._set_to_file(key, value, ttl)

        return success or file_success

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        success = False

        # Try Redis
        if self._connected and self.redis_client:
            try:
                await self.redis_client.delete(key)
                success = True
            except RedisError as e:
                logger.warning(f"Redis delete error: {e}")

        # Delete from file cache
        file_success = await self._delete_from_file(key)

        return success or file_success

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        # Try Redis first
        if self._connected and self.redis_client:
            try:
                return bool(await self.redis_client.exists(key))
            except RedisError:
                pass

        # Check file cache
        cache_file = self.cache_dir / f"{key}.cache"
        return cache_file.exists()

    async def _get_from_file(self, key: str) -> Optional[str]:
        """Get value from file cache"""
        cache_file = self.cache_dir / f"{key}.cache"

        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text())

            # Check expiration
            if data.get("expires_at"):
                expires_at = datetime.fromisoformat(data["expires_at"])
                if datetime.now() >= expires_at:
                    logger.debug(f"Cache expired (file): {key}")
                    await self._delete_from_file(key)
                    return None

            logger.debug(f"Cache hit (file): {key}")
            return data["value"]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error reading cache file {key}: {e}")
            return None

    async def _set_to_file(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in file cache"""
        cache_file = self.cache_dir / f"{key}.cache"

        try:
            data = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "expires_at": None
            }

            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
                data["expires_at"] = expires_at.isoformat()

            cache_file.write_text(json.dumps(data, indent=2))
            logger.debug(f"Cache set (file): {key}")
            return True
        except Exception as e:
            logger.error(f"Error writing cache file {key}: {e}")
            return False

    async def _delete_from_file(self, key: str) -> bool:
        """Delete file from cache"""
        cache_file = self.cache_dir / f"{key}.cache"

        try:
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Cache deleted (file): {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache file {key}: {e}")
            return False

    async def clear_expired(self) -> int:
        """
        Clear expired entries from file cache

        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                data = json.loads(cache_file.read_text())
                if data.get("expires_at"):
                    expires_at = datetime.fromisoformat(data["expires_at"])
                    if datetime.now() >= expires_at:
                        cache_file.unlink()
                        count += 1
            except Exception:
                pass

        if count > 0:
            logger.info(f"Cleared {count} expired cache entries")

        return count


# Global cache manager instance
cache = CacheManager()
