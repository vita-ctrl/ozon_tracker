from fastapi import APIRouter

from api.deps import UserDep
from models import User
from schemas import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(user: UserDep) -> User:
    return user
