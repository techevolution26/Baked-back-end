import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models import OrderStatus, PaymentStatus


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    blueprint_id: uuid.UUID
    price: float
    payment_status: PaymentStatus
    order_status: OrderStatus
    created_at: datetime
    customer_username: str | None = None
