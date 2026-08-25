from ..models import OutOfStockProductData
from ..utils import _to_int, _to_str, clean_url, config
from ..widget_states import WidgetStates


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
