"""Authentication routes.

Thin HTTP layer: validate input (via Pydantic), inject dependencies, call the
service layer, and return the result. No business logic lives here.
"""

from typing import Annotated  # Lets us declare a reusable `Depends(...)` type alias.

from fastapi import APIRouter, Depends, status  # Router, dependency injection, status codes.
from sqlalchemy.orm import Session  # Type of the injected database session.

from app.core.database import get_db  # Dependency that yields a DB session per request.
from app.schemas.auth import TokenResponse, UserLogin, UserRegister  # Request/response schemas.
from app.schemas.user import UserResponse  # Public user representation.
from app.services.auth_service import login_user, register_user  # Authentication business logic.

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Reusable alias so each endpoint declares `db: DbSession` instead of
# repeating `Depends(get_db)`.
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={400: {"description": "Email or username already in use"}},
)
def register(payload: UserRegister, db: DbSession) -> UserResponse:
    """Create a new user account.

    - **username**: 3-30 characters, must be unique.
    - **email**: valid email address, must be unique.
    - **password**: 8-72 characters (bcrypt limit).

    Returns the created user without any sensitive fields.
    """
    return register_user(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and obtain an access token",
    responses={401: {"description": "Incorrect email or password"}},
)
def login(payload: UserLogin, db: DbSession) -> TokenResponse:
    """Authenticate with email and password.

    Returns a bearer JWT access token to send in the
    `Authorization: Bearer <token>` header of protected requests.
    """
    return login_user(db, payload)