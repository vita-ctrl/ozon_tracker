from contextlib import suppress
from datetime import timedelta

import redis.asyncio as aioredis

from .models import Cookies


class RedisCookieStorage:
    def __init__(
        self,
        redis_url: str,
        ttl: timedelta,
        instance_id: str,
        key: str | None = None,
        refresh_lock_key: str | None = None,
        refresh_lock_ttl: timedelta = timedelta(minutes=5),
        health_key: str | None = None,
    ):
        self.redis_url = redis_url
        self.cookies_key = key or f"ozon:kz:{instance_id}:cookies"
        self.ttl = ttl
        self.refresh_lock_key = refresh_lock_key or f"ozon:kz:{instance_id}:refresh_lock"
        self.refresh_lock_ttl = refresh_lock_ttl
        self.health_key = health_key or f"ozon:kz:{instance_id}:health"
        self._redis: aioredis.Redis | None = None

    async def _client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def get_cookies_ttl(self) -> int:
        redis = await self._client()
        return await redis.ttl(self.cookies_key)

    async def get(self) -> Cookies | None:
        try:
            redis = await self._client()
            data = await redis.get(self.cookies_key)
        except Exception:
            return None
        if not data:
            return None
        return Cookies.model_validate_json(data)

    async def set(self, cookies: Cookies) -> None:
        with suppress(Exception):
            redis = await self._client()
            await redis.set(self.cookies_key, cookies.model_dump_json(), ex=self.ttl)

    async def close(self) -> None:
        if self._redis:
            with suppress(Exception):
                await self._redis.aclose()
            self._redis = None

    async def get_health(self) -> bool:
        try:
            redis = await self._client()
            value = await redis.get(self.health_key)
        except Exception:
            return False
        return value == "true"

    async def set_health(self, healthy: bool) -> None:
        with suppress(Exception):
            redis = await self._client()
            await redis.set(self.health_key, "true" if healthy else "false")

    async def acquire_refresh_lock(self) -> bool:
        redis = await self._client()
        result = await redis.set(
            self.refresh_lock_key, "1", nx=True, ex=int(self.refresh_lock_ttl.total_seconds())
        )
        return result is not None

    async def release_refresh_lock(self) -> None:
        redis = await self._client()
        await redis.delete(self.refresh_lock_key)
