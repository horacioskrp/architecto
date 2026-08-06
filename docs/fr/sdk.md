# SDK Python

> 🇬🇧 [English version](../en/sdk.md)

`architecto-sdk` est le client Python officiel : il encapsule l'API REST
(`/api/v1/chat`, `/api/v1/health`) avec des modèles typés et des clients
**synchrone** et **asynchrone**. Code : [`sdk/python/`](../../sdk/python/).

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
```

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
`headers` (auth). Détails complets : [`sdk/python/README.md`](../../sdk/python/README.md).
