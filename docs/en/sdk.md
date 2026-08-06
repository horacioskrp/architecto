# Python SDK

> 🇫🇷 [Version française](../fr/sdk.md)

`architecto-sdk` is the official Python client: it wraps the REST API
(`/api/v1/chat`, `/api/v1/health`) with typed models and both **synchronous** and
**asynchronous** clients. Source: [`sdk/python/`](../../sdk/python/).

## Installation

```bash
uv add architecto-sdk
# or locally from the monorepo:
uv pip install -e sdk/python
```

## Synchronous

```python
from architecto_sdk import ArchitectoClient

with ArchitectoClient("http://localhost:8000") as client:
    print(client.health().version)
    print(client.chat("Propose an architecture for a booking API").answer)
```

## Asynchronous

```python
import asyncio
from architecto_sdk import AsyncArchitectoClient

async def main() -> None:
    async with AsyncArchitectoClient("http://localhost:8000") as client:
        print((await client.chat("Modular monolith or microservices?")).answer)

asyncio.run(main())
```

## Errors

- `ArchitectoAPIError` — HTTP response >= 400 (`.status_code`, `.body`)
- `ArchitectoConnectionError` — network / timeout
- all inherit from `ArchitectoError`

## Configuration

`base_url`, `api_prefix` (`/api/v1`), `timeout` (60s), `max_retries` (2),
`headers` (auth). Full details: [`sdk/python/README.md`](../../sdk/python/README.md).
