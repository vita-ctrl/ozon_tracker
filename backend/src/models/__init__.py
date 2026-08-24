from sqlalchemy.orm import declarative_base

Base = declarative_base()
from .user import User  # noqa: E402

__all__ = ["Base", "User"]
