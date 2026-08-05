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
├── api/v1/            # HTTP routes (health, chat)
├── agent/             # LangGraph graph: state · prompts · nodes · graph · tools/
├── core/
│   ├── config/       # per-domain settings (app, database, llm, embeddings…)
│   ├── env/          # .env resolution + caching
│   └── llm/          # multi-provider LLM adapters (Adapter + Registry)
├── db/                # async session · models · pgvector store
└── schemas/           # Pydantic DTOs (API input/output)
```

### Role of each layer

| Layer      | Responsibility                                                    |
|------------|------------------------------------------------------------------|
| `api`      | HTTP exposure, validation via `schemas`, no business logic.      |
| `agent`    | Agent logic: LangGraph graph, prompts, tools.                    |
| `core`     | Cross-cutting foundations: configuration, env loading, LLM.      |
| `db`       | Data access: async SQLAlchemy session, models, vector store.     |
| `schemas`  | API contracts (Pydantic), decoupled from database models.        |

## The agent (LangGraph)

The agent is a **state graph**, not a plain LLM call. This makes it extensible
(memory, human-in-the-loop, thread persistence).

```
        ┌─────────┐   tools_condition   ┌─────────┐
START ─▶ │  agent  │ ──────────────────▶ │  tools  │
        └─────────┘ ◀────────────────── └─────────┘
             │
             ▼
            END
```

- **`agent`**: the LLM (with its bound tools) answers, or decides to call a tool.
- **`tools`**: runs the requested tool (e.g. knowledge base search).
- **`tools_condition`**: ReAct loop — while the LLM requests a tool, go through
  `tools` again; otherwise finish.

Files: [`agent/state.py`](../../backend/src/architecto/agent/state.py),
[`agent/nodes.py`](../../backend/src/architecto/agent/nodes.py),
[`agent/graph.py`](../../backend/src/architecto/agent/graph.py).

## RAG (knowledge base)

Architecture documents (patterns, ADRs, best practices) are indexed in **pgvector**
through `langchain-postgres`. The agent reaches them via a `search_knowledge_base`
tool it calls when a question relates to documented decisions.

## Chat request flow

```
POST /api/v1/chat
   → schemas (ChatRequest)
   → run_agent(message, thread_id)      # agent/graph.py
       → agent_node: LLM + tools
       → [optional] tools_node: RAG
   → ChatResponse
```

## Frontend

React + Vite, minimal chat. The dev server proxies `/api` to the backend
(`http://localhost:8000`) — see `frontend/vite.config.js`.

## Key decisions

- **LangGraph graph** over `AgentExecutor` → extensibility.
- **LLM adapter** → provider swappable by config, see [LLM providers](llm-providers.md).
- **Per-domain configuration** → namespaced sections, see [Configuration](configuration.md).
