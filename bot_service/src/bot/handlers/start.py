from aiogram import F, Router
from aiogram.enums.chat_type import ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message
from core import Config
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start(message: Message, session: AsyncSession, config: Config) -> None:
    await message.answer("Hello World")
