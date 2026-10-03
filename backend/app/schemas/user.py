"""Pydantic schemas for returning user data."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    """Public representation of a user.

    Built directly from the SQLAlchemy `User` model. Sensitive fields such as
    `password_hash` are intentionally absent, so they can never be serialised.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime