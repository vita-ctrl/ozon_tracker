import json
from typing import Any
from urllib.parse import parse_qs
from pydantic import BaseModel, field_validator, model_validator


class WebAppUser(BaseModel):
    id: int
    is_bot: bool | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    allows_write_to_pm: bool | None = None
    photo_url: str | None = None


class WebAppChat(BaseModel):
    id: int
    type: str
    title: str
    username: str | None = None
    photo_url: str | None = None


class WebAppInitData(BaseModel):
    query_id: str | None = None
    user: WebAppUser | None = None
    receiver: WebAppUser | None = None
    chat: WebAppChat | None = None
    chat_type: str | None = None
    chat_instance: str | None = None
    start_param: str | None = None
    can_send_after: int | None = None
    auth_date: int
    hash: str
    signature: str | None = None

    @classmethod
    def parse_init_data(cls, raw_data: str) -> WebAppInitData:
        return cls.model_validate(raw_data)

    @model_validator(mode="before")
    @classmethod
    def parse_init_data_params(cls, raw_data: Any) -> dict[str, Any]:
        if isinstance(raw_data, dict):
            return raw_data
        if not isinstance(raw_data, str):
            raise ValueError("init data must be a string")
        return {key: values[0] for key, values in parse_qs(raw_data).items()}

    @field_validator("user", "receiver", mode="before")
    @classmethod
    def parse_user_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

    @field_validator("chat", mode="before")
    @classmethod
    def parse_chat_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

    @field_validator("auth_date", "can_send_after", mode="before")
    @classmethod
    def parse_int(cls, value):
        if isinstance(value, str):
            return int(value)
        return value
