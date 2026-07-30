import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import get_current_user, require_role
from ..models import Bakery, Blueprint, DesignTemplate, Order, OrderStatus, User, UserRole
from ..schemas import OrderOut
from ..services.pricing import calculate_blueprint_price

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
async def list_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Customers see their own orders; a bakery owner sees orders placed
    with the bakery they own; admins see everything."""
    if current_user.role == UserRole.bakery_owner:
        bakery = await session.scalar(select(Bakery).where(Bakery.owner_user_id == current_user.id))
        if not bakery:
            return []
        query = select(Order).where(Order.bakery_id == bakery.id)
    elif current_user.role == UserRole.admin:
        query = select(Order)
    else:
        query = select(Order).where(Order.customer_id == current_user.id)

    result = await session.scalars(query.order_by(Order.created_at.desc()))
    return result.all()


@router.post("", response_model=OrderOut)
async def create_order(
    blueprint_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    blueprint = await session.get(Blueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    base_price = Decimal("0")
    if blueprint.template_id:
        template = await session.get(DesignTemplate, blueprint.template_id)
        if template:
            base_price = Decimal(str(template.base_price))

    price = calculate_blueprint_price(base_price, blueprint.layers)

    order = Order(
        blueprint_id=blueprint.id,
        customer_id=current_user.id,
        bakery_id=blueprint.bakery_id,
        price=price,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: uuid.UUID,
    new_status: OrderStatus,
    current_user: User = Depends(require_role(UserRole.bakery_owner, UserRole.admin)),
    session: AsyncSession = Depends(get_session),
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.order_status = new_status
    await session.commit()
    await session.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Performing a joined query to pull order data along with the associated customer user profile info
    query = (
        select(Order, User.username)
        .join(User, Order.customer_id == User.id)
        .where(Order.id == order_id)
    )
    result = await session.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order, username = row

    if current_user.id != order.customer_id and current_user.role not in (
        UserRole.bakery_owner,
        UserRole.admin,
    ):
        raise HTTPException(status_code=403, detail="Not permitted")
        
    # Append the dynamically fetched username text straight onto the response object
    order.customer_username = username
    return order

