from fastapi import APIRouter

from api.deps import ParserServiceDep

router = APIRouter()


@router.get(
    "/health/",
    summary="Check is service healthy",
)
async def health(
    parser_service: ParserServiceDep,
):
    await parser_service.check_health()
    return {"status": "ok"}
