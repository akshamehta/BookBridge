from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)


@app.get("/")
def root():
    return {
        "message": "Welcome to BookBridge!",
        "app_name": settings.APP_NAME,
        "database": settings.POSTGRES_DB,
        "debug": settings.DEBUG,
    }