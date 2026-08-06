import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import UserDep
from api.v1 import routers
from bot import create_bot, create_dispatcher
from core import create_sessionmaker, load_config


config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    sessionmaker = await create_sessionmaker(config)

    app.state.sessionmaker = sessionmaker

    bot = create_bot(config)
    dp = create_dispatcher(bot, sessionmaker)

    polling_task = asyncio.create_task(
        dp.start_polling(bot, config=config, handle_signals=False)
    )

    yield

    await dp.stop_polling()

    polling_task.cancel()
    await asyncio.gather(polling_task, return_exceptions=True)

    await bot.session.close()


def create_app() -> FastAPI:

    app = FastAPI(title="Telegram Bot API", version="1.0.0", lifespan=lifespan)
    routers.setup(app)

    @app.get("/health")
    async def health_check(user: UserDep):
        return {"status": "healthy"}

    return app
