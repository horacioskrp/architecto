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
├── api/v1/            # agrégateur : inclut les routers des features
├── agent/             # orchestration LangGraph : state · prompts · nodes · graph · tools
├── core/              # fondations transverses (aucun métier)
│   ├── config/       # settings par domaine (app, database, llm, embeddings…)
│   ├── env/          # résolution + cache du fichier .env
│   ├── db/           # infra connexion : base (DeclarativeBase) + session async
│   └── llm/          # adaptateurs LLM multi-provider (Adapter + Registry)
└── features/          # vertical slices (métier regroupé par feature)
    ├── chat/         # router + schemas
    ├── knowledge/    # models · vectorstore pgvector · tool de recherche (RAG)
    └── health/       # router
```

### Deux axes d'organisation

- **`core/`** — fondations **transverses**, sans métier : configuration, chargement
  de l'environnement, connexion base de données, adaptateurs LLM.
- **`features/`** — le métier en **tranches verticales** : chaque feature possède
  son router, ses schémas, ses modèles et ses outils.
- **`agent/`** — le moteur d'orchestration LangGraph ; il agrège les outils que les
  features exposent (ex. la recherche de la feature `knowledge`).

| Couche       | Responsabilité                                                       |
|--------------|---------------------------------------------------------------------|
| `api`        | Agrège et versionne les routers des features (aucun métier).        |
| `agent`      | Orchestration : graphe LangGraph, prompts, registre d'outils.       |
| `core`       | Fondations transverses : config, env, connexion DB, LLM.            |
| `features/*` | Une tranche verticale par domaine (router · schemas · models · tools).|

## L'agent (LangGraph)

L'agent est un **graphe d'états** plutôt qu'un simple appel LLM. Cela le rend
extensible (mémoire, human-in-the-loop, persistance des threads).

```
                 needs_clarification ?
                 ┌──────────────┐
START ─▶ triage ─┤              ├─▶ clarify ─▶ END
                 └──────┬───────┘
                        │ non
                        ▼
                   ┌─────────┐  tools_condition  ┌─────────┐
                   │  agent  │ ────────────────▶ │  tools  │
                   └─────────┘ ◀──────────────── └─────────┘
                        │
                        ▼
                       END
```

- **`triage`** : décide (sortie structurée) si des informations essentielles manquent.
- **`clarify`** : si oui, pose des questions ciblées et termine le tour (pas de réponse
  hâtive) — c'est le comportement « copilote ».
- **`agent`** : sinon, le LLM (avec ses outils liés) répond ou décide d'appeler un outil.
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

## Frontend (app desktop Electron)

App **Electron** (client léger) construite avec **electron-vite**. Le renderer est
l'app **React + TypeScript** (Tailwind + shadcn/ui, état **MobX**, police système).

```
frontend/
├── electron.vite.config.ts   # config des 3 process
├── electron-builder.yml      # packaging (win/mac/linux)
└── src/
    ├── main/index.ts         # process principal : fenêtre, cycle de vie, CSS prod
    ├── preload/index.ts      # pont typé (contextBridge -> window.api)
    └── renderer/             # l'app React
        ├── index.html
        └── src/              # main.tsx · router.tsx · api · stores · components · pages
```

**Sécurité** : `contextIsolation: true`, `sandbox: true`, `nodeIntegration: false`,
preload minimal via `contextBridge`, CSP stricte injectée en production.

**Spécificités Electron** :
- routage par **`createHashRouter`** (la prod charge en `file://`, l'history routing
  ne marche pas) ;
- pas de proxy `/api` : le renderer appelle le backend en **URL absolue** configurable
  (`VITE_API_BASE_URL`, défaut `http://localhost:8000`) — cohérent avec le SDK.

L'app est un **client léger** : le backend tourne séparément (local ou conteneur).

## Choix structurants

- **Graphe LangGraph** plutôt qu'`AgentExecutor` → extensibilité.
- **Adaptateur LLM** → provider interchangeable par config, voir
  [Providers LLM](llm-providers.md).
- **Configuration par domaine** → sections namespacées, voir
  [Configuration](configuration.md).
