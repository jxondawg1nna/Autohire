from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routes import api_router

settings = get_settings()

app = FastAPI(title="AutoHire API", version="0.1.0", openapi_url="/openapi.json")

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Lightweight service liveness probe."""

    return {"status": "ok", "environment": settings.app_env}


app.include_router(api_router, prefix="/api")
