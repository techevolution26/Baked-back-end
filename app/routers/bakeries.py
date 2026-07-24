import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import get_current_user
from ..models import Bakery, User
from ..schemas import BakeryOut, BakeryUpdate
from ..services.tenant import find_bakery_by_host

router = APIRouter(prefix="/bakeries", tags=["bakeries"])


@router.get("", response_model=list[BakeryOut])
async def list_bakeries(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(Bakery).where(Bakery.verified.is_(True)))
    return result.all()


# Literal routes ("resolve", "me") must come before /{bakery_id} below --
# otherwise FastAPI tries to parse "resolve"/"me" as a bakery_id and
# 422s instead of matching these.
@router.get("/resolve", response_model=BakeryOut)
async def resolve_bakery(host: str, session: AsyncSession = Depends(get_session)):
    """Public, unauthenticated: given a Host header value, returns the
    bakery that owns it. Used by the frontend to render the correct
    storefront for whichever domain the request came in on."""
    bakery = await find_bakery_by_host(session, host)
    if not bakery:
        raise HTTPException(status_code=404, detail="No bakery found for this domain")
    return bakery


@router.get("/me", response_model=BakeryOut)
async def get_my_bakery(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    bakery = await session.scalar(select(Bakery).where(Bakery.owner_user_id == current_user.id))
    if not bakery:
        raise HTTPException(status_code=404, detail="You don't own a bakery yet")
    return bakery


@router.patch("/me", response_model=BakeryOut)
async def update_my_bakery(
    payload: BakeryUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    bakery = await session.scalar(select(Bakery).where(Bakery.owner_user_id == current_user.id))
    if not bakery:
        raise HTTPException(status_code=404, detail="You don't own a bakery yet")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bakery, field, value)

    await session.commit()
    await session.refresh(bakery)
    return bakery


@router.get("/{bakery_id}", response_model=BakeryOut)
async def get_bakery(bakery_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await session.get(Bakery, bakery_id)
