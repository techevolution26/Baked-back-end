from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import create_access_token, hash_password, verify_password
from ..models import Bakery, User
from ..schemas import Token, UserCreate, UserOut
from ..services.tenant import require_tenant

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(
    payload: UserCreate,
    bakery: Bakery = Depends(require_tenant),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.scalar(
        select(User).where(User.username == payload.username, User.bakery_id == bakery.id)
    )
    if existing:
        raise HTTPException(status_code=400, detail="That username is already taken at this bakery")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        bakery_id=bakery.id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    bakery: Bakery = Depends(require_tenant),
    session: AsyncSession = Depends(get_session),
):
    user = await session.scalar(
        select(User).where(User.username == form.username, User.bakery_id == bakery.id)
    )
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return Token(access_token=create_access_token(user.id))
