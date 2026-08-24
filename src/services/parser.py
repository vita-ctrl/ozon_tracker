import asyncio
from contextlib import suppress
from datetime import timedelta
from http import HTTPStatus
import random
import time
import aiohttp
from curl_cffi import BrowserTypeLiteral, requests
from curl_cffi import Response as R
from pydantic import BaseModel, HttpUrl
import nodriver as uc
import redis.asyncio as aioredis

from .captcha import CaptchaSolveError, OzonCaptchaSolver


class Response(BaseModel):
    text: str
    status_code: HTTPStatus


class Cookie(BaseModel):
    name: str
    value: str
    domain: str | None = None


class Cookies(BaseModel):
    cookies: list[Cookie]


MAX_COOKIE_ATTEMPTS = 3


class CookieCollectionError(RuntimeError):
    pass


class OzonParserCurl:
    def __init__(
        self,
        headers: dict,
        *,
        impersonate: BrowserTypeLiteral = "chrome131",
    ) -> None:
        self.session = requests.AsyncSession(impersonate=impersonate)
        self.session.headers.update(headers)

    def set_cookies(self, cookies: Cookies) -> None:
        for cookie in cookies.cookies:
            self.session.cookies.set(cookie.name, cookie.value)

    def set_headers(self, headers: dict) -> None:
        self.session.headers.update(headers)

    async def get(self, url: HttpUrl) -> Response:
        resp: R = await self.session.get(str(url))
        return Response(text=resp.text, status_code=HTTPStatus(resp.status_code))


class RedisCookieStorage:
    def __init__(
        self,
        redis_url: str,
        key: str = "ozon:kz:cookies",
        ttl: timedelta = timedelta(seconds=30),
    ):
        self.redis_url = redis_url
        self.key = key
        self.ttl = ttl
        self._redis: aioredis.Redis | None = None

    async def _client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def get_ttl(self) -> int:
        redis = await self._client()
        return await redis.ttl(self.key)

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
    def __init__(
        self,
        headless: bool = False,
        duration_range: tuple[float, float] = (10.0, 30.0),
        scroll_sleep_range: tuple[float, float] = (1.0, 4.0),
        scroll_step_range: tuple[int, int] = (300, 700),
    ):
        self.headless = headless
        self.duration_range = duration_range
        self.scroll_sleep_range = scroll_sleep_range
        self.scroll_step_range = scroll_step_range
        self.browser: uc.Browser | None = None
        self._http_session: aiohttp.ClientSession | None = None

    @property
    def http_session(self) -> aiohttp.ClientSession:
        if self._http_session is None:
            self._http_session = aiohttp.ClientSession()
        return self._http_session

    async def refresh_cookies(self, url: str) -> Cookies:
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        for _ in range(MAX_COOKIE_ATTEMPTS):
            cookies = await self._collect_attempt(url)
            if cookies is not None:
                return cookies

        raise CookieCollectionError(
            f"Failed to collect cookies after {MAX_COOKIE_ATTEMPTS} attempts"
        )

    async def _collect_attempt(self, url: str) -> Cookies | None:
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        page = await self.browser.get(url)
        try:
            await page.sleep(3)

            solver = OzonCaptchaSolver(self.http_session)
            try:
                await solver.solve_captcha(page)
            except CaptchaSolveError:
                return None

            if await self._scroll_with_captcha_check(page, solver):
                return None

            raw_cookies = await self.browser.cookies.get_all()
            cookies_list = [
                Cookie(name=c.name, value=c.value, domain=c.domain)
                for c in raw_cookies
                if c.value
            ]
            return Cookies(cookies=cookies_list)
        finally:
            with suppress(Exception):
                await page.close()

    async def _scroll_with_captcha_check(
        self, page: uc.Tab, solver: OzonCaptchaSolver
    ) -> bool:
        duration = random.uniform(*self.duration_range)
        end_time = time.time() + duration
        while time.time() < end_time:
            if await solver.is_captcha(page):
                return True
            scroll_step = random.randint(*self.scroll_step_range)
            await page.scroll_down(scroll_step)
            await page.sleep(random.uniform(*self.scroll_sleep_range))
        return False

    async def close(self) -> None:
        if self._http_session:
            with suppress(Exception):
                await self._http_session.close()
            self._http_session = None

        if self.browser:
            with suppress(Exception):
                self.browser.stop()
            self.browser = None


class OzonCookieManager:
    def __init__(self, storage: RedisCookieStorage, browser: OzonParserBrowser):
        self.storage = storage
        self.browser = browser
        self._watcher_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

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

    async def watch(
        self,
        url: HttpUrl,
        referesh_bellow: timedelta = timedelta(seconds=30),
        interval: timedelta = timedelta(seconds=5),
    ) -> None:
        while True:
            await asyncio.sleep(interval.total_seconds())
            ttl = await self.storage.get_ttl()
            if ttl < referesh_bellow.total_seconds():
                await self.collect_cookies(url, force=True)

    async def start_watcher(self, url: HttpUrl) -> None:
        self._watcher_task = asyncio.create_task(self.watch(url))

    async def stop_watcher(self) -> None:
        if self._watcher_task:
            self._watcher_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._watcher_task
            self._watcher_task = None

    async def close(self) -> None:
        async with self._lock:
            await self.storage.close()
            await self.browser.close()
            await self.stop_watcher()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
