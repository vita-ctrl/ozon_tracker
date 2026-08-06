from datetime import datetime

from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import MappedColumn, mapped_column

from models import Base


class User(Base):
    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True)
    first_name: MappedColumn[str] = mapped_column(String(64))
    last_name: MappedColumn[str | None] = mapped_column(String(64), nullable=True)
    username: MappedColumn[str | None] = mapped_column(String(64), nullable=True)
    language_code: MappedColumn[str | None] = mapped_column(String(8), nullable=True)
    photo_url: MappedColumn[str | None] = mapped_column(String(256), nullable=True)
    is_premium: MappedColumn[bool] = mapped_column(default=False)
    allows_write_to_pm: MappedColumn[bool] = mapped_column(default=False)
    added_to_attachment_menu: MappedColumn[bool] = mapped_column(default=False)

    notification_threshold: MappedColumn[float] = mapped_column(default=5.0)
    check_frequency_hours: MappedColumn[int] = mapped_column(default=6)
    notifications_paused: MappedColumn[bool] = mapped_column(default=False)

    created_at: MappedColumn[datetime] = mapped_column(server_default=func.now())
    updated_at: MappedColumn[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
