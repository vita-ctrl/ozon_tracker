from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from core import Config

from bot import handlers, middlewares


def create_bot(config: Config) -> Bot:
    return Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))


def create_dispatcher(bot: Bot) -> Dispatcher:
    dp = Dispatcher(bot=bot)
    handlers.setup(dp)

    middlewares.setup(dp, bot)

    return dp
