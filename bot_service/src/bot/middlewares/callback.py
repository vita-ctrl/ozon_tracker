from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from aiogram import BaseMiddleware, exceptions
from aiogram.types import CallbackQuery


class CallbackMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        call: CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        await handler(call, data)
        with suppress(exceptions.TelegramAPIError):
            await call.answer()
