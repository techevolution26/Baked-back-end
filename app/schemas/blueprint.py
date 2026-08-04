import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .template import TierConfig, BlueprintLayer
from ..services.pricing import DEFAULT_CATEGORY

__all__ = ["TierConfig", "BlueprintLayer", "BlueprintCreate", "BlueprintOut"]


class BlueprintCreate(BaseModel):
    template_id: uuid.UUID | None = None
    bakery_id: uuid.UUID
    category: str = DEFAULT_CATEGORY
    tiers: list[TierConfig] = Field(default_factory=lambda: [TierConfig()])
    layers: list[BlueprintLayer] = Field(default_factory=list)
    printable_elements: list[dict[str, Any]] = Field(default_factory=list)


class BlueprintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    template_id: uuid.UUID | None
    bakery_id: uuid.UUID
    category: str
    tiers: list[TierConfig]
    layers: list[dict[str, Any]]
    preview_render_url: str | None