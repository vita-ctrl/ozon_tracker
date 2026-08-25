from http import HTTPStatus

from curl_cffi import BrowserTypeLiteral, requests
from curl_cffi import Response as R

from .models import Cookies, Response


class OzonParserCurl:
    def __init__(
        self,
        headers: dict,
        *,
        impersonate: BrowserTypeLiteral = "chrome131",
    ) -> None:
        self.session = requests.AsyncSession(impersonate=impersonate)
        self.session.headers.update(headers)

    def set_cookies(self, cookies: Cookies) -> None:
        for cookie in cookies.cookies:
            self.session.cookies.set(cookie.name, cookie.value)

    def set_headers(self, headers: dict) -> None:
        self.session.headers.update(headers)

    async def get(self, url: str) -> Response:
        resp: R = await self.session.get(str(url))
        return Response(text=resp.text, status_code=HTTPStatus(resp.status_code))
