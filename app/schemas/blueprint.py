import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BlueprintLayer(BaseModel):
    """One entry in blueprint.layers -- matches the layer types in the system design doc."""
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


class BlueprintCreate(BaseModel):
    template_id: uuid.UUID | None = None
    bakery_id: uuid.UUID
    tiers: list[dict[str, Any]]
    layers: list[BlueprintLayer]
    printable_elements: list[dict[str, Any]] = Field(default_factory=list)


class BlueprintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    template_id: uuid.UUID | None
    bakery_id: uuid.UUID
    tiers: list[dict[str, Any]]
    layers: list[dict[str, Any]]
    preview_render_url: str | None
