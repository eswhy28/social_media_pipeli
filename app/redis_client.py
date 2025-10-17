import redis.asyncio as redis
from app.config import settings

# Redis connection pool
redis_pool = None


async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=10
        )
    return redis_pool


async def get_redis():
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)


async def close_redis():
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()
