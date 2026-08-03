import json
from functools import lru_cache
from typing import Any

from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Bot(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BOT_",
        extra="ignore",
    )

    token: str
    admins: list[int] = []

    @field_validator("admins", mode="before")
    @classmethod
    def parse_json_list(cls, value: Any) -> list[int]:
        """Parse JSON string to list of integers"""
        return json.loads(value) if isinstance(value, str) else value


class DB(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        extra="ignore",
    )

    user: str
    password: str
    host: str
    port: int
    name: str

    @property
    def url(self) -> str:
        """Get SQLAlchemy async database URL for asyncpg"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Redis(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="REDIS_",
        extra="ignore",
    )

    url: str


class SelfConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )

    headers: dict
    base_url: HttpUrl


class Config:
    bot: Bot = Bot()  # type: ignore
    db: DB = DB()  # type: ignore
    headers: dict = SelfConfig().headers  # type: ignore
    base_url: str = str(SelfConfig().base_url)  # type: ignore


@lru_cache
def load_config() -> Config:
    """Load configuration with caching"""
    return Config()
