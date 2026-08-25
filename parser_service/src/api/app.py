from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1 import routers
from core import load_config
from services import OzonCookieManager, OzonParserBrowser, RedisCookieStorage

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage = RedisCookieStorage(config.redis.url, config.cookie_ttl)
    manager = OzonCookieManager(storage, OzonParserBrowser())
    await manager.start_watcher()

    app.state.cookie_manager = manager


    yield

    await manager.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Parser Service API", version="1.0.0", lifespan=lifespan)
    routers.setup(app)
    return app
