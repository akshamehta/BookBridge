"""Database access functions for the User model.

This layer only talks to the database. Business rules (duplicate checks,
validation, error mapping) belong in the service layer.
"""

from uuid import UUID  # Type of the user primary key.

from sqlalchemy import select  # SQLAlchemy 2.0-style query construction.
from sqlalchemy.orm import Session  # Synchronous database session.

from app.core.security import hash_password  # Hashes plaintext passwords with bcrypt.
from app.models.user import User  # ORM model for the users table.
from app.schemas.auth import UserRegister  # Validated registration payload.


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email address.

    Args:
        db: Active database session.
        email: Email to look up (exact match).

    Returns:
        The matching `User`, or `None` if no user has this email.
    """
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Fetch a user by username.

    Args:
        db: Active database session.
        username: Username to look up (exact match).

    Returns:
        The matching `User`, or `None` if no user has this username.
    """
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    """Fetch a user by primary key.

    Args:
        db: Active database session.
        user_id: The user's unique identifier.

    Returns:
        The matching `User`, or `None` if it does not exist.
    """
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def create_user(db: Session, user: UserRegister) -> User:
    """Persist a new user.

    The plaintext password is hashed before storage. This function does not
    check for duplicate emails or usernames; the service layer must do that
    first. The database unique constraints remain the final safeguard, so an
    `IntegrityError` can still be raised under a race condition. The caller
    should catch it and call `db.rollback()`.

    Args:
        db: Active database session.
        user: Validated registration data.

    Returns:
        The newly created `User`, refreshed with database-generated values
        such as `id` and `created_at`.
    """
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user