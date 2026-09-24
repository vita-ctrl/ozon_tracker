import asyncio
from contextlib import suppress

from core import load_config

from .browser import OzonParserBrowser
from .models import CookieCollectionError, Cookies, RefreshAlreadyInProgressError
from .storage import RedisCookieStorage

config = load_config()


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

    async def collect_cookies(
        self, *, force: bool = False, retry_after_exc: bool = False, browser=False
    ) -> Cookies:
        if not force:
            cached = await self.storage.get_cookies()
            if cached:
                return cached

        if not browser:
            raise CookieCollectionError("Browser cookie collection is disabled")

        if force:
            acquired = await self.storage.acquire_refresh_lock()
            if not acquired:
                raise RefreshAlreadyInProgressError()

        async with self._lock:
            try:
                try:
                    cookies = await self.browser.refresh_cookies(config.base_url)
                except CookieCollectionError:
                    if not retry_after_exc:
                        raise
                    await self.browser.restart_browser()
                    cookies = await self.browser.refresh_cookies(config.base_url)

                await self.storage.set(cookies)
                await self.storage.set_health(True)
                return cookies
            finally:
                if force:
                    await self.storage.release_refresh_lock()

    async def watch(self) -> None:
        refresh_bellow, interval = (
            config.watch_cookies_refresh_bellow,
            config.watch_cookies_interval,
        )

        while True:
            ttl = await self.storage.get_cookies_ttl()
            if ttl < refresh_bellow.total_seconds():
                with suppress(RefreshAlreadyInProgressError):
                    await self.collect_cookies(force=True, retry_after_exc=True, browser=True)
            await asyncio.sleep(interval.total_seconds())

    async def start_watcher(self) -> None:
        self._watcher_task = asyncio.create_task(self.watch())

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
