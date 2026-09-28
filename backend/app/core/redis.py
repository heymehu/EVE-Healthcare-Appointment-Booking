import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

try:
    import redis.asyncio as redis
    from redis.asyncio.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    ConnectionPool = None

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None


def get_redis_pool() -> Optional[ConnectionPool]:
    global _redis_pool
    if not REDIS_AVAILABLE:
        return None
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
    return _redis_pool


def get_redis_client() -> Optional[redis.Redis]:
    global _redis_client
    if not REDIS_AVAILABLE:
        return None
    if _redis_client is None:
        pool = get_redis_pool()
        if pool:
            _redis_client = redis.Redis(connection_pool=pool)
    return _redis_client


async def close_redis_pool() -> None:
    global _redis_pool, _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


@asynccontextmanager
async def redis_lifespan():
    try:
        client = get_redis_client()
        if client:
            await client.ping()
            logger.info("Redis connection established")
        else:
            logger.warning("Redis not available, running without cache")
        yield
    except Exception as e:
        logger.warning("Redis connection failed: %s", e)
        yield
    finally:
        await close_redis_pool()


class CacheService:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._client: Optional[redis.Redis] = None
        self._memory_cache: dict = {}

    @property
    def client(self) -> Optional[redis.Redis]:
        if self._client is None:
            self._client = get_redis_client()
        return self._client

    def _use_memory(self) -> bool:
        return not get_settings().CACHE_ENABLED or self.client is None

    async def get(self, key: str) -> Optional[str]:
        if self._use_memory():
            return self._memory_cache.get(key)
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.warning("Cache get failed for key %s: %s", key, e)
            return self._memory_cache.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        if self._use_memory():
            self._memory_cache[key] = value
            return True
        try:
            return await self.client.set(key, value, ex=ttl or self.ttl)
        except Exception as e:
            logger.warning("Cache set failed for key %s: %s", key, e)
            self._memory_cache[key] = value
            return True

    async def delete(self, key: str) -> bool:
        if self._use_memory():
            self._memory_cache.pop(key, None)
            return True
        try:
            return await self.client.delete(key) > 0
        except Exception as e:
            logger.warning("Cache delete failed for key %s: %s", key, e)
            self._memory_cache.pop(key, None)
            return True

    async def delete_pattern(self, pattern: str) -> int:
        if self._use_memory():
            keys_to_delete = [k for k in self._memory_cache if pattern.replace("*", "") in k]
            for k in keys_to_delete:
                self._memory_cache.pop(k, None)
            return len(keys_to_delete)
        try:
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await self.client.delete(*keys)
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            logger.warning("Cache delete pattern failed for %s: %s", pattern, e)
            return 0


cache_service = CacheService()