import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Numeric, DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OrderStatus(str, enum.Enum):
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    baking = "baking"
    ready = "ready"
    delivered = "delivered"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blueprint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blueprints.id"), unique=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    bakery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bakeries.id"), index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    payment_status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.pending)
    order_status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.submitted)
    mpesa_transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    blueprint: Mapped["Blueprint"] = relationship(back_populates="order")
