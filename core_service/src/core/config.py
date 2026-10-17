import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class SelfConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )

    debug: bool = False
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated or JSON-encoded origins into a list"""
        value = self.cors_origins.strip()
        if value.startswith("["):
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]


class Config:
    debug: bool = SelfConfig().debug
    cors_origins: list[str] = SelfConfig().cors_origin_list
    db: DB = DB()  # type: ignore
    redis: Redis = Redis()  # type: ignore
    bot: Bot = Bot()  # type: ignore


@lru_cache
def load_config() -> Config:
    """Load configuration with caching"""
    return Config()
