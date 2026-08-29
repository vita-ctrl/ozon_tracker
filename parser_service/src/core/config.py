from datetime import timedelta
from enum import Enum
from functools import lru_cache

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Currency(str, Enum):
    # Рекомендуемые валюты
    RUB = "RUB"  # Российский рубль
    USD = "USD"  # Доллар США
    BYN = "BYN"  # Белорусский рубль
    KZT = "KZT"  # Казахстанский тенге
    ILS = "ILS"  # Новый израильский шекель
    AMD = "AMD"  # Армянский драм
    UZS = "UZS"  # Узбекский сум
    KGS = "KGS"  # Киргизский сом
    AZN = "AZN"  # Азербайджанский манат
    GEL = "GEL"  # Грузинский лари
    MNT = "MNT"  # Монгольский тугрик

    # Все остальные доступные валюты
    AUD = "AUD"  # Австралийский доллар
    DKK = "DKK"  # Датская крона
    JPY = "JPY"  # Иена
    CAD = "CAD"  # Канадский доллар
    CNY = "CNY"  # Китайский юань
    MDL = "MDL"  # Молдавский лей
    NOK = "NOK"  # Норвежская крона
    PLN = "PLN"  # Польский злотый
    SGD = "SGD"  # Сингапурский доллар
    TRY = "TRY"  # Турецкая лира
    UAH = "UAH"  # Украинская гривна
    GBP = "GBP"  # Фунт стерлингов
    CZK = "CZK"  # Чешская крона
    SEK = "SEK"  # Шведская крона
    CHF = "CHF"  # Швейцарский франк

    def __str__(self):
        return self.value




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
    currency_change_url: HttpUrl
    default_currency: Currency


class Config:
    redis: Redis = Redis()  # type: ignore
    headers: dict = SelfConfig().headers  # type: ignore
    base_url: str = str(SelfConfig().base_url)  # type: ignore
    base_api_url: str = str(SelfConfig().base_api_url)  # type: ignore
    currency_change_url: str = str(SelfConfig().currency_change_url)  # type: ignore
    default_currency: Currency = SelfConfig().default_currency  # type: ignore

    max_cookie_attempts: int = 3
    max_captcha_solve_attempts: int = 3
    watch_cookies_interval = timedelta(minutes=5)
    watch_cookies_refresh_bellow = timedelta(seconds=30)
    cookie_ttl = timedelta(minutes=5)
    rate_limit_capacity: int = 10
    rate_limit_refill_rate: float = 10.0


@lru_cache
def load_config() -> Config:
    """Load configuration with caching"""
    return Config()
