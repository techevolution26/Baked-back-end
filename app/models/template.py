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
    story: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_shape: Mapped[str] = mapped_column(String(50))
    base_price: Mapped[float] = mapped_column(Numeric(10, 2))
    cover_image_url: Mapped[str] = mapped_column(String(500))
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    layers: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    customizable_fields: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bakery: Mapped["Bakery"] = relationship(back_populates="templates")