from datetime import timedelta
from functools import lru_cache

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    base_api_url: HttpUrl


class Config:
    redis: Redis = Redis()  # type: ignore
    headers: dict = SelfConfig().headers  # type: ignore
    base_url: str = str(SelfConfig().base_url)  # type: ignore
    base_api_url: str = str(SelfConfig().base_api_url)  # type: ignore

    max_cookie_attempts: int = 3
    max_captcha_solve_attemps: int = 3
    watch_cookies_interval = timedelta(minutes=5)
    watch_cookies_refresh_bellow = timedelta(seconds=30)
    cookie_ttl = timedelta(minutes=5)


@lru_cache
def load_config() -> Config:
    """Load configuration with caching"""
    return Config()
