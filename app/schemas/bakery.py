import uuid

from pydantic import BaseModel, ConfigDict


class BakeryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    location: str
    mpesa_till: str | None
    verified: bool
    rating: float


class BakeryUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    mpesa_till: str | None = None
