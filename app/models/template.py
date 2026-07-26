import uuid

from sqlalchemy import String, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DesignTemplate(Base):
    __tablename__ = "design_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bakery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bakeries.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    # A short "why we made this" fun fact or recipe history -- narrative
    # only, not used in pricing/layout.
    story: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Ordered bottom-to-top, e.g. [{"shape": "round"}, {"shape": "square"}]
    # -- replaces the old flat base_shape string now that tier count and
    # per-tier shape are both configurable in the Bakery Studio.
    tiers: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2))
    cover_image_url: Mapped[str] = mapped_column(String(500))
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    # The bakery owner's authored default appearance, assembled in the
    # Bakery Studio -- same layer format as Blueprint.layers. A
    # customer's blueprint starts as a copy of this, then gets modified
    # within whatever customizable_fields allows.
    layers: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    # What the customer is allowed to change once the lightweight
    # customer-facing editor exists -- see
    # schemas.template.TemplateCustomizationRules for the shape.
    customizable_fields: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bakery: Mapped["Bakery"] = relationship(back_populates="templates")