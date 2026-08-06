from typing import Annotated

from fastapi import Depends, Request, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core import load_config, verify_init_data
from models import User
from schemas import WebAppInitData

config = load_config()


async def get_session(request: Request):
    sessionmaker: async_sessionmaker = request.app.state.sessionmaker
    async with sessionmaker() as session:
        yield session


async def get_current_user(request: Request, session: SessionDep) -> User:
    raw_init_data = request.headers.get("X-Telegram-Init-Data")
    if not raw_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Telegram-Init-Data header",
        )
    if not verify_init_data(raw_init_data, config.bot.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-Telegram-Init-Data header",
        )
    init_data = WebAppInitData.parse_init_data(raw_init_data)
    if not init_data.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user data in X-Telegram-Init-Data header",
        )
    user = await session.scalar(select(User).where(User.id == init_data.user.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]
