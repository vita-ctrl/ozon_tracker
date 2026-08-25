import json

from ..models import ProductDataDict
from ..utils import _to_int, _to_str


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
