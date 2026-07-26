import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Blueprint(Base):
    __tablename__ = "blueprints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("design_templates.id"), nullable=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    bakery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bakeries.id"), index=True)
    # The customer's actual tier structure -- usually a copy of the
    # template's tiers, same shape as DesignTemplate.tiers.
    tiers: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    layers: Mapped[list[dict]] = mapped_column(JSONB)
    preview_render_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    printable_elements: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["Order | None"] = relationship(back_populates="blueprint", uselist=False)