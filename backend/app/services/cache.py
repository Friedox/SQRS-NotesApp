from typing import Optional

import redis.asyncio as redis

from config import settings


class CacheService:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis.url,
            decode_responses=False,  # Keep as bytes for better performance
        )

    async def get(self, key: str) -> Optional[bytes]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def close(self) -> None:
        await self.client.close()


cache_service = CacheService()
