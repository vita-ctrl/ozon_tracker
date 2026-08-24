from typing import Annotated

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core import load_config, verify_init_data
from models import User
from schemas import WebAppInitData

config = load_config()

init_data_scheme = APIKeyHeader(
    name="X-Telegram-Init-Data",
    scheme_name="Telegram initData",
    description="Telegram WebApp initData query string (user должен быть URL-encoded)",
)


async def get_session(request: Request):
    sessionmaker: async_sessionmaker = request.app.state.sessionmaker
    async with sessionmaker() as session:
        yield session


async def get_current_user(
    session: SessionDep, raw_init_data: str = Depends(init_data_scheme)
) -> User:
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
        user = User(
            id=init_data.user.id,
            first_name=init_data.user.first_name,
            last_name=init_data.user.last_name,
            username=init_data.user.username,
            language_code=init_data.user.language_code,
            photo_url=init_data.user.photo_url,
            is_premium=init_data.user.is_premium,
            allows_write_to_pm=init_data.user.allows_write_to_pm,
            added_to_attachment_menu=init_data.user.added_to_attachment_menu,
        )
        session.add(user)
        await session.commit()
    return user


SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]
