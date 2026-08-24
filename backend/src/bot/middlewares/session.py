from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import async_sessionmaker


class SessionMiddleware(BaseMiddleware):
    """
    Middleware for adding session.
    """

    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        """Session middleware"""
        self.sessionmaker = sessionmaker

    async def __call__(  # type: ignore
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        """Session middleware"""
        async with self.sessionmaker() as session:
            data["session"] = session
            return await handler(event, data)
