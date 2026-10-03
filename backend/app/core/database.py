from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# ==========================
# SQLAlchemy Engine
# ==========================

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


# ==========================
# Session Factory
# ==========================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ==========================
# Base Model
# ==========================

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass


# ==========================
# Database Dependency
# ==========================

def get_db() -> Generator[Session, None, None]:
    """
    Creates a new database session for each request.

    The session is automatically closed after the request finishes.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()