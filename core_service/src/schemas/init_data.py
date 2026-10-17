from urllib.parse import parse_qsl

from pydantic import BaseModel


class WebAppUser(BaseModel):
    id: int
    is_bot: bool | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool = False
    allows_write_to_pm: bool = False
    added_to_attachment_menu: bool = False
    photo_url: str | None = None


class WebAppInitData(BaseModel):
    query_id: str | None = None
    user: WebAppUser | None = None
    auth_date: int
    hash: str

    @classmethod
    def parse_init_data(cls, init_data_raw: str) -> "WebAppInitData":
        """Parse Telegram WebApp initData query string into a model."""
        import json

        parsed = dict(parse_qsl(init_data_raw, keep_blank_values=True))

        # The 'user' field is a JSON-encoded string
        if "user" in parsed:
            parsed["user"] = json.loads(parsed["user"])

        if "auth_date" in parsed:
            parsed["auth_date"] = int(parsed["auth_date"])

        return cls.model_validate(parsed)
