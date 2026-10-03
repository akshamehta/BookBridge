"""API route package. Re-exports every router so `main.py` can import them from one place."""

from .auth import router as auth_router

__all__ = ["auth_router"]