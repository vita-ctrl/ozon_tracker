import json
from typing import ClassVar

from .exceptions import ProductExtractError
from .extractors.base import WidgetExtractor
from .extractors.json_ld import JsonLdExtractor
from .extractors.out_of_stock import OutOfStockExtractor
from .extractors.widgets import (
    BigPromoExtractor,
    BrandExtractor,
    CharacteristicsExtractor,
    DetailSkuExtractor,
    GalleryExtractor,
    HeadingExtractor,
    MainWidgetExtractor,
    PriceExtractor,
    RatingExtractor,
    SellerExtractor,
)
from .models import (
    BigPromo,
    CharacteristicItem,
    OutOfStockProductData,
    ProductData,
    ProductDataDict,
    ProductType,
)
from .widget_states import WidgetStates


class OzonProductExtractor:
    FILL_KEYS: ClassVar[set[str]] = {
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

    def extract(self, json_data: dict | str) -> ProductData | OutOfStockProductData:
        try:
            if isinstance(json_data, str):
                json_data = json.loads(json_data)
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
        except Exception as e:
            raise ProductExtractError("Failed to extract product data") from e


def fill(data: ProductDataDict, key: str, value) -> None:
    if key not in data or data[key] is None:
        data[key] = value


__all__ = [
    "BigPromo",
    "CharacteristicItem",
    "OutOfStockProductData",
    "OzonProductExtractor",
    "ProductData",
    "ProductDataDict",
    "ProductType",
    "ProductExtractError",
    "WidgetExtractor",
    "WidgetStates",
]
