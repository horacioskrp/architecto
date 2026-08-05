# Architecture

> 🇬🇧 [English version](../en/architecture.md)

## Monorepo

```
architecto/
├── backend/     # API FastAPI + agent LangGraph
├── frontend/    # UI React (Vite)
├── docs/        # cette documentation
└── docker-compose.yml   # Postgres + pgvector
```

## Backend

```
backend/src/architecto/
├── main.py            # app FastAPI + CORS + activation LangSmith
├── api/v1/            # routes HTTP (health, chat)
├── agent/             # graphe LangGraph : state · prompts · nodes · graph · tools/
├── core/
│   ├── config/       # settings par domaine (app, database, llm, embeddings…)
│   ├── env/          # résolution + cache du fichier .env
│   └── llm/          # adaptateurs LLM multi-provider (Adapter + Registry)
├── db/                # session async · models · vectorstore pgvector
└── schemas/           # DTO Pydantic (entrée/sortie API)
```

### Rôle de chaque couche

| Couche     | Responsabilité                                                     |
|------------|-------------------------------------------------------------------|
| `api`      | Exposition HTTP, validation via `schemas`, aucun métier.          |
| `agent`    | Logique de l'agent : graphe LangGraph, prompts, outils (tools).   |
| `core`     | Fondations transverses : configuration, chargement env, LLM.      |
| `db`       | Accès données : session SQLAlchemy async, modèles, store vectoriel.|
| `schemas`  | Contrats d'API (Pydantic), découplés des modèles de base.         |

## L'agent (LangGraph)

L'agent est un **graphe d'états** plutôt qu'un simple appel LLM. Cela le rend
extensible (mémoire, human-in-the-loop, persistance des threads).

```
        ┌─────────┐   tools_condition   ┌─────────┐
START ─▶ │  agent  │ ──────────────────▶ │  tools  │
        └─────────┘ ◀────────────────── └─────────┘
             │
             ▼
            END
```

- **`agent`** : le LLM (avec ses outils liés) répond, ou décide d'appeler un outil.
- **`tools`** : exécute l'outil demandé (ex. recherche dans la base de connaissances).
- **`tools_condition`** : boucle ReAct — tant que le LLM demande un outil, on repasse
  par `tools`, sinon on termine.

Fichiers : [`agent/state.py`](../../backend/src/architecto/agent/state.py),
[`agent/nodes.py`](../../backend/src/architecto/agent/nodes.py),
[`agent/graph.py`](../../backend/src/architecto/agent/graph.py).

## RAG (base de connaissances)

Les documents d'architecture (patterns, ADR, best practices) sont indexés dans
**pgvector** via `langchain-postgres`. L'agent y accède par un outil
`search_knowledge_base` qu'il appelle quand une question porte sur des choix
documentés.

## Flux d'une requête de chat

```
POST /api/v1/chat
   → schémas (ChatRequest)
   → run_agent(message, thread_id)      # agent/graph.py
       → agent_node : LLM + tools
       → [éventuel] tools_node : RAG
   → ChatResponse
```

## Frontend

React + Vite, chat minimal. Le serveur de dev proxifie `/api` vers le backend
(`http://localhost:8000`) — voir `frontend/vite.config.js`.

## Choix structurants

- **Graphe LangGraph** plutôt qu'`AgentExecutor` → extensibilité.
- **Adaptateur LLM** → provider interchangeable par config, voir
  [Providers LLM](llm-providers.md).
- **Configuration par domaine** → sections namespacées, voir
  [Configuration](configuration.md).
