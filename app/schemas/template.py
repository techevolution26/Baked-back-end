import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class BlueprintLayer(BaseModel):
    """One entry in a layers[] array -- matches the layer types in the
    system design doc. Defined here since DesignTemplate needs it for
    its own `layers` field; Blueprint imports it from here too."""
    type: str
    target: str | None = None
    swatch_id: str | None = None
    asset_id: str | None = None
    x: float | None = None
    y: float | None = None
    scale: float | None = None
    rotation: float | None = None
    url: str | None = None
    value: str | None = None
    font: str | None = None


class TierConfig(BaseModel):
    """One tier, bottom-to-top. Shape is per-tier so a design can mix
    e.g. a round bottom tier with a square top tier. Weight is
    customer-adjustable even when shape/count aren't -- quantity is a
    checkout concern, not a design-customization one."""
    shape: Literal["round", "square"] = "round"
    kg: float = 1.0


class TemplateCustomizationRules(BaseModel):
    colors_editable: bool = True
    stickers_editable: bool = True
    max_stickers: int = 5


class DesignTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    bakery_id: uuid.UUID
    name: str
    story: str | None
    tiers: list[TierConfig]
    base_price: float
    cover_image_url: str
    tags: list[str]
    layers: list[dict[str, Any]]
    customizable_fields: TemplateCustomizationRules


class DesignTemplateCreate(BaseModel):
    name: str
    story: str | None = None
    tiers: list[TierConfig] = Field(default_factory=lambda: [TierConfig()])
    base_price: float
    cover_image_url: str
    tags: list[str] = Field(default_factory=list)
    layers: list[BlueprintLayer] = Field(default_factory=list)
    customizable_fields: TemplateCustomizationRules = Field(default_factory=TemplateCustomizationRules)