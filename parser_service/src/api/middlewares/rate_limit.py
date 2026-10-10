import time
from collections.abc import Callable
from http import HTTPStatus

import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class DistributedTokenBucketMiddleware(BaseHTTPMiddleware):
    LUA_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local current_time = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])

    local data = redis.call('HMGET', key, 'tokens', 'timestamp')
    local tokens = tonumber(data[1])
    local timestamp = tonumber(data[2])

    if tokens == nil then
        tokens = capacity
        timestamp = current_time
    end

    -- Refill tokens based on elapsed time
    local delta = math.max(0, current_time - timestamp)
    local refill = math.floor(delta * refill_rate)

    tokens = math.min(capacity, tokens + refill)

    local allowed = 0
    if tokens >= requested then
        tokens = tokens - requested
        allowed = 1
    end

    -- Update timestamp and tokens atomically
    if allowed == 1 then
        redis.call('HSET', key, 'tokens', tokens, 'timestamp', current_time)
    else
        redis.call('HSET', key, 'tokens', tokens)
    end

    redis.call('EXPIRE', key, 3600)
    return {allowed, tokens}
    """

    def __init__(
        self,
        app: ASGIApp,
        capacity: int = 10,
        refill_rate: float = 10.0,
    ):
        super().__init__(app)
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._script_sha: str | None = None

    async def _load_script(self, redis_client: redis.Redis) -> None:
        if self._script_sha is None:
            self._script_sha = await redis_client.script_load(self.LUA_SCRIPT)

    @staticmethod
    def _get_client_id(request: Request) -> str:
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        if request.client and request.client.host:
            return request.client.host

        return "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in {"/docs", "/redoc", "/openapi.json"}:
            return await call_next(request)

        try:
            redis_client: redis.Redis = request.app.state.redis
        except AttributeError:
            return await call_next(request)

        try:
            await self._load_script(redis_client)
            client_id = self._get_client_id(request)
            key = f"rate-limit:{client_id}"

            result = await redis_client.evalsha(
                self._script_sha,
                1,
                key,
                self.capacity,
                self.refill_rate,
                time.time(),
                1,
            )

            allowed, tokens_left = result[0], result[1]

            if bool(allowed):
                response = await call_next(request)
                response.headers["X-RateLimit-Remaining"] = str(round(tokens_left))
                response.headers["X-RateLimit-Limit"] = str(self.capacity)
                return response
            else:
                return Response(
                    content='{"detail": "Too Many Requests. Rate limit exceeded."}',
                    status_code=HTTPStatus.TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={"Retry-After": str(max(1, int(1 / self.refill_rate)))},
                )
        except Exception as e:
            return await call_next(request)
