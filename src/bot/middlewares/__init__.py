from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker


from .callback import CallbackMiddleware
from .session import SessionMiddleware


def setup(dp: Dispatcher, sessionmaker: async_sessionmaker, bot: Bot) -> None:
    """Setups all middlewares"""
    dp.callback_query.outer_middleware(CallbackMiddleware())
    if sessionmaker:
        dp.update.outer_middleware(SessionMiddleware(sessionmaker))
