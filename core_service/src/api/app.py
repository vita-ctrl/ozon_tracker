from contextlib import asynccontextmanager

from api.v1.routers import setup
from core import load_config
from fastapi import FastAPI

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


def create_app() -> FastAPI:

    app = FastAPI(title="Core Service API", version="1.0.0", lifespan=lifespan)
    setup(app)

    @app.get("/health")
    async def health_check():
        return "ok"

    return app
