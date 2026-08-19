# architecto-sdk (Python)

SDK client Python pour l'agent [Architecto](../../README.md). Encapsule l'API REST
(chat + streaming, base de connaissances, mémoire long terme, santé) avec des
modèles typés et des clients sync + async.

## Installation

```bash
uv add architecto-sdk
# ou, en local depuis le monorepo :
uv pip install -e sdk/python
```

## Usage — synchrone

```python
from architecto_sdk import ArchitectoClient

with ArchitectoClient("http://localhost:8000") as client:
    print(client.health().version)                 # "0.1.0"
    reply = client.chat(
        "Propose une architecture pour une API de réservation",
        project="reservations",  # scope la mémoire long terme au projet
    )
    print(reply.answer)
```

### Streaming (token par token)

```python
with ArchitectoClient() as client:
    for event in client.stream_chat("Compare monolithe modulaire vs microservices"):
        if event.type == "delta":
            print(event.text, end="", flush=True)
        elif event.type == "tool":
            print(f"\n[outil {event.name} : {event.phase}]")
```

### Base de connaissances & mémoire

```python
with ArchitectoClient() as client:
    client.ingest(["docs/patterns.md", "docs/adr-0001.md"])  # RAG
    for src in client.list_sources():
        print(src.source, src.chunk_count)

    for project in client.list_projects():
        for adr in client.list_decisions(project.slug):
            print(adr.title, "→", adr.decision)
```

## Usage — asynchrone

```python
import asyncio
from architecto_sdk import AsyncArchitectoClient

async def main() -> None:
    async with AsyncArchitectoClient("http://localhost:8000") as client:
        reply = await client.chat("Compare monolithe modulaire vs microservices")
        print(reply.answer)

asyncio.run(main())
```

## Configuration

`ArchitectoClient` / `AsyncArchitectoClient` :

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `base_url` | `http://localhost:8000` | Racine du service |
| `api_prefix` | `/api/v1` | Préfixe des routes |
| `timeout` | `60.0` | Timeout HTTP (s) |
| `max_retries` | `2` | Retries transport (erreurs réseau) |
| `headers` | `None` | En-têtes additionnels (ex. auth) |
| `transport` | `None` | Transport httpx custom (tests via `httpx.MockTransport`) |

## Gestion d'erreurs

```python
from architecto_sdk import ArchitectoClient, ArchitectoAPIError, ArchitectoConnectionError

try:
    with ArchitectoClient() as client:
        client.chat("...")
except ArchitectoAPIError as e:
    print(e.status_code, e.body)     # réponse HTTP d'erreur (>= 400)
except ArchitectoConnectionError as e:
    print("Service injoignable :", e) # réseau / timeout
```

Toutes les exceptions dérivent de `ArchitectoError`.

## API

| Méthode | Retour | Endpoint |
|---------|--------|----------|
| `chat(message, thread_id="default", project="")` | `ChatResponse` | `POST /api/v1/chat` |
| `stream_chat(message, thread_id="default", project="")` | `Iterator[ChatStreamEvent]` | `POST /api/v1/chat/stream` |
| `ingest(files)` | `IngestResult` | `POST /api/v1/knowledge/ingest` |
| `list_sources()` | `list[SourceOut]` | `GET /api/v1/knowledge/sources` |
| `delete_source(source)` | `None` | `DELETE /api/v1/knowledge/sources` |
| `list_projects()` | `list[ProjectOut]` | `GET /api/v1/memory/projects` |
| `list_decisions(project)` | `list[DecisionOut]` | `GET /api/v1/memory/decisions` |
| `health()` | `HealthStatus` | `GET /api/v1/health` |

Les méthodes async (`AsyncArchitectoClient`) sont identiques ; `stream_chat` y renvoie un `AsyncIterator[ChatStreamEvent]`.

Modèles (Pydantic v2) : `ChatRequest`, `ChatResponse`, `ChatStreamEvent`,
`HealthStatus`, `SourceOut`, `IngestResult`, `ProjectOut`, `DecisionOut`.
