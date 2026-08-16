# Architecture

> 🇫🇷 [Version française](../fr/architecture.md)

## Monorepo

```
architecto/
├── backend/     # FastAPI API + LangGraph agent
├── frontend/    # React UI (Vite)
├── docs/        # this documentation
└── docker-compose.yml   # Postgres + pgvector
```

## Backend

```
backend/src/architecto/
├── main.py            # FastAPI app + CORS + LangSmith activation
├── api/v1/            # aggregator: includes each feature's router
├── agent/             # LangGraph orchestration: state · prompts · nodes · graph · tools
├── core/              # cross-cutting foundations (no business logic)
│   ├── config/       # per-domain settings (app, database, llm, embeddings…)
│   ├── env/          # .env resolution + caching
│   ├── db/           # connection infra: base (DeclarativeBase) + async session
│   └── llm/          # multi-provider LLM adapters (Adapter + Registry)
└── features/          # vertical slices (business logic grouped by feature)
    ├── chat/         # router (POST /chat, POST /chat/stream) + schemas
    ├── knowledge/    # RAG: ingestion (upload) · pgvector store · search
    ├── memory/       # long-term memory: projects + decisions (ADR) + router
    ├── analysis/     # repo dependency analysis (ast, cycles, layers)
    ├── adr · architecture · database · diagrams · security/   # agent tools
    └── health/       # router
```

### Two organizing axes

- **`core/`** — **cross-cutting** foundations, no business logic: configuration,
  environment loading, database connection, LLM adapters.
- **`features/`** — business logic as **vertical slices**: each feature owns its
  router, schemas, models and tools.
- **`agent/`** — the LangGraph orchestration engine; it aggregates the tools that
  features expose (e.g. the search tool from the `knowledge` feature).

| Layer        | Responsibility                                                     |
|--------------|--------------------------------------------------------------------|
| `api`        | Aggregates and versions feature routers (no business logic).       |
| `agent`      | Orchestration: LangGraph graph, prompts, tool registry.            |
| `core`       | Cross-cutting foundations: config, env, DB connection, LLM.        |
| `features/*` | One vertical slice per domain (router · schemas · models · tools). |

## The agent (LangGraph)

The agent is a **state graph**, not a plain LLM call. This makes it extensible
(memory, human-in-the-loop, thread persistence).

```
                 needs_clarification ?
                 ┌──────────────┐
START ─▶ triage ─┤              ├─▶ clarify ─▶ END
                 └──────┬───────┘
                        │ no
                        ▼
                   ┌─────────┐  tools_condition  ┌─────────┐
                   │  agent  │ ────────────────▶ │  tools  │
                   └─────────┘ ◀──────────────── └─────────┘
                        │
                        ▼
                       END
```

- **`triage`**: decides (structured output) whether essential info is missing.
- **`clarify`**: if so, asks targeted questions and ends the turn (no premature
  answer) — this is the "copilot" behavior.
- **`agent`**: otherwise, the LLM (with its bound tools) answers or decides to call a tool.
- **`tools`**: runs the requested tool (e.g. knowledge base search).
- **`tools_condition`**: ReAct loop — while the LLM requests a tool, go through
  `tools` again; otherwise finish.

Files: [`agent/state.py`](../../backend/src/architecto/agent/state.py),
[`agent/nodes.py`](../../backend/src/architecto/agent/nodes.py),
[`agent/graph.py`](../../backend/src/architecto/agent/graph.py).

### Streaming (SSE)

Besides `POST /chat` (full response), `POST /chat/stream` streams the answer
**token by token** as Server-Sent Events. `stream_agent` turns LangGraph's
`astream_events` stream into structured events: `{type:"tool"}` (tool activity,
for transparency), `{type:"delta"}` (tokens), then `{type:"done"}` /
`{type:"error"}`.

### Thread persistence (checkpointer)

The LangGraph checkpointer is **selectable** via `AGENT_CHECKPOINTER`: `memory`
(volatile, default — dev/tests) or `postgres` (durable via `AsyncPostgresSaver`).
In postgres mode a FastAPI *lifespan* opens the saver at startup and wires the
durable graph (`build_graph_with` + `get_graph`/`set_graph`).

## RAG (knowledge base)

Architecture documents (patterns, ADRs, best practices) are indexed in **pgvector**
through `langchain-postgres`. The agent reaches them via a `search_knowledge_base`
tool it calls when a question relates to documented decisions.

**Ingestion**: two paths feed the index, both idempotent (content hash +
*delete-by-source*):

- **CLI**: `scripts/ingest.py <file|folder>` (chunking + embeddings + upsert).
- **From the client**: users upload their docs (`POST /knowledge/ingest`,
  multipart); the `source` is the original filename (stable identity). Sources can
  be listed/deleted (`GET`/`DELETE /knowledge/sources`).

## Endpoints (`/api/v1`)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Health + version |
| `POST` | `/chat` | One conversation turn (full response) |
| `POST` | `/chat/stream` | Streaming response (SSE) |
| `POST` | `/knowledge/ingest` | Ingest uploaded documents (RAG) |
| `GET` | `/knowledge/sources` | List ingested sources |
| `DELETE` | `/knowledge/sources` | Delete a source and its chunks |
| `GET` | `/memory/projects` | Projects with recorded decisions |
| `GET` | `/memory/decisions` | A project's decisions (ADRs) |

## Chat request flow

```
POST /api/v1/chat
   → schemas (ChatRequest)
   → run_agent(message, thread_id)      # agent/graph.py
       → agent_node: LLM + tools
       → [optional] tools_node: RAG
   → ChatResponse
```

## Frontend (Electron desktop app)

An **Electron** app (thin client) built with **electron-vite**. The renderer is the
**React + TypeScript** app (Tailwind + shadcn/ui, **MobX** state, system font stack).

```
frontend/
├── electron.vite.config.ts   # config for the 3 processes
├── electron-builder.yml      # packaging (win/mac/linux)
└── src/
    ├── main/index.ts         # main process: window, lifecycle, prod CSP
    ├── preload/index.ts      # typed bridge (contextBridge -> window.api)
    └── renderer/             # the React app
        ├── index.html
        └── src/              # main.tsx · router.tsx · api · stores · components · pages
```

**Security**: `contextIsolation: true`, `sandbox: true`, `nodeIntegration: false`,
minimal preload via `contextBridge`, strict CSP injected in production.

**Electron specifics**:
- routing via **`createHashRouter`** (production loads over `file://`, where history
  routing does not work);
- no `/api` proxy: the renderer calls the backend at a configurable **absolute URL**
  (`VITE_API_BASE_URL`, default `http://localhost:8000`) — consistent with the SDK.

The app is a **thin client**: the backend runs separately (local or container).

**State (MobX)** — one store per domain, aggregated by `RootStore`:
`ChatStore` (multi-conversations, streaming, tool activity), `ThemeStore`,
`UiStore` (sidebar, modals), `KnowledgeStore` (knowledge base), `DecisionsStore`
(per-project ADRs). Conversations and preferences persist in `localStorage`.

**Typed API contract** — the client (`api/client.ts`) derives its types from the
backend **OpenAPI** schema (`api/schema.d.ts`, generated by `pnpm gen:api` from
`backend/openapi.json`). A backend schema change not propagated to the front
breaks `tsc`: no more silent front/back drift.

**Robustness & tests** — an `ErrorBoundary` (global + per message) prevents blank
screens; critical stores and components are covered by **Vitest** tests
(`pnpm test`). Mermaid and the syntax highlighter are lazy-loaded (out of the
initial bundle).

## Key decisions

- **LangGraph graph** over `AgentExecutor` → extensibility.
- **LLM adapter** → provider swappable by config, see [LLM providers](llm-providers.md).
- **Per-domain configuration** → namespaced sections, see [Configuration](configuration.md).
