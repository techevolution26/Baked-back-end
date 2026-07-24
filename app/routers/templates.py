import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import require_role
from ..models import Bakery, DesignTemplate, User, UserRole
from ..schemas import DesignTemplateCreate, DesignTemplateOut

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[DesignTemplateOut])
async def list_templates(
    bakery_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(DesignTemplate).where(DesignTemplate.is_active.is_(True))
    if bakery_id:
        query = query.where(DesignTemplate.bakery_id == bakery_id)
    result = await session.scalars(query)
    return result.all()


@router.post("", response_model=DesignTemplateOut)
async def create_template(
    payload: DesignTemplateCreate,
    current_user: User = Depends(require_role(UserRole.bakery_owner, UserRole.admin)),
    session: AsyncSession = Depends(get_session),
):
    bakery = await session.scalar(select(Bakery).where(Bakery.owner_user_id == current_user.id))
    if not bakery:
        raise HTTPException(status_code=404, detail="You don't own a bakery yet")

    template = DesignTemplate(
        bakery_id=bakery.id,
        name=payload.name,
        base_shape=payload.base_shape,
        base_price=payload.base_price,
        cover_image_url=payload.cover_image_url,
        tags=payload.tags,
        customizable_fields=payload.customizable_fields,
    )
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


@router.get("/{template_id}", response_model=DesignTemplateOut)
async def get_template(template_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    template = await session.get(DesignTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
