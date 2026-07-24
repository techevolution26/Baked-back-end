from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import get_current_user
from ..models import User
from ..schemas import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    await session.commit()
    await session.refresh(current_user)
    return current_user
