"""Shared FastAPI dependencies for the API layer."""

from typing import Annotated  # Lets us declare reusable `Depends(...)` type aliases.

from fastapi import Depends, HTTPException, status  # Depends: dependency injection; HTTPException/status: 401 responses.
from fastapi.security import OAuth2PasswordBearer  # Reads "Authorization: Bearer <token>" and powers Swagger's Authorize button.
from jose import JWTError  # Raised by decode_access_token for bad signature, malformed token, or expiry.

from app.core.security import decode_access_token  # Verifies the JWT and returns its payload.

# Tells FastAPI where clients obtain tokens. This also makes the "Authorize"
# button in /docs work. If the auth router is mounted under a prefix
# (e.g. /api/v1), tokenUrl must include it, such as "/api/v1/auth/login".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _credentials_exception() -> HTTPException:
    """Build the single 401 response used for every auth failure.

    One generic message avoids leaking whether a token was malformed,
    expired, or missing its subject. The WWW-Authenticate header is required
    by the OAuth2 bearer spec for 401 responses.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Resolve the authenticated user's id from the bearer token.

    Steps:
        1. `oauth2_scheme` extracts the token (401 automatically if the
           Authorization header is absent or not a Bearer token).
        2. The token is verified and decoded (signature and expiry).
        3. The user id is read from the standard `sub` claim.

    Returns:
        The user id as a string. No database lookup is done yet; a later
        version will load and return the `User` object.

    Raises:
        HTTPException: 401 if the token is invalid, expired, or has no `sub`.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise _credentials_exception() from None

    user_id = payload.get("sub")
    if not user_id:
        raise _credentials_exception()

    return str(user_id)


# Reusable alias so routes can write `user_id: CurrentUserId`
# instead of repeating `Depends(get_current_user)` everywhere.
CurrentUserId = Annotated[str, Depends(get_current_user)]