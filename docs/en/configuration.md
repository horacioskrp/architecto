# Configuration

> 🇫🇷 [Version française](../fr/configuration.md)

All configuration comes from **environment variables**, with nothing
business-related hardcoded. It is organized into **domain sections**, each with its
own prefix. Reference file: [`backend/.env.example`](../../backend/.env.example).

## Principle

- Each section is a standalone `BaseSettings` with its own `env_prefix`.
- Secrets are `SecretStr` (masked in logs).
- Access is via `settings.<section>.<field>` (e.g. `settings.db.url`).
- The `.env` file is resolved **once** per process (directory walk + cache),
  independent of the current working directory.

## Sections

### `APP_` — application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Architecto` | Application name |
| `APP_ENV` | `dev` | `dev` \| `staging` \| `prod` |
| `APP_DEBUG` | `false` | FastAPI debug mode |
| `APP_API_V1_PREFIX` | `/api/v1` | Route prefix |
| `APP_HOST` | `127.0.0.1` | Bind host (loopback by default — the API is unauthenticated; the container forces `0.0.0.0`) |
| `APP_PORT` | `8000` | Bind port |

### `AGENT_` — agent behavior

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_CHECKPOINTER` | `memory` | LangGraph thread persistence: `memory` (volatile, dev/tests) \| `postgres` (durable via `AsyncPostgresSaver`, recommended in prod) |

### `DB_` — database

The Postgres URL is **composed** from its parts (nothing hardcoded).

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_DRIVER` | `postgresql+psycopg` | SQLAlchemy driver |
| `DB_HOST` | `localhost` | Host |
| `DB_PORT` | `5433` | Port (5433 to avoid a local clash) |
| `DB_USER` | `architecto` | User |
| `DB_PASSWORD` | `architecto` | Password (`SecretStr`) |
| `DB_NAME` | `architecto` | Database |
| `DB_ECHO` | `false` | SQL logging |
| `DB_POOL_SIZE` | `5` | Pool size |
| `DB_MAX_OVERFLOW` | `10` | Connections beyond the pool |
| `DB_POOL_PRE_PING` | `true` | Check connection before use |

### `LLM_` — chat model

See [LLM providers](llm-providers.md) for per-provider details.

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `anthropic` | `anthropic` \| `openai` \| `google` \| `deepseek` |
| `LLM_MODEL` | `claude-sonnet-5` | Model identifier |
| `LLM_API_KEY` | — | Provider key (`SecretStr`) |
| `LLM_TEMPERATURE` | `0.2` | Temperature |
| `LLM_MAX_TOKENS` | — | Output token limit |
| `LLM_TIMEOUT` | `60` | Timeout (s) |
| `LLM_BASE_URL` | — | Custom URL (DeepSeek, OpenAI-compatible proxies) |

### `EMBEDDING_` — embeddings (RAG)

Decoupled from chat: Anthropic provides no embeddings.

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_PROVIDER` | `openai` | `openai` \| `google` \| `local` (fastembed, **no key**) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `EMBEDDING_API_KEY` | — | Key (`SecretStr`) — unused for `local` |
| `EMBEDDING_BASE_URL` | — | Custom URL |

### `KNOWLEDGE_` — knowledge base ingestion

Guard rails applied to client-side uploads (endpoint `/knowledge/ingest`).

| Variable | Default | Description |
|----------|---------|-------------|
| `KNOWLEDGE_MAX_UPLOAD_MB` | `20` | Max size per file (MB) |
| `KNOWLEDGE_MAX_FILES` | `20` | Max files per request |

### `LANGSMITH_` — observability

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGSMITH_TRACING` | `false` | Enable tracing |
| `LANGSMITH_API_KEY` | — | Key (`SecretStr`) |
| `LANGSMITH_PROJECT` | `architecto` | Project name |
| `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` | Endpoint |

### `CORS_` — CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed origins (comma-separated) |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials |

### `RATELIMIT_` — rate limiting

Per-IP sliding window, in process memory (defense in depth; `/health` is exempt).

| Variable | Default | Description |
|----------|---------|-------------|
| `RATELIMIT_ENABLED` | `true` | Enable the rate-limiting middleware |
| `RATELIMIT_REQUESTS` | `120` | Requests allowed per window and per client |
| `RATELIMIT_WINDOW_SECONDS` | `60` | Window duration (s) |

## Overriding the `.env` file

The `ENV_FILE` variable points to a different file:

```bash
ENV_FILE=/path/to/.env.prod uv run uvicorn architecto.main:app
```

## Adding a section

1. Create `core/config/<section>.py` with a `SectionSettings` class + `env_prefix`.
2. Add it to `Settings` in `core/config/settings.py`.
3. Expose it in `core/config/__init__.py`.
4. Document its variables here (EN) and in the equivalent FR page.
