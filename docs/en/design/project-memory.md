# Design — Project memory

> 🇫🇷 [Version française](../../fr/design/project-memory.md) · Roadmap: [roadmap](../roadmap.md)

Design note for `feature/project-memory`. Goal: the agent **remembers** a project's
architecture decisions across sessions. Dovetails with `generate_adr` (a stored
decision has the same fields as an ADR).

## Decisions

- **Project identity**: explicit slug argument, **fallback to `thread_id`** if absent.
- **Access**: explicit tools `save_decision` / `recall_decisions` (the agent decides).
- **Retrieval**: **SQL (recency) + semantic (pgvector)** fused via **RRF reranking**
  (Reciprocal Rank Fusion). Interface extensible to a stronger reranker
  (LLM/cross-encoder) later.

## Data model

- `Project`: `slug` (unique), `name`, timestamps.
- `ArchitectureDecision`: `project_id`, `title`, `status`, `context`, `decision`,
  `consequences`, timestamps (same fields as an ADR).

## Architecture (ports / adapters)

Same pattern as ingestion → core testable without a DB.

- `DecisionStore` (SQL, source of truth): `add`, `list_by_project`, `clear`.
- `DecisionIndex` (pgvector, collection `architecto_decisions`): `add(decision)`,
  `search(project, query, k)` → ids ranked by similarity.
- `resolve_project(slug, thread_id)` → slug if given, else thread_id, else `default`.
- `reciprocal_rank_fusion(rankings)` → fuse ranked lists (pure function).

## Tools exposed to the agent

- `save_decision(title, context, decision, consequences, status, project="")`:
  persists (SQL) **and** indexes (vector). `thread_id` obtained via injected `RunnableConfig`.
- `recall_decisions(query="", project="", k=5)`:
  - with `query` → **semantic** + **recency** candidates → **RRF** → top-k;
  - without `query` → recent list (SQL).

## Reranking (RRF)

For each ranked list, `score(id) += 1 / (K + rank)` (K≈60). Sort by descending score.
Combines semantic similarity and recency without an extra model.

## Tests (no database)

- `reciprocal_rank_fusion`: pure fusion (expected order).
- `resolve_project`: slug > thread_id > default.
- `save`/`recall` tools with mocked `DecisionStore` **and** `DecisionIndex`.

## Watch-outs

- `thread_id` injection via `RunnableConfig` in tools.
- Vector indexing of decisions consumes embeddings (key required end-to-end).
- New tables → re-run `scripts/init_db.py` in dev.

## Implementation steps (small pushes)

1. ✅ Design note (this document)
2. ⬜ `Project` + `ArchitectureDecision` models + `init_db`
3. ⬜ RRF reranking + `resolve_project` + tests
4. ⬜ Ports + adapters (SQL + pgvector decisions)
5. ⬜ Tools `save_decision` / `recall_decisions` + tests (mocks)
6. ⬜ Agent wiring + roadmap
7. ⬜ PR to `develop`
