import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import get_current_user
from ..models import Blueprint, User
from ..schemas import BlueprintCreate, BlueprintOut

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


@router.post("", response_model=BlueprintOut)
async def create_blueprint(
    payload: BlueprintCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    blueprint = Blueprint(
        template_id=payload.template_id,
        customer_id=current_user.id,
        bakery_id=payload.bakery_id,
        category=payload.category,
        tiers=[tier.model_dump() for tier in payload.tiers],
        layers=[layer.model_dump(exclude_none=True) for layer in payload.layers],
        printable_elements=payload.printable_elements,
    )
    session.add(blueprint)
    await session.commit()
    await session.refresh(blueprint)
    return blueprint


@router.get("/{blueprint_id}", response_model=BlueprintOut)
async def get_blueprint(blueprint_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    blueprint = await session.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint