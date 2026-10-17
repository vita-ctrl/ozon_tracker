from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_write_to_pm: Mapped[bool] = mapped_column(Boolean, default=False)
    added_to_attachment_menu: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_threshold: Mapped[float] = mapped_column(Float, default=5.0)
    check_frequency_hours: Mapped[int] = mapped_column(Integer, default=6)
    notifications_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
