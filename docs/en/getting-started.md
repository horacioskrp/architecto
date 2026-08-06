# Getting started

> 🇫🇷 [Version française](../fr/getting-started.md)

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Docker (for Postgres + pgvector)

## 1. Database

Postgres with pgvector, exposed on host port **5433** (to avoid clashing with a
local Postgres on 5432):

```bash
docker compose up -d db
```

## 2. Backend

```bash
cd backend
cp .env.example .env        # fill in keys (LLM_API_KEY, EMBEDDING_API_KEY…)
uv sync
uv run python scripts/init_db.py     # vector extension + tables
uv run uvicorn architecto.main:app --reload
```

- API: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs
- Health: `GET /api/v1/health`

Test the chat:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Propose an architecture for a booking API", "thread_id": "demo"}'
```

## 3. Desktop app (Electron)

```bash
cd frontend
corepack enable pnpm   # enable pnpm (bundled with Node)
pnpm install
pnpm dev               # launches the Electron app
```

The **Electron** app (thin client) targets the backend at an absolute URL
(`http://localhost:8000` by default, overridable via `VITE_API_BASE_URL`).

Package an installer: `pnpm build:win` (or `build:mac` / `build:linux`).

## Optional providers

The base install ships Anthropic (chat) and OpenAI (embeddings). For Gemini or
DeepSeek:

```bash
uv add langchain-google-genai     # Gemini
uv add langchain-deepseek         # DeepSeek
```

Then change `LLM_PROVIDER` in `.env`. See [LLM providers](llm-providers.md).

## Backend with Docker

The `docker-compose.yml` orchestrates the database and API (the desktop app runs
locally):

```bash
cp backend/.env.example backend/.env   # set LLM keys (optional for /health)
docker compose up --build              # db + backend
```

- Backend: http://localhost:8000
- The `backend` service initializes the schema (vector extension + tables) on startup.

Image details:

| Service | Image | Notes |
|---------|-------|-------|
| `backend` | multi-stage Python 3.12 + uv, non-root runtime | `Dockerfile` |
| `db` | `pgvector/pgvector:pg16` | volume `architecto_pgdata` |

Within the docker network the backend reaches the database at `db:5432`
(`DB_HOST`/`DB_PORT` overridden in compose).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Intégration manquante pour le provider …` | provider package not installed | `uv add langchain-<provider>` |
| DB connection refused | container not started / wrong port | `docker compose up -d db`, check `DB_PORT=5433` |
| 401 from the LLM | missing/invalid API key | set `LLM_API_KEY` in `.env` |
