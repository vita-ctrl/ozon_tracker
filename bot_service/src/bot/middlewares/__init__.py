from aiogram import Bot, Dispatcher

from .callback import CallbackMiddleware


def setup(dp: Dispatcher, bot: Bot) -> None:
    """Setups all middlewares"""
    dp.callback_query.outer_middleware(CallbackMiddleware())
