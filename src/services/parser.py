import asyncio
from contextlib import suppress
from datetime import timedelta
from http import HTTPStatus
import random
import time
import aiohttp
from curl_cffi import BrowserTypeLiteral, requests
from curl_cffi import Response as R
from nodriver.core.tab import cdp
from pydantic import BaseModel, HttpUrl, validate_call
import nodriver as uc
import redis.asyncio as aioredis

from .captcha import OzonCaptchaSolver


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

    @validate_call
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


CAPTCHA_TEXTS = (
    "Подтвердите, что вы не бот",
    "Подтвердите, что Вы не бот",
    "Сопоставьте пазл",
    "передвигая ползунок",
)


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

    async def is_captcha(self, page: uc.Tab) -> bool:
        for text in CAPTCHA_TEXTS:
            element = await page.find_element_by_text(text)
            if element is not None:
                return True
        return False

    async def get_captcha_elements(self, page: uc.Tab) -> tuple[uc.Element, uc.Element]:
        captcha = await page.select("#captcha")
        if not isinstance(captcha, uc.Element):
            raise RuntimeError("Captcha element not found")
        image = await captcha.query_selector("#image")
        puzzle = await page.query_selector("#puzzle")
        if not isinstance(image, uc.Element) or not isinstance(puzzle, uc.Element):
            raise RuntimeError("Captcha or puzzle element not found")
        return image, puzzle

    async def test(self, url: str, time_to_sleep: int) -> None:
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        page = await self.browser.get(url)

        await page.sleep(time_to_sleep)

    async def drag_slider(
        self, tab, slider_element, distance_x: float, steps: int = 30
    ) -> tuple[int, int]:
        pos = await slider_element.get_position()
        start_x = pos.center[0]
        start_y = pos.center[1]

        # 1. Зажимаем — mousePressed, БЕЗ mouseReleased
        await tab.send(
            cdp.input_.dispatch_mouse_event(
                type_="mousePressed",
                x=start_x,
                y=start_y,
                button=cdp.input_.MouseButton("left"),
                buttons=1,
                click_count=1,
            )
        )
        await asyncio.sleep(random.uniform(0.05, 0.15))

        # 2. Двигаем мышь пошагово, кнопка всё ещё "зажата" (buttons=1)
        current_x = start_x
        for i in range(1, steps + 1):
            # человекоподобная траектория: небольшой джиттер + неравномерный шаг
            progress = i / steps
            eased = 1 - (1 - progress) ** 2  # ease-out
            target_x = start_x + distance_x * eased
            jitter_y = start_y + random.uniform(-1.5, 1.5)

            await tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mouseMoved",
                    x=target_x,
                    y=jitter_y,
                    button=cdp.input_.MouseButton("left"),
                    buttons=1,  # важно: buttons=1 означает "кнопка всё ещё зажата"
                )
            )
            current_x = target_x
            await asyncio.sleep(random.uniform(0.01, 0.03))

        return current_x, start_y

    async def refresh_cookies(self, url: str) -> Cookies:
        print("Refreshing cookies...")
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        page = await self.browser.get(url)
        await page.sleep(3)
        is_captcha = await self.is_captcha(page)

        while is_captcha:
            async with aiohttp.ClientSession() as session:
                image, puzzle = await self.get_captcha_elements(page)
                solver = OzonCaptchaSolver(session)
                solve_result = await solver.solve_from_elements(image, puzzle)
                print(solve_result)
                slider = await page.select("#slider")
                left_puzzle = solver.parse_position(puzzle.attrs["style"]).left
                while left_puzzle < solve_result:
                    print("left_puzzle:", left_puzzle)
                    print("solve_result:", solve_result)
                    x, y = await self.drag_slider(page, slider, 10, 1)
                    attrs = await puzzle.get_js_attributes()
                    # print(attrs)
                    left_puzzle = round(float(attrs["style"]["left"].replace("px", "")))

                # 3. Отпускаем — только теперь mouseReleased
                await page.sleep(2)
                await page.send(
                    cdp.input_.dispatch_mouse_event(
                        type_="mouseReleased",
                        x=x,
                        y=y,
                        button=cdp.input_.MouseButton("left"),
                        buttons=0,
                    )
                )

                await page.sleep(2)
                is_captcha = await self.is_captcha(page)

        return

        duration = random.uniform(*self.duration_range)
        end_time = time.time() + duration
        while time.time() < end_time:
            scroll_step = random.randint(*self.scroll_step_range)
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
    def __init__(self, storage: RedisCookieStorage, browser: OzonParserBrowser):
        self.storage = storage
        self.browser = browser
        self._watcher_task: asyncio.Task | None = None
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

    @validate_call
    async def watch(
        self,
        url: HttpUrl,
        referesh_bellow: timedelta = timedelta(seconds=30),
        interval: timedelta = timedelta(seconds=5),
    ) -> None:
        captchas_url_random = open("captchas.txt", "r").read().splitlines()
        await self.browser.test(random.choice(captchas_url_random), 2)
        i = 0
        while i < 3:
            print(f"Watching cookies for {url}...")
            await asyncio.sleep(interval.total_seconds())
            print(f"Checking cookies for {url}...")
            ttl = await self.storage.get_ttl()
            if ttl < referesh_bellow.total_seconds():
                print("Cookies are about to expire, refreshing...")
                await self.collect_cookies(url, force=True)
            i += 1

    @validate_call
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
