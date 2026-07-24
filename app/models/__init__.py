"""
Re-exports every model so the rest of the app can do
`from app.models import User, Bakery, ...` without knowing which file
each lives in -- and so Alembic's target_metadata, and cross-file
relationship() string references, see everything registered on Base.
"""
from .base import Base
from .user import User, UserRole
from .bakery import Bakery
from .template import DesignTemplate
from .assets import StickerAsset, ColorPalette
from .blueprint import Blueprint
from .order import Order, OrderStatus, PaymentStatus

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Bakery",
    "DesignTemplate",
    "StickerAsset",
    "ColorPalette",
    "Blueprint",
    "Order",
    "OrderStatus",
    "PaymentStatus",
]
