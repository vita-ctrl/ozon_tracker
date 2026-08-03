import asyncio
from contextlib import suppress
from datetime import timedelta
from http import HTTPStatus
import json
import os
import random
import time
from curl_cffi import BrowserTypeLiteral, requests
from curl_cffi import Response as R
from pydantic import BaseModel, HttpUrl, validate_call
import nodriver as uc
import redis.asyncio as aioredis

from services import OzonProductExtractor


class Response(BaseModel):
    text: str
    status_code: HTTPStatus


class Cookie(BaseModel):
    name: str
    value: str
    domain: str | None = None


class Cookies(BaseModel):
    cookies: list[Cookie]


class OzonParserCurl:
    def __init__(self, impersonate: BrowserTypeLiteral, headers: dict) -> None:
        self.session = requests.AsyncSession(impersonate=impersonate)
        self.session.headers.update(headers)

    def set_cookies(self, cookies: Cookies) -> None:
        for cookie in cookies.cookies:
            self.session.cookies.set(cookie.name, cookie.value)

    def set_headers(self, headers: dict) -> None:
        self.session.headers.update(headers)

    @validate_call
    async def get(self, url: HttpUrl) -> Response:
        resp: R = await self.session.get(str(url))
        return Response(text=resp.text, status_code=HTTPStatus(resp.status_code))


class RedisCookieStorage:
    """Хранение кук в Redis."""

    def __init__(
        self,
        redis_url: str | None = None,
        key: str = "ozon:kz:cookies",
        ttl: timedelta = timedelta(minutes=5),
    ):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.key = key
        self.ttl = ttl
        self._redis: aioredis.Redis | None = None

    async def _client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def get(self) -> Cookies | None:
        try:
            redis = await self._client()
            data = await redis.get(self.key)
        except Exception:
            return None
        if not data:
            return None
        return Cookies.model_validate_json(data)

    async def set(self, cookies: Cookies) -> None:
        with suppress(Exception):
            redis = await self._client()
            await redis.set(self.key, cookies.model_dump_json(), ex=self.ttl)

    async def close(self) -> None:
        if self._redis:
            with suppress(Exception):
                await self._redis.aclose()
            self._redis = None


class OzonParserBrowser:
    """Управление браузером: запуск, навигация, сбор кук."""

    def __init__(
        self,
        headless: bool = False,
        duration_range: tuple[float, float] = (10.0, 30.0),
        scroll_sleep_range: tuple[float, float] = (1.0, 4.0),
    ):
        self.headless = headless
        self.duration_range = duration_range
        self.scroll_sleep_range = scroll_sleep_range
        self.browser: uc.Browser | None = None

    async def refresh_cookies(self, url: str) -> Cookies:
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        page = await self.browser.get(url)
        await page.sleep(5)

        duration = random.uniform(*self.duration_range)
        end_time = time.time() + duration
        while time.time() < end_time:
            scroll_step = random.randint(300, 700)
            await page.scroll_down(scroll_step)
            await page.sleep(random.uniform(*self.scroll_sleep_range))

        raw_cookies = await self.browser.cookies.get_all()
        cookies_list = [
            Cookie(name=c.name, value=c.value, domain=c.domain)
            for c in raw_cookies
            if c.value
        ]
        return Cookies(cookies=cookies_list)

    async def close(self) -> None:
        if self.browser:
            with suppress(Exception):
                self.browser.stop()
            self.browser = None


class OzonCookieManager:
    """Оркестратор: кеш в Redis + single-flight обновление через браузер."""

    def __init__(self, storage: RedisCookieStorage, browser: OzonParserBrowser):
        self.storage = storage
        self.browser = browser
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @validate_call
    async def collect_cookies(self, url: HttpUrl, force: bool = False) -> Cookies:
        if not force:
            cached = await self.storage.get()
            if cached:
                return cached

        async with self._lock:
            if not force:
                cached = await self.storage.get()
                if cached:
                    return cached

            cookies = await self.browser.refresh_cookies(str(url))
            await self.storage.set(cookies)
            return cookies

    async def close(self) -> None:
        async with self._lock:
            await self.storage.close()
            await self.browser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


async def main():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Referer": "https://ozon.kz/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    storage = RedisCookieStorage()
    browser = OzonParserBrowser(headless=False)
    async with OzonCookieManager(storage=storage, browser=browser) as manager:
        cookies = await manager.collect_cookies(HttpUrl("https://www.ozon.kz/"))
        print(f"Всего собрано кук: {len(cookies.cookies)}")

    curl_parser = OzonParserCurl(impersonate="chrome131", headers=headers)
    curl_parser.set_cookies(cookies)
    response = await curl_parser.get(
        HttpUrl(
            "https://ozon.kz/api/entrypoint-api.bx/page/json/v2?url=/product/biologicheski-aktivnaya-dobavka-k-pishche-perfecto-lux-perfekto-lyuks-4125695810/"
        )
    )
    product = OzonProductExtractor().extract(json.loads(response.text))
    print(product)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
