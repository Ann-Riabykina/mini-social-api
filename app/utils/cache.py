import hashlib
import json

from redis.asyncio import Redis

CACHE_PREFIX = "posts:list:"


def build_posts_cache_key(params: dict) -> str:
    serialized = json.dumps(params, sort_keys=True)
    digest = hashlib.sha256(serialized.encode()).hexdigest()
    return f"{CACHE_PREFIX}{digest}"


async def invalidate_posts_cache(redis: Redis) -> None:
    keys = await redis.keys(f"{CACHE_PREFIX}*")
    if keys:
        await redis.delete(*keys)
