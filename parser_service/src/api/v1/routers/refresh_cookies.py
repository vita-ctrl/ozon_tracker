from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.deps import CookieManagerDep
from core import load_config
from services.parser import CookieCollectionError, RefreshAlreadyInProgressError

router = APIRouter()


class ResponseModel(BaseModel):
    success: bool
    message: str


config = load_config()


@router.post(
    "/force_refresh_cookies/",
    summary="Refresh cookies",
)
async def force_refresh_cookies(
    manager: CookieManagerDep, retry_after_exc: bool = False
):
    try:
        await manager.collect_cookies(
            force=True, retry_after_exc=retry_after_exc, browser=True
        )
        return {
            "success": True,
            "message": f"Cookies refreshed! Instance id: {config.instance_id}",
        }
    except RefreshAlreadyInProgressError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail={"success": False, "message": "Refresh already in progress."},
        )
    except CookieCollectionError as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e) or "Cookie collection failed"},
        )
