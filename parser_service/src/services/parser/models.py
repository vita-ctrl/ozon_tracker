from http import HTTPStatus

from pydantic import BaseModel


class Response(BaseModel):
    text: str
    status_code: HTTPStatus


class Cookie(BaseModel):
    name: str
    value: str
    domain: str | None = None


class Cookies(BaseModel):
    cookies: list[Cookie]


class CookieCollectionError(RuntimeError):
    pass
