import uuid

from pydantic import BaseModel, ConfigDict

from ..models import UserRole


class UserCreate(BaseModel):
    """Lightweight registration -- just enough to create an account.
    Name, phone, email are filled in later via account settings."""
    username: str
    password: str
    role: UserRole = UserRole.customer


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    name: str | None
    phone: str | None
    email: str | None
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
