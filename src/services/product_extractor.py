import json
import re
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel, field_validator

from core import load_config


config = load_config()


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
    price: int
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

    @field_validator("sku", "price", mode="before")
    @classmethod
    def coerce_int(cls, v):
        if v is None or v == "":
            raise ValueError("Field is required")
        result = _to_int(v)
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
    price: int
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


def _to_int(v):
    if v is None:
        return 0
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        v = re.sub(r"[^\d]", "", v)
        return int(v) if v else 0
    return int(v)


def _to_str(v):
    if v is None:
        return ""
    return str(v).strip()


def clean_url(url: str, base_url: str) -> str:
    return urlunparse(urlparse(base_url + url)._replace(query=""))


def safe_get(obj, *path, default=None):
    for key in path:
        try:
            obj = obj[key]
        except KeyError, IndexError, TypeError:
            return default
    return obj


def find_texts_by_key(
    obj, key: str = "text", results: list[str] | None = None
) -> list[str]:
    if results is None:
        results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key and isinstance(v, str):
                results.append(v)
            else:
                find_texts_by_key(v, key, results)
    elif isinstance(obj, list):
        for item in obj:
            find_texts_by_key(item, key, results)
    return results


def extract_json_ld(json_data: dict) -> dict | None:
    seo = json_data.get("seo", {})
    scripts = seo.get("script", [])
    for script in scripts:
        inner = script.get("innerHTML", "")
        if not inner:
            continue
        try:
            data = json.loads(inner)
        except json.JSONDecodeError:
            continue
        if data.get("@type") == "Product":
            return data
    return None


def fill(data: ProductDataDict, key: str, value) -> None:
    if key not in data or data[key] is None:
        data[key] = value


class WidgetStates:
    def __init__(self, widget_states: dict[str, str]):
        self._states: dict[str, dict] = {}
        for key, value in widget_states.items():
            prefix = re.split(r"[^a-zA-Z]", key)[0]
            if prefix in self._states:
                continue
            try:
                self._states[prefix] = json.loads(value)
            except json.JSONDecodeError:
                continue

    def get(self, name: str) -> dict | None:
        return self._states.get(name)

    def has(self, name: str) -> bool:
        return name in self._states


class WidgetExtractor(ABC):
    @abstractmethod
    def extract(self, states: WidgetStates) -> ProductDataDict:
        """Returns a partially filled product data dictionary."""


class HeadingExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webProductHeading")
        if not widget:
            return {}
        return {"title": _to_str(widget.get("title"))}


class DetailSkuExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webDetailSKU")
        if not widget:
            return {}
        return {"sku": _to_int(widget.get("copyText"))}


class PriceExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webPrice")
        if not widget:
            return {}
        result: ProductDataDict = {
            "price_text": widget.get("price"),
            "original_price_text": widget.get("originalPrice"),
        }
        price = _to_int(widget.get("price"))
        if price:
            result["price"] = price
        return result


class BrandExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webBrand")
        if not widget:
            return {}
        result: ProductDataDict = {
            "brand_label": widget.get("params", {}).get("title"),
        }
        brand_name = safe_get(widget, "content", "title", "text", 0, "content")
        if isinstance(brand_name, str):
            result["brand"] = brand_name
        return result


class SellerExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webCurrentSeller")
        if not widget:
            return {}
        texts = find_texts_by_key(widget)
        seller_name: str | None = next(
            (t for t in texts if any(m in t for m in ("ООО", "ИП ", '"'))),
            None,
        )
        if not seller_name:
            seller_name = safe_get(widget, "sellerCell", "centerBlock", "title", "text")  # type: ignore[assignment]
        return {"seller_raw_texts": texts, "seller_name": seller_name}


class RatingExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        result: ProductDataDict = {}
        review_score = states.get("webReviewProductScore")
        if review_score:
            rating_val = review_score.get("totalScore")
            if rating_val is not None:
                result["rating"] = str(rating_val)
            count_val = review_score.get("reviewsCount")
            if count_val is not None:
                result["review_count"] = str(count_val)
        if not result.get("rating"):
            single_score = states.get("webSingleProductScore")
            if single_score:
                text = single_score.get("text", "")
                if text:
                    m = re.match(r"([\d.]+)", text)
                    if m:
                        result["rating"] = m.group(1)
        return result


class CharacteristicsExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webShortCharacteristics")
        return {"characteristics": self._extract(widget) if widget else []}

    def _extract(self, widget: dict) -> list[CharacteristicItem]:
        characteristics: list[CharacteristicItem] = []
        for c in widget.get("characteristics", []):
            title = safe_get(c, "title", "textRs", 0, "content")
            if title is None:
                continue
            values = [v.get("text") for v in c.get("values", [])]
            characteristics.append(CharacteristicItem(title=title, values=values))
        return characteristics


class GalleryExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webGallery")
        if not widget:
            return {}
        images: list[str] = [
            img["src"]
            for img in widget.get("images", [])
            if isinstance(img, dict) and isinstance(img.get("src"), str)
        ]
        result: ProductDataDict = {"gallery_images": list(dict.fromkeys(images))}
        cover = widget.get("coverImage")
        if cover:
            result["main_image"] = cover
        return result


class MainWidgetExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("webProductMainWidget")
        if not widget:
            return {}
        url_path = widget.get("url", "")
        if not url_path:
            return {}
        return {"url": clean_url(url_path, config.base_url)}


class BigPromoExtractor(WidgetExtractor):
    def extract(self, states: WidgetStates) -> ProductDataDict:
        widget = states.get("bigPromoPDP")
        if not widget:
            return {}
        title_val = safe_get(widget, "title", "text")
        title = title_val if isinstance(title_val, str) else None
        stock_text = safe_get(widget, "stockNumber", "text")
        quantity = _to_int(stock_text) if stock_text else None
        return {"big_promo": BigPromo(title=title, quantity=quantity)}


class JsonLdExtractor:
    def extract(self, json_data: dict) -> ProductDataDict:
        ld = extract_json_ld(json_data)
        if not ld:
            return {}
        offers = ld.get("offers", {})
        agg_rating = ld.get("aggregateRating", {})
        return {
            "title": _to_str(ld.get("name")),
            "description": ld.get("description"),
            "brand": ld.get("brand"),
            "sku": _to_int(ld.get("sku")),
            "main_image": ld.get("image"),
            "price": _to_int(offers.get("price")),
            "currency": offers.get("priceCurrency"),
            "availability": offers.get("availability"),
            "url": _to_str(offers.get("url")),
            "rating": agg_rating.get("ratingValue"),
            "review_count": agg_rating.get("reviewCount"),
        }


class OutOfStockExtractor:
    def extract(self, states: WidgetStates) -> OutOfStockProductData:
        widget = states.get("webOutOfStock")
        data: dict = {}
        if widget:
            sku_val = widget.get("sku")
            if sku_val is not None:
                data["sku"] = _to_int(sku_val)
            title_val = widget.get("skuName")
            if title_val:
                data["title"] = _to_str(title_val)
            price_val = widget.get("price")
            if price_val:
                data["price_text"] = price_val
            image_val = widget.get("coverImage")
            if image_val:
                data["main_image"] = image_val
            seller_val = widget.get("sellerName")
            if seller_val:
                data["seller_name"] = seller_val
            link_val = widget.get("productLink")
            if link_val:
                data["url"] = clean_url(link_val, config.base_url)
            delivery = widget.get("deliveryMessage")
            if delivery:
                data["delivery_message"] = delivery
        return OutOfStockProductData(**data)


class OzonProductExtractor:
    FILL_KEYS = {
        "title",
        "sku",
        "price",
        "brand",
        "rating",
        "review_count",
        "main_image",
        "url",
    }

    def __init__(self) -> None:
        self._extractors: list[WidgetExtractor] = [
            HeadingExtractor(),
            DetailSkuExtractor(),
            PriceExtractor(),
            BrandExtractor(),
            SellerExtractor(),
            RatingExtractor(),
            CharacteristicsExtractor(),
            GalleryExtractor(),
            MainWidgetExtractor(),
            BigPromoExtractor(),
        ]

    def extract(self, json_data: dict) -> ProductData | OutOfStockProductData:
        states = WidgetStates(json_data.get("widgetStates", {}))

        if states.has("webOutOfStock"):
            return OutOfStockExtractor().extract(states)

        data: ProductDataDict = JsonLdExtractor().extract(json_data)

        for extractor in self._extractors:
            partial = extractor.extract(states)
            for key, value in partial.items():
                if key in self.FILL_KEYS:
                    fill(data, key, value)
                else:
                    data[key] = value  # type: ignore[index]

        return ProductData(**data)
