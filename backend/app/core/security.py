"""Password hashing and JWT utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return the bcrypt hash of a plaintext password.

    Note: bcrypt only uses the first 72 bytes of the input, so enforce a
    maximum password length at the schema layer.
    """
    return _pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash.

    Returns False (instead of raising) if the stored hash is malformed.
    """
    try:
        return _pwd_context.verify(password, hashed_password)
    except ValueError:
        return False


def create_access_token(data: dict[str, Any]) -> str:
    """Create a signed JWT access token.

    The payload is copied (the input is not mutated) and extended with the
    `iat` and `exp` claims. `exp` is computed from
    `settings.ACCESS_TOKEN_EXPIRE_MINUTES`.
    """
    now = datetime.now(UTC)
    payload = data.copy()
    payload.update(
        {
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify a JWT access token and return its payload.

    The signature and expiry are validated, and the algorithm is pinned to
    `settings.ALGORITHM`.

    Raises:
        jose.JWTError: If the token is invalid, tampered with, or expired
            (`ExpiredSignatureError` is a subclass of `JWTError`).
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


__all__ = [
    "JWTError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]