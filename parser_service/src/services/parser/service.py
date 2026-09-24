import asyncio
from contextlib import suppress
from http import HTTPStatus

from curl_cffi.requests.exceptions import Timeout
from fastapi import HTTPException

from core import load_config
from services.parser import (
    OzonCookieManager,
    OzonParserCurl,
    RefreshAlreadyInProgressError,
)
from services.parser.models import CookieCollectionError
from services.product_extractor import (
    Currency,
    OutOfStockProductData,
    OzonProductExtractor,
    ProductData,
    ProductExtractError,
)

config = load_config()


class ParserService:
    def __init__(
        self,
        curl_client: OzonParserCurl,
        product_extractor: OzonProductExtractor,
        cookie_manager: OzonCookieManager,
    ):
        self.curl_client = curl_client
        self.product_extractor = product_extractor
        self.cookie_manager = cookie_manager

    async def _set_currency(self, currency: Currency):
        response = await self.curl_client.post(
            config.currency_change_url,
            json={
                "currency_code": str(currency),
            },
        )
        if not response.status_code.is_success:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Service didn't change currency successfully.",
            )

    async def check_health(self):
        healthy = await self.cookie_manager.storage.get_health()
        if not healthy:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="Service is not healthy.",
            )


    async def get_product_data(
        self, url: str, currency: Currency | None = None
    ) -> ProductData | OutOfStockProductData:
        with suppress(CookieCollectionError):
            cookies = await self.cookie_manager.collect_cookies()
            self.curl_client.set_cookies(cookies)

        if currency:
            await self._set_currency(currency)
        else:
            with suppress(HTTPException):
                await self._set_currency(config.default_currency)

        try:
            response = await self.curl_client.get(f"{config.base_api_url}{url}")
        except Timeout:
            await self.cookie_manager.storage.set_health(False)
            raise HTTPException(
                status_code=HTTPStatus.GATEWAY_TIMEOUT, detail="Service didn't respond."
            )

        if not response.status_code.is_success:
            await self.cookie_manager.storage.set_health(False)

            async def _refresh():
                with suppress(CookieCollectionError, RefreshAlreadyInProgressError):
                    await self.cookie_manager.collect_cookies(
                        force=True, retry_after_exc=True
                    )

            asyncio.create_task(_refresh())
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="Service didn't respond successfully.",
            )

        try:
            product_data = self.product_extractor.extract(response.text)
        except ProductExtractError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_GATEWAY,
                detail="Cannot extract info from product.",
            )
        return product_data
