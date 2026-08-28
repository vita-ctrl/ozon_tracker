from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from api.middlewares import DistributedTokenBucketMiddleware
from api.v1 import routers
from core import load_config
from services import OzonCookieManager, OzonParserBrowser, RedisCookieStorage

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = aioredis.from_url(config.redis.url, decode_responses=True)
    app.state.redis = redis_client

    storage = RedisCookieStorage(config.redis.url, config.cookie_ttl)
    manager = OzonCookieManager(storage, OzonParserBrowser())
    await manager.start_watcher()

    app.state.cookie_manager = manager

    yield

    await manager.close()
    await redis_client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="Parser Service API", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        DistributedTokenBucketMiddleware,
        capacity=config.rate_limit_capacity,
        refill_rate=config.rate_limit_refill_rate,
    )

    routers.setup(app)
    return app
