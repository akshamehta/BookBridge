"""Authentication business logic: registration and login.

This layer owns the rules (uniqueness checks, credential verification, token
issuing) and translates failures into HTTP errors. Database access is
delegated to the CRUD layer.
"""

from fastapi import HTTPException, status  # HTTP error responses.
from sqlalchemy.exc import IntegrityError  # Raised when a DB unique constraint is violated.
from sqlalchemy.orm import Session  # Synchronous database session.

from app.core.security import (  # Password and JWT utilities.
    create_access_token,
    hash_password,
    verify_password,
)
from app.crud.user import (  # Database access functions.
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.models.user import User  # ORM model, used for return type hints.
from app.schemas.auth import TokenResponse, UserLogin, UserRegister  # Request/response schemas.

# A valid bcrypt hash of a throwaway value. When a login email is unknown we
# still verify against it, so response time does not reveal whether an
# account exists (user-enumeration timing attack).
_DUMMY_PASSWORD_HASH = hash_password("bookbridge-dummy-password")


def _bad_request(detail: str) -> HTTPException:
    """Build a 400 Bad Request error with the given message."""
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _invalid_credentials() -> HTTPException:
    """Build the 401 error used for every failed login.

    The message is deliberately identical for "unknown email" and "wrong
    password" so attackers cannot tell which accounts exist. The
    WWW-Authenticate header is required by the bearer-token spec for 401s.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def register_user(db: Session, user: UserRegister) -> User:
    """Register a new user.

    Args:
        db: Active database session.
        user: Validated registration payload.

    Returns:
        The newly created `User`.

    Raises:
        HTTPException: 400 if the email or username is already in use. This
            includes the rare case where a concurrent request wins the race
            and the database unique constraint rejects the insert.
    """
    if get_user_by_email(db, user.email) is not None:
        raise _bad_request("Email already registered")

    if get_user_by_username(db, user.username) is not None:
        raise _bad_request("Username already taken")

    try:
        return create_user(db, user)
    except IntegrityError:
        # Two requests passed the checks above at the same time; the DB
        # constraint is the final safeguard. Reset the session and report it.
        db.rollback()
        raise _bad_request("Email or username already in use") from None


def login_user(db: Session, credentials: UserLogin) -> TokenResponse:
    """Authenticate a user and issue an access token.

    Args:
        db: Active database session.
        credentials: Validated login payload.

    Returns:
        A `TokenResponse` containing a signed JWT whose `sub` claim is the
        user's id.

    Raises:
        HTTPException: 401 if the email is unknown or the password is wrong.
    """
    user = get_user_by_email(db, credentials.email)

    if user is None:
        # Spend comparable time as a real check, then fail.
        verify_password(credentials.password, _DUMMY_PASSWORD_HASH)
        raise _invalid_credentials()

    if not verify_password(credentials.password, user.hashed_password):
        raise _invalid_credentials()

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)