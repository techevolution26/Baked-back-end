import uuid
from datetime import datetime

from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Bakery(Base):
    __tablename__ = "bakeries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("users.id", name="fk_bakeries_owner_user_id_users", use_alter=True), 
    unique=True)
    name: Mapped[str] = mapped_column(String(150))
    location: Mapped[str] = mapped_column(String(255))
    mpesa_till: Mapped[str | None] = mapped_column(String(20), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Platform-provided slug, e.g. "sweetfig" -> sweetfig.<PLATFORM_DOMAIN>.
    subdomain: Mapped[str | None] = mapped_column(String(63), unique=True, nullable=True, index=True)
    # Optional bring-your-own domain, e.g. "sweetfigbakery.com", once verified.
    custom_domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)

    owner: Mapped["User"] = relationship(back_populates="owned_bakery", foreign_keys=[owner_user_id])
    templates: Mapped[list["DesignTemplate"]] = relationship(back_populates="bakery")
