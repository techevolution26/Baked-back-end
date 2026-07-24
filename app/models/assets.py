"""Reusable customization assets: sticker library and color palettes."""
import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StickerAsset(Base):
    __tablename__ = "sticker_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bakery_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bakeries.id"), nullable=True)  # null = global library
    name: Mapped[str] = mapped_column(String(100))
    thumbnail_url: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(80))


class ColorPalette(Base):
    __tablename__ = "color_palettes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bakery_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bakeries.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(80))
    hex: Mapped[str] = mapped_column(String(7))
    swatch_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
