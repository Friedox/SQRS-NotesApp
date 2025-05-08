import redis.asyncio as redis

from config import settings


redis_client = redis.Redis(
    host=settings.redis.host,
    port=settings.redis.port,
    db=settings.redis.db,
    decode_responses=False,  # Keep as bytes for better performance
)
