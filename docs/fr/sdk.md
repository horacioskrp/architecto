# SDK Python

> 🇬🇧 [English version](../en/sdk.md)

`architecto-sdk` est le client Python officiel : il encapsule l'API REST
(chat + streaming, base de connaissances, mémoire long terme, santé) avec des
modèles typés et des clients **synchrone** et **asynchrone**.
Code : [`sdk/python/`](../../sdk/python/).

## Installation

```bash
uv add architecto-sdk
# ou en local depuis le monorepo :
uv pip install -e sdk/python
```

## Synchrone

```python
from architecto_sdk import ArchitectoClient

with ArchitectoClient("http://localhost:8000") as client:
    print(client.health().version)
    print(client.chat("Propose une architecture pour une API de réservation").answer)

    # Streaming token par token
    for event in client.stream_chat("Compare monolithe modulaire vs microservices"):
        if event.type == "delta":
            print(event.text, end="", flush=True)

    # Base de connaissances (RAG) + mémoire long terme
    client.ingest(["docs/patterns.md"])
    for project in client.list_projects():
        client.list_decisions(project.slug)
```

## Surface complète

`chat` · `stream_chat` · `ingest` · `list_sources` · `delete_source` ·
`list_projects` · `list_decisions` · `health` — voir le tableau des méthodes et
des modèles dans [`sdk/python/README.md`](../../sdk/python/README.md).

## Asynchrone

```python
import asyncio
from architecto_sdk import AsyncArchitectoClient

async def main() -> None:
    async with AsyncArchitectoClient("http://localhost:8000") as client:
        print((await client.chat("Monolithe modulaire ou microservices ?")).answer)

asyncio.run(main())
```

## Erreurs

- `ArchitectoAPIError` — réponse HTTP >= 400 (`.status_code`, `.body`)
- `ArchitectoConnectionError` — réseau / timeout
- toutes dérivent de `ArchitectoError`

## Configuration

`base_url`, `api_prefix` (`/api/v1`), `timeout` (60 s), `max_retries` (2),
`headers` (auth), `transport` (httpx custom, tests). Détails complets :
[`sdk/python/README.md`](../../sdk/python/README.md).
