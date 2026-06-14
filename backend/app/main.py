from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_counseling,
    routes_drugs,
    routes_health,
    routes_prescriptions,
    routes_rag,
)
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="PharmaGuard AI API",
        version="0.1.0",
        description=(
            "Foundation API for a pharmacist-centered AI copilot. "
            "All current outputs are draft-only and require pharmacist review."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes_health.router)
    app.include_router(routes_prescriptions.router)
    app.include_router(routes_drugs.router)
    app.include_router(routes_counseling.router)
    app.include_router(routes_rag.router)

    return app


app = create_app()
