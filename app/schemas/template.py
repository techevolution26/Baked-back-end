import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DesignTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    bakery_id: uuid.UUID
    name: str
    base_shape: str
    base_price: float
    cover_image_url: str
    tags: list[str]
    customizable_fields: dict[str, Any]


class DesignTemplateCreate(BaseModel):
    name: str
    base_shape: str
    base_price: float
    cover_image_url: str
    tags: list[str] = Field(default_factory=list)
    customizable_fields: dict[str, Any] = Field(default_factory=dict)
