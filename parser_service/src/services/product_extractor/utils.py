import re
from typing import Callable, TypeVar
from urllib.parse import urlparse, urlunparse

from core import load_config

config = load_config()

T = TypeVar("T", int, float)


def _parse_number(
    v: object,
    target_type: type[T],
    parser_func: Callable[[float], T],
    default: T,
) -> T:
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return parser_func(float(v))
    if isinstance(v, str):
        v_clean = v.strip().replace(" ", "").replace(",", ".")
        try:
            return parser_func(float(v_clean))
        except ValueError:
            m = re.search(r"\d+(?:[.,]\d+)?", re.sub(r"\s", "", v))
            if m:
                try:
                    return parser_func(float(m.group(0).replace(",", ".")))
                except ValueError:
                    return default
            return default
    return default


def _to_int(v) -> int:
    return _parse_number(v, int, round, 0)


def _to_float(v) -> float:
    return _parse_number(v, float, float, 0.0)


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
