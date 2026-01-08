from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def me(current_user=Depends(get_current_user)):
    return current_user
