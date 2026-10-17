from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.v1.routers import setup
from core import load_config

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async_engine = create_async_engine(url=config.db.url, echo=False)

    sessionmaker = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )
    app.state.sessionmaker = sessionmaker
    try:
        yield
    finally:
        await async_engine.dispose()


def create_app() -> FastAPI:

    app = FastAPI(title="Core Service API", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["*"],
        allow_headers=["X-Telegram-Init-Data", "Content-Type"],
        allow_credentials=False,
    )

    setup(app)

    return app
