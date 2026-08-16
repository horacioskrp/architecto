"""Tests smoke : import du paquet + construction des objets (sans réseau)."""

import architecto_sdk
from architecto_sdk import (
    ArchitectoClient,
    AsyncArchitectoClient,
    ChatRequest,
    ChatResponse,
)


def test_version_exposee():
    assert architecto_sdk.__version__


def test_client_synchrone_se_construit():
    client = ArchitectoClient("http://localhost:8000")
    assert client is not None


def test_client_async_se_construit():
    client = AsyncArchitectoClient("http://localhost:8000")
    assert client is not None


def test_modeles_valident_les_champs():
    req = ChatRequest(message="Propose une archi", thread_id="t")
    assert req.message == "Propose une archi"

    resp = ChatResponse(thread_id="t", answer="ok")
    assert resp.answer == "ok"
