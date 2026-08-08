import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import get_current_user
from ..models import Blueprint, User, UserRole
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
async def get_blueprint(
    blueprint_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    blueprint = await session.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    if current_user.role == UserRole.admin:
        return blueprint

    if current_user.role == UserRole.bakery_owner:
        if blueprint.bakery_id != current_user.bakery_id:
            raise HTTPException(status_code=403, detail="Not permitted")
        return blueprint

    if blueprint.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not permitted")

    return blueprint
