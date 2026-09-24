from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel, field_validator

from core import Currency  # noqa: F401

from .utils import _to_float, _to_int


class ProductType(StrEnum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"


class CharacteristicItem(TypedDict):
    title: str
    values: list[str | None]


class BigPromo(BaseModel):
    title: str | None = None
    quantity: int | None = None


class ProductData(BaseModel):
    model_config = {"populate_by_name": True}
    product_type: ProductType = ProductType.IN_STOCK
    title: str
    description: str | None = None
    brand: str | None = None
    sku: int
    main_image: str | None = None
    price: float
    currency: str | None = None
    availability: str | None = None
    url: str
    rating: float | str | None = None
    review_count: int | str | None = None
    price_text: str | None = None
    original_price_text: str | None = None
    brand_label: str | None = None
    seller_raw_texts: list[str] = []
    seller_name: str | None = None
    characteristics: list[CharacteristicItem] = []
    gallery_images: list[str] = []
    big_promo: BigPromo | None = None

    @field_validator("sku", mode="before")
    @classmethod
    def coerce_sku(cls, v):
        if v is None or v == "":
            raise ValueError("Field is required")
        result = _to_int(v)
        if result == 0:
            raise ValueError("Field must be a non-zero value")
        return result

    @field_validator("price", mode="before")
    @classmethod
    def coerce_price(cls, v):
        if v is None or v == "":
            raise ValueError("Field is required")
        result = _to_float(v)
        if result == 0:
            raise ValueError("Field must be a non-zero value")
        return result

    @field_validator("title", "url", mode="before")
    @classmethod
    def check_not_empty(cls, v):
        if v is None:
            raise ValueError("Field is required")
        if isinstance(v, str) and v.strip():
            return v.strip()
        raise ValueError("Field cannot be empty")


class OutOfStockProductData(BaseModel):
    model_config = {"populate_by_name": True}
    product_type: ProductType = ProductType.OUT_OF_STOCK
    title: str | None = None
    sku: int | None = None
    main_image: str | None = None
    price_text: str | None = None
    url: str | None = None
    seller_name: str | None = None
    availability: str = "OutOfStock"
    delivery_message: str | None = None


class ProductDataDict(TypedDict, total=False):
    title: str
    description: str | None
    brand: str | None
    sku: int
    main_image: str | None
    price: float
    currency: str | None
    availability: str | None
    url: str
    rating: float | str | None
    review_count: int | str | None
    price_text: str | None
    original_price_text: str | None
    brand_label: str | None
    seller_raw_texts: list[str]
    seller_name: str | None
    characteristics: list[CharacteristicItem]
    gallery_images: list[str]
    big_promo: BigPromo | None
