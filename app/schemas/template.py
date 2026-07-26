import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .blueprint import BlueprintLayer


class TemplateCustomizationRules(BaseModel):
    """What a customer is allowed to change once the lightweight
    customer-facing editor exists. The Bakery Studio sets these."""
    colors_editable: bool = True
    stickers_editable: bool = True
    max_stickers: int = 5


class DesignTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    bakery_id: uuid.UUID
    name: str
    story: str | None
    base_shape: str
    base_price: float
    cover_image_url: str
    tags: list[str]
    layers: list[dict[str, Any]]
    customizable_fields: TemplateCustomizationRules


class DesignTemplateCreate(BaseModel):
    name: str
    story: str | None = None
    base_shape: str
    base_price: float
    cover_image_url: str
    tags: list[str] = Field(default_factory=list)
    layers: list[BlueprintLayer] = Field(default_factory=list)
    customizable_fields: TemplateCustomizationRules = Field(default_factory=TemplateCustomizationRules)