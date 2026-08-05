import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from architecto.api.v1.router import api_router
from architecto.core.config import settings


def _configure_langsmith() -> None:
    """Propage la config LangSmith aux variables d'env lues par LangChain."""
    if not settings.langsmith.enabled:
        return
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_API_KEY", settings.langsmith.api_key.get_secret_value())
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langsmith.project)
    os.environ.setdefault("LANGSMITH_ENDPOINT", settings.langsmith.endpoint)


def create_app() -> FastAPI:
    _configure_langsmith()

    app = FastAPI(
        title=settings.app.name,
        version="0.1.0",
        debug=settings.app.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.app.api_v1_prefix)
    return app


app = create_app()
