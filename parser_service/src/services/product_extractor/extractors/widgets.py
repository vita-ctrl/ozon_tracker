import re

from ..models import BigPromo, CharacteristicItem, ProductDataDict
from ..utils import (
    _to_float,
    _to_int,
    _to_str,
    clean_url,
    config,
    find_texts_by_key,
    safe_get,
)
from ..widget_states import WidgetStates
from .base import WidgetExtractor


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
        price = _to_float(widget.get("price"))
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
