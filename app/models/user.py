import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRole(str, enum.Enum):
    customer = "customer"
    bakery_owner = "bakery_owner"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Login identifier. Unique per bakery, not globally -- the same
    # username can exist at two different bakeries since they're
    # separate storefronts.
    username: Mapped[str] = mapped_column(String(50))
    # Everything below is optional at signup by design ("lightweight
    # registration") and filled in later from account/bakery settings.
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.customer)
    # Which bakery's storefront this account belongs to. Customers are
    # scoped to the bakery they registered under; a bakery_owner's own
    # account is scoped to the bakery they own. Null only for
    # platform-level admins.
    bakery_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bakeries.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # The bakery this user OWNS (only meaningful for role=bakery_owner).
    # Distinct from bakery_id above, which is the tenant this account is
    # scoped to for login/lookup purposes.
    owned_bakery: Mapped["Bakery | None"] = relationship(
        back_populates="owner", foreign_keys="Bakery.owner_user_id", uselist=False
    )

    __table_args__ = (UniqueConstraint("username", "bakery_id", name="uq_users_username_bakery"),)
