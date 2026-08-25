import re
from urllib.parse import urlparse, urlunparse

from core import load_config

config = load_config()


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
        except (KeyError, IndexError, TypeError):
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
