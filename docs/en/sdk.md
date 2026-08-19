# Python SDK

> 🇫🇷 [Version française](../fr/sdk.md)

`architecto-sdk` is the official Python client: it wraps the REST API
(chat + streaming, knowledge base, long-term memory, health) with typed models
and both **synchronous** and **asynchronous** clients.
Source: [`sdk/python/`](../../sdk/python/).

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

    # Token-by-token streaming
    for event in client.stream_chat("Compare modular monolith vs microservices"):
        if event.type == "delta":
            print(event.text, end="", flush=True)

    # Knowledge base (RAG) + long-term memory
    client.ingest(["docs/patterns.md"])
    for project in client.list_projects():
        client.list_decisions(project.slug)
```

## Full surface

`chat` · `stream_chat` · `ingest` · `list_sources` · `delete_source` ·
`list_projects` · `list_decisions` · `health` — see the method and model tables
in [`sdk/python/README.md`](../../sdk/python/README.md).

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
`headers` (auth), `transport` (custom httpx, tests). Full details:
[`sdk/python/README.md`](../../sdk/python/README.md).
