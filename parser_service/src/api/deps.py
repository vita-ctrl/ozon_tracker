from typing import Annotated

from fastapi import Depends, Request

from core import load_config
from services import OzonParserCurl, OzonProductExtractor, ParserService
from services.parser import OzonCookieManager

config = load_config()

def get_cookie_manager(request: Request) -> OzonCookieManager:
    return request.app.state.cookie_manager

def get_parser_service(request: Request) -> ParserService:
    product_extractor = OzonProductExtractor()
    curl_client = OzonParserCurl(config.headers)
    cookie_manager: OzonCookieManager = request.app.state.cookie_manager
    return ParserService(curl_client, product_extractor, cookie_manager)

ParserServiceDep = Annotated[ParserService, Depends(get_parser_service)]
CookieManagerDep = Annotated[OzonCookieManager, Depends(get_cookie_manager)]
