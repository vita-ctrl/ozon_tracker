import random
import time
from contextlib import suppress

import httpx
import nodriver as uc

from core import load_config

from ..captcha import CaptchaSolveError, OzonCaptchaSolver
from .models import Cookie, CookieCollectionError, Cookies

config = load_config()


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
        self._http_session: httpx.AsyncClient | None = None

    @property
    def http_session(self) -> httpx.AsyncClient:
        if self._http_session is None:
            self._http_session = httpx.AsyncClient()
        return self._http_session

    async def refresh_cookies(self, url: str) -> Cookies:
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        for _ in range(config.max_cookie_attempts):
            cookies = await self._collect_attempt(url)
            if cookies is not None:
                return cookies

        raise CookieCollectionError(
            f"Failed to collect cookies after {config.max_cookie_attempts} attempts"
        )

    async def _collect_attempt(self, url: str) -> Cookies | None:
        if not self.browser:
            self.browser = await uc.start(headless=self.headless)

        page = await self.browser.get(url)
        await page.sleep(3)

        solver = OzonCaptchaSolver(self.http_session)
        try:
            await solver.solve_captcha(page, config.max_captcha_solve_attempts)
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
                await self._http_session.aclose()
            self._http_session = None

        if self.browser:
            with suppress(Exception):
                self.browser.stop()
            self.browser = None
