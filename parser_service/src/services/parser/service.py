from core import load_config
from services.parser import OzonCookieManager, OzonParserCurl
from services.product_extractor import OzonProductExtractor

config = load_config()


class ParserService:
    def __init__(
        self, curl_client: OzonParserCurl, product_extractor: OzonProductExtractor, cookie_manager: OzonCookieManager
    ):
        self.curl_client = curl_client
        self.product_extractor = product_extractor
        self.cookie_manager = cookie_manager

    async def get_product_data(self, url: str):
        cookies = await self.cookie_manager.collect_cookies()
        self.curl_client.set_cookies(cookies)
        response = await self.curl_client.get(f"{config.base_api_url}{url}")
        product_data = self.product_extractor.extract(response.text)

        return product_data
