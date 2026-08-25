import hashlib
import hmac
import time
from datetime import timedelta
from urllib.parse import parse_qsl

from pydantic import ValidationError
from schemas import WebAppInitData


def verify_init_data(
    init_data_raw: str,
    bot_token: str,
    expire_at: timedelta = timedelta(minutes=5),
) -> bool:
    parsed = dict(parse_qsl(init_data_raw, keep_blank_values=True))

    received_hash = parsed.get("hash")
    if not received_hash:
        return False

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed.items()) if key != "hash"
    )

    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return False

    try:
        data = WebAppInitData.parse_init_data(init_data_raw)
    except ValidationError:
        return False

    return not time.time() - data.auth_date > expire_at.total_seconds()
