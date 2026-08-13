# Design — Dependency analysis

> 🇫🇷 [Version française](../../fr/design/github-analyzer.md) · Roadmap: [roadmap](../roadmap.md)

Design note for `feature/github-analyzer`. Goal: **real static analysis** of a
project's dependencies — **not** an LLM read of the repo. Findings are **computed**
(reliable and testable), not model opinions.

## Decisions

- **Language**: Python only, via the `ast` module (reliable, no heavy dependency).
- **Source**: **local** path *or* **GitHub URL** (shallow clone).
- **Analysis**: **import cycles** + **layer-rule violations**.

## Principle

The `analyze_dependencies` tool **does not call an LLM**. It parses the code, builds the
**intra-project dependency graph**, and detects objective facts. This is the grounding
the initial vision lacked ("your Domain layer depends on Infrastructure" = real
analysis, not a prompt).

## Model

- A module is identified by its **dotted path** relative to the root package
  (e.g. `architecto.core.config`).
- An **intra-project** import is one whose target module starts with the root package.
- A **layer** is the 1st segment under the root (`architecto.core.X` → layer `core`).

## Layer rules (default, configurable)

**Allowed** dependency direction:

```
core     → (no internal layer)   # foundations
features → core
agent    → features, core
api      → agent, features, core
```

A violation is e.g. `core` importing `features`, or a feature importing `api`.

## Layout

```
features/analysis/
├── source.py     # resolve_source: local path, or GitHub clone (--depth 1) into a tmp
├── parser.py     # build_graph(root) -> {module: set(intra-project deps)}  (ast)
├── cycles.py     # find_cycles(graph)  (strongly connected components)
├── layers.py     # DEFAULT_LAYER_RULES + find_layer_violations(graph, rules)
└── tools.py      # analyze_dependencies(source) -> factual report
```

## Output

Factual Markdown report: module count, detected **cycles**, detected **layer
violations** (with the offending edges), and a status ("no issue detected" when
applicable).

## Tests (deterministic, no network)

- `parser`: synthetic mini-package → expected graph.
- `cycles`: package with a cycle → cycle detected; without → empty.
- `layers`: `core → features` violation detected; valid direction → none.
- `source`: local path resolved; GitHub clone mocked/skipped in tests.

## Watch-outs

- **Clone**: requires `git` + network, **public repos** only at first; temp directory
  cleaned up after analysis.
- `ast` analysis is **static**: dynamic/conditional imports are not covered.
- Re-exports in `__init__.py` create real edges (expected).

## Implementation steps (small pushes)

1. ✅ Design note (this document)
2. ✅ `parser` (ast → graph) + test
3. ✅ `cycles` + test
4. ✅ `layers` (rules) + test
5. ✅ `source` (local path + GitHub clone) + test
6. ✅ `analyze_dependencies` tool (report) + agent + roadmap
7. 🟦 PR to `develop`
