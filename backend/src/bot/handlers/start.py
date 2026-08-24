from aiogram import F, Router
from aiogram.enums.chat_type import ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from core import Config


router = Router()


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start(message: Message, session: AsyncSession, config: Config) -> None:
    await message.answer("")
