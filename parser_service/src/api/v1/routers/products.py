from http import HTTPStatus
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query

from api.deps import ParserServiceDep

router = APIRouter()


@router.get("/products/")
async def get_product(parser_service: ParserServiceDep, url: str = Query(...)):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid URL")
    product_url = parsed.path
    response = await parser_service.get_product_data(product_url)
    return response
