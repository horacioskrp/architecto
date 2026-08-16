# Architecto — Vue d'ensemble

> 🇬🇧 [English version](../en/README.md)

**Architecto** est un agent IA « architecte logiciel ». Il assiste la conception :
clarification des besoins, choix d'architecture, rédaction d'ADR, diagrammes,
découpage en modules et revue de code — en s'appuyant sur une base de connaissances
vectorielle (RAG).

## Stack

| Couche    | Technologies                                              |
|-----------|-----------------------------------------------------------|
| Backend   | FastAPI · uv · Pydantic v2                                |
| Agent     | LangChain · LangGraph · LangSmith (observabilité)         |
| Données   | PostgreSQL · pgvector · SQLAlchemy                        |
| LLM       | Multi-provider (Claude · OpenAI · Gemini · DeepSeek)      |
| Desktop   | Electron · React · TS · Vite · React Router · Tailwind · shadcn/ui · MobX |

## Principes

- **Configuration par l'environnement** — rien de métier n'est écrit en dur ;
  tout est piloté par variables d'environnement. Voir [Configuration](configuration.md).
- **LLM interchangeable** — le provider est sélectionné par config grâce à un
  pattern adaptateur. Voir [Providers LLM](llm-providers.md).
- **Séparation par domaine** — `api`, `agent`, `core`, `db`, `schemas` sont
  découplés et testables isolément. Voir [Architecture](architecture.md).

## Par où commencer

1. [Démarrage](getting-started.md) — lancer la base, le backend et le frontend.
2. [Configuration](configuration.md) — variables d'environnement par section.
3. [Architecture](architecture.md) — organisation du code et flux de l'agent.
4. [Providers LLM](llm-providers.md) — changer de modèle, ajouter un provider.
5. [SDK Python](sdk.md) — client typé pour consommer l'API.
6. [Feuille de route](roadmap.md) — ce qu'on construit et dans quel ordre.

## Statut

Trio backend (Phases 1-3) livré ; client desktop Electron avec streaming,
multi-conversations, ingestion RAG depuis le client et panneau de décisions ;
robustesse frontend (tests, types OpenAPI, ErrorBoundary). Voir la
[feuille de route](roadmap.md). Reste notamment la **CI**. Cette documentation
évolue avec le code.
