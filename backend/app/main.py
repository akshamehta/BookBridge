"""BookBridge FastAPI application entrypoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager  # Builds the lifespan from a generator function.

from fastapi import FastAPI  # The application class.

from app.api import auth_router  # Authentication routes.
from app.core.config import settings  # Application settings (APP_NAME, ...).
from app.core.database import engine  # SQLAlchemy engine, disposed on shutdown.


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown.

    Startup: nothing to do yet. Database tables are NOT created here;
    schema changes are managed exclusively by Alembic migrations.

    Shutdown: close all pooled database connections cleanly.
    """
    # --- startup ---
    yield
    # --- shutdown ---
    engine.dispose()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(auth_router)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Return a simple message confirming the API is running."""
    return {"message": "BookBridge API is running"}