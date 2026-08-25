from pydantic import BaseModel

CAPTCHA_TEXTS = (
    "Подтвердите, что вы не бот",
    "Подтвердите, что Вы не бот",
    "Сопоставьте пазл",
    "передвигая ползунок",
)

MAX_DRAG_ITERATIONS = 50


class CaptchaPosition(BaseModel):
    top: int
    left: int


class CaptchaSolveError(RuntimeError):
    pass
