from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from core import Config


Base = declarative_base()


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_sessionmaker(config: Config) -> async_sessionmaker:
    engine = create_async_engine(config.db.url, future=True)

    await create_tables(engine)
    return async_sessionmaker(engine, expire_on_commit=False)
