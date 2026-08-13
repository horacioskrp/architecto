# Real-condition tests (e2e)

> 🇫🇷 [Version française](../fr/e2e.md)

How to replay the real chain (database + embeddings + agent) in a few commands.

## Prerequisites

- **Docker** (pgvector database).
- **`backend/.env`** with a chat provider (`LLM_*`, **with credit**) and an embeddings
  provider. Tip: `EMBEDDING_PROVIDER=local` (fastembed) runs **without a key** — ideal
  when chat is DeepSeek/Claude (no embeddings API).
- Extras installed depending on the provider:
  ```bash
  cd backend
  uv sync --extra dev --extra local          # + --extra deepseek for DeepSeek chat
  ```

## Procedure

```bash
docker compose up -d db                       # pgvector database
cd backend
uv run python scripts/init_db.py              # schema + vector extension
uv run python scripts/ingest.py ../docs/en    # populate the RAG
uv run python scripts/smoke.py                # ingestion + search + 1 chat turn
```

`smoke.py` prints a recap of the 3 stages. The chat turn needs a working chat provider;
if it fails (key/balance), it is **reported gracefully** without crashing.

## What it validates

| Stage | Checks |
|-------|--------|
| `init_db` | schema + `vector` extension |
| `ingest.py` | chunking + embeddings + pgvector upsert + **idempotence** |
| search | `search_knowledge_base` returns **sourced** excerpts |
| chat | the agent runs and **calls its tools** (needs a chat with credit) |

## Override the chat provider without touching `.env`

Environment variables take precedence over `.env`. DeepSeek example (key read from `.env`):

```powershell
$env:LLM_PROVIDER="deepseek"; $env:LLM_MODEL="deepseek-chat"
$env:LLM_BASE_URL="https://api.deepseek.com"
uv run python scripts/smoke.py
```

## Notes

- **Embeddings**: DeepSeek and Claude don't provide them → `EMBEDDING_PROVIDER=local`
  unblocks RAG without a key (a small ONNX model downloaded on first use).
- The database keeps its data in the `architecto_pgdata` volume (a `stop`/`start`
  preserves it). `scripts/ingest.py --reset` starts from a clean collection.
