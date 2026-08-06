# architecto-sdk (Python)

SDK client Python pour l'agent [Architecto](../../README.md). Encapsule l'API REST
(`/api/v1/chat`, `/api/v1/health`) avec des modèles typés et des clients sync + async.

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
    reply = client.chat("Propose une architecture pour une API de réservation")
    print(reply.answer)
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
| `chat(message, thread_id="default")` | `ChatResponse` | `POST /api/v1/chat` |
| `health()` | `HealthStatus` | `GET /api/v1/health` |

Modèles : `ChatRequest`, `ChatResponse`, `HealthStatus` (Pydantic v2).
