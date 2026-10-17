from pydantic import BaseModel


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None
    is_premium: bool = False
    allows_write_to_pm: bool = False
    added_to_attachment_menu: bool = False
    notification_threshold: float = 5.0
    check_frequency_hours: int = 6
    notifications_paused: bool = False
