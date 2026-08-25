import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
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



class Config:
    bot: Bot = Bot()  # type: ignore


@lru_cache
def load_config() -> Config:
    """Load configuration with caching"""
    return Config()
