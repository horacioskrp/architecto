import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from architecto.agent.chat_agent import GraphChatAgent
from architecto.agent.checkpointer import postgres_checkpointer
from architecto.agent.graph import build_graph_with, set_graph
from architecto.api.v1.router import api_router
from architecto.core.config import settings
from architecto.features.chat.ports import get_chat_agent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Câble un graphe à persistance durable si `AGENT_CHECKPOINTER=postgres`.

    Sinon on ne fait rien : l'agent utilise le graphe par défaut (checkpointer
    en mémoire), threads volatils — adapté au dev et aux tests.
    """
    if settings.agent.checkpointer == "postgres":
        async with postgres_checkpointer() as saver:
            set_graph(build_graph_with(saver))
            try:
                yield
            finally:
                set_graph(None)
    else:
        yield


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
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Racine de composition : on injecte l'implémentation concrète du port
    # ChatAgent (agent LangGraph) que la feature chat consomme via abstraction.
    app.dependency_overrides[get_chat_agent] = GraphChatAgent

    app.include_router(api_router, prefix=settings.app.api_v1_prefix)
    return app


app = create_app()
