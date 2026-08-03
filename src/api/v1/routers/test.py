from fastapi import APIRouter, HTTPException, status


router = APIRouter()


@router.get("/test")
def test():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access forbidden",
    )
