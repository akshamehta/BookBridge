"""Pydantic schemas for authentication requests and responses."""

from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

# bcrypt is built on the Blowfish cipher, whose key schedule accepts at most
# 72 bytes of key material. Anything beyond that is silently truncated (or
# rejected by newer bcrypt releases), so two long passwords sharing the same
# first 72 bytes would be treated as identical. We therefore cap the input.
PASSWORD_MAX_BYTES = 72

Username = Annotated[str, Field(min_length=3, max_length=30)]
Password = Annotated[str, Field(min_length=8, max_length=PASSWORD_MAX_BYTES)]


def _check_password_bytes(value: str) -> str:
    """Reject passwords whose UTF-8 encoding exceeds bcrypt's 72-byte limit.

    `max_length` counts characters, but bcrypt limits bytes, and a single
    non-ASCII character can take up to 4 bytes.
    """
    if len(value.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise ValueError(f"Password must be at most {PASSWORD_MAX_BYTES} bytes long")
    return value


class UserRegister(BaseModel):
    """Payload for registering a new account."""

    username: Username
    email: EmailStr
    password: Password

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)


class UserLogin(BaseModel):
    """Payload for logging in with email and password."""

    email: EmailStr
    # No length rules on purpose: login should fail with "invalid credentials",
    # not reveal the password policy. The 72-byte guard still protects bcrypt.
    password: Annotated[str, Field(min_length=1, max_length=PASSWORD_MAX_BYTES)]

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)


class TokenResponse(BaseModel):
    """OAuth2-style bearer token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"