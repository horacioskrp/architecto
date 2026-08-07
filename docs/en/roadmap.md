# Roadmap

> 🇫🇷 [Version française](../fr/roadmap.md)

Reference document: what we build, in which order, and how we track progress.
Updated on every PR merged into `develop`.

## Guiding principles

- **Reliable before broad**: depth on a few verifiable capabilities rather than a
  shallow sweep of many tools (avoid *demoware*).
- **Editable artifacts, not an oracle**: the agent *drafts* reviewable outputs
  (diagrams, ADRs, cited answers) that a human validates.
- **Grounding**: visibly separate the **verified fact** (cited) from the **generated
  suggestion**.
- **Copilot, not chatbot**: value comes from reasoning (clarification, trade-offs),
  not an authoritative answer.

## Working method (Gitflow)

- One capability = one `feature/*` branch = one PR to `develop`.
- Small, **tested** units (at least one test per feature).
- `develop` stays always-integrable; `main` only receives releases.
- See [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## Status

Legend: ⬜ todo · 🟦 in progress · ✅ done

| Phase | Feature | Branch | Status |
|-------|---------|--------|--------|
| 0 | CI + PR template | `feature/ci` | ⬜ |
| 1 | Clarification loop | `feature/clarify-loop` | ✅ |
| 1 | RAG ingestion ([design](design/rag-ingestion.md)) | `feature/rag-ingestion` | ✅ |
| 1 | Cited answers | `feature/rag-citations` | ✅ |
| 1 | UML/Mermaid tool | `feature/uml-tool` | ✅ |
| 1 | ADR output | `feature/adr-output` | ✅ |
| 2 | Project memory ([design](design/project-memory.md)) | `feature/project-memory` | ✅ |
| 2 | Architecture generator (trade-offs) | `feature/architecture-generator` | ✅ |
| 2 | Database designer | `feature/database-designer` | ⬜ |
| 3 | GitHub repository analyzer | `feature/github-analyzer` | ⬜ |
| 3 | Security checklist (OWASP) | `feature/security-checklist` | ⬜ |

---

## Phase 0 — Foundation (optional, recommended)

### `feature/ci`
- **Goal**: validate every PR to `develop` automatically.
- **Scope**: GitHub Actions — backend (`ruff` + `pytest` + `py_compile`), frontend
  (`tsc --noEmit` + `vite build`), sdk (`pytest`). A `.github/pull_request_template.md`.
- **Acceptance**: the workflow runs on a PR and passes.

## Phase 1 — The credible trio (reliable & demonstrable)

### `feature/clarify-loop`
- **Goal**: the agent asks questions when essential info is missing, instead of
  answering immediately.
- **Scope**: `clarify` node + conditional edge in the LangGraph graph; enriched state
  (`needs_clarification`, `questions`); simple decision policy.
- **Deliverables**: updated graph + routing test.
- **Acceptance**: vague prompt → answer with questions; complete prompt → no questions.

### `feature/rag-ingestion`
- **Goal**: populate pgvector (the store is empty today).
- **Scope**: ingestion (chunking + embeddings + upsert) from Markdown files via a
  `scripts/ingest.py` script (and/or an endpoint).
- **Deliverables**: ingestion script + test (mocked embeddings).
- **Acceptance**: after ingestion, `search_knowledge_base` returns relevant excerpts.

### `feature/rag-citations`
- **Goal**: every grounded answer cites its sources.
- **Scope**: propagate chunk metadata (title/source); citation format in the answer.
- **Deliverables**: tool returning content + source, citing prompt, test.
- **Acceptance**: a RAG answer lists the sources used.

### `feature/uml-tool`
- **Goal**: generate Mermaid diagrams from a description.
- **Scope**: `@tool generate_diagram` (class / sequence / component) returning valid
  Mermaid.
- **Deliverables**: tool + test (the `mermaid` block has the expected shape).
- **Acceptance**: description → coherent ```mermaid``` block.

### `feature/adr-output`
- **Goal**: produce a structured ADR.
- **Scope**: ADR output/tool (Context · Decision · Consequences · Alternatives) in
  Markdown.
- **Deliverables**: tool + structure test.
- **Acceptance**: ADR output with the expected sections.

## Phase 2 — Extension (semi-verifiable, must be grounded)

- **`feature/project-memory`** — long-term memory: `projects` + `decisions` model
  (Postgres), retrieved across sessions.
- **`feature/architecture-generator`** — **trade-off-oriented** module breakdown
  (justifies boundaries and couplings), not a list of modules.
- **`feature/database-designer`** — entities, relations, keys, indexes, SQL script;
  **syntactic** validation of the generated SQL.

## Phase 3 — Must be grounded (high risk otherwise)

- **`feature/github-analyzer`** — **real** dependency analysis (import graph, layer
  rules), not an LLM read of the repo.
- **`feature/security-checklist`** — **OWASP**-grounded checklist (a checklist, not a
  verdict).

## Advisory — with explicit caveats (never authoritative output)

- **Cost Estimator** and **Cloud Advisor**: available in conversation, always with
  caveats; not reliably groundable → no "official" output.

## Deferred

- **Multi-agent** (Architect / Database / Security / DevOps / Review / Docs): only if a
  single well-equipped agent no longer suffices. Premature today.

## Out of scope (anti-goals)

- No ungrounded authoritative verdict.
- No multi-agent "for the demo".
- No breadth at the expense of the Phase 1 trio's depth.
