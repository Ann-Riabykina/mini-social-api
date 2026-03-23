from collections.abc import AsyncGenerator
from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def create_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> AsyncGenerator[Redis, None]:
    yield create_redis_client()
