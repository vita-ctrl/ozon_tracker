from typing import Literal

from pydantic import Field

from schemas import WebAppUser


class UserOut(WebAppUser):
    notification_threshold: float = Field(5.0, ge=0, le=100)
    check_frequency_hours: Literal[3, 6, 24] = 6
    notifications_paused: bool = False
