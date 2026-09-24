from collections.abc import Iterable
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


def _build_default_extractors() -> list[WidgetExtractor]:
    return [
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

    def __init__(
        self,
        extractors: Iterable[WidgetExtractor] | None = None,
        out_of_stock_extractor: OutOfStockExtractor | None = None,
        json_ld_extractor: JsonLdExtractor | None = None,
    ) -> None:
        self._extractors = (
            list(extractors) if extractors is not None else _build_default_extractors()
        )
        self._out_of_stock_extractor = (
            out_of_stock_extractor or OutOfStockExtractor()
        )
        self._json_ld_extractor = json_ld_extractor or JsonLdExtractor()

    def extract(self, json_data: dict | str) -> ProductData | OutOfStockProductData:
        try:
            if isinstance(json_data, str):
                import json

                json_data = json.loads(json_data)
            states = WidgetStates(json_data.get("widgetStates", {}))

            if states.has("webOutOfStock"):
                return self._out_of_stock_extractor.extract(states)

            data: ProductDataDict = self._json_ld_extractor.extract(json_data)

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
