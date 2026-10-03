"""API package. Re-exports every router so `main.py` can import them from `app.api`."""

from app.api.routes import auth_router

__all__ = ["auth_router"]