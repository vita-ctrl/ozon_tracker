from http import HTTPStatus
from typing import Annotated
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query

from api.deps import ParserServiceDep
from core import Currency
from services import OutOfStockProductData, ProductData

router = APIRouter()


@router.get(
    "/products/",
    response_model=ProductData | OutOfStockProductData,
    summary="Retrieve a product info",
)
async def get_product(
    parser_service: ParserServiceDep,
    url: Annotated[str, Query()],
    currency: Annotated[Currency | None, Query()] = None,
):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid URL.")
    product_url = parsed.path
    product = await parser_service.get_product_data(product_url, currency=currency)
    return product
