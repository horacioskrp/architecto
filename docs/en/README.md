# Architecto — Overview

> 🇫🇷 [Version française](../fr/README.md)

**Architecto** is a "software architect" AI agent. It assists design work:
clarifying requirements, choosing architectures, writing ADRs, diagrams, module
breakdowns and code review — backed by a vector knowledge base (RAG).

## Stack

| Layer     | Technologies                                              |
|-----------|-----------------------------------------------------------|
| Backend   | FastAPI · uv · Pydantic v2                                |
| Agent     | LangChain · LangGraph · LangSmith (observability)         |
| Data      | PostgreSQL · pgvector · SQLAlchemy                        |
| LLM       | Multi-provider (Claude · OpenAI · Gemini · DeepSeek)      |
| Frontend  | React (Vite)                                              |

## Principles

- **Environment-driven configuration** — nothing business-related is hardcoded;
  everything is driven by environment variables. See [Configuration](configuration.md).
- **Swappable LLM** — the provider is selected by config through an adapter
  pattern. See [LLM providers](llm-providers.md).
- **Domain separation** — `api`, `agent`, `core`, `db`, `schemas` are decoupled
  and independently testable. See [Architecture](architecture.md).

## Where to start

1. [Getting started](getting-started.md) — run the database, backend and frontend.
2. [Configuration](configuration.md) — environment variables by section.
3. [Architecture](architecture.md) — code layout and agent flow.
4. [LLM providers](llm-providers.md) — switch models, add a provider.

## Status

Project under initial setup. This documentation evolves alongside the code.
