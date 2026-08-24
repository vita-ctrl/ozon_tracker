from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot import handlers, middlewares
from core import Config


def create_bot(config: Config) -> Bot:
    return Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))


def create_dispatcher(bot: Bot, sessionmaker: async_sessionmaker) -> Dispatcher:
    dp = Dispatcher(bot=bot)
    handlers.setup(dp)

    middlewares.setup(dp, sessionmaker, bot)

    return dp
