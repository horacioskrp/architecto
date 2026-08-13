# Design — Analyse de dépendances

> 🇬🇧 [English version](../../en/design/github-analyzer.md) · Feuille de route : [roadmap](../roadmap.md)

Note de conception de `feature/github-analyzer`. Objectif : une **vraie analyse
statique** des dépendances d'un projet — **pas** une lecture LLM du repo. Les findings
sont **calculés** (donc fiables et testables), pas des opinions du modèle.

## Décisions

- **Langage** : Python seul, via le module `ast` (fiable, sans dépendance lourde).
- **Source** : chemin **local** *ou* **URL GitHub** (clone superficiel).
- **Analyse** : **cycles d'imports** + **violations de règles de couches**.

## Principe

L'outil `analyze_dependencies` **n'appelle pas de LLM**. Il parse le code, construit le
**graphe de dépendances intra-projet**, et détecte des faits objectifs. C'est le
grounding qui manquait à la vision initiale (« votre couche Domain dépend de
Infrastructure » = analyse réelle, pas un prompt).

## Modèle

- Module identifié par son **chemin pointé** relatif au package racine
  (ex. `architecto.core.config`).
- Import **intra-projet** = import dont le module cible commence par le package racine.
- **Couche** = 1ᵉʳ segment sous la racine (`architecto.core.X` → couche `core`).

## Règles de couches (défaut, configurables)

Direction de dépendance **autorisée** :

```
core     → (aucune couche interne)   # fondations
features → core
agent    → features, core
api      → agent, features, core
```

Violation = ex. `core` important `features`, ou une feature important `api`.

## Arborescence

```
features/analysis/
├── source.py     # resolve_source : chemin local, ou clone GitHub (--depth 1) dans un tmp
├── parser.py     # build_graph(root) -> {module: set(deps intra-projet)}  (ast)
├── cycles.py     # find_cycles(graph)  (composantes fortement connexes)
├── layers.py     # DEFAULT_LAYER_RULES + find_layer_violations(graph, rules)
└── tools.py      # analyze_dependencies(source) -> rapport factuel
```

## Sortie

Rapport Markdown factuel : nombre de modules, **cycles** détectés, **violations de
couches** détectées (avec les arêtes fautives), et un statut (« aucun problème
détecté » le cas échéant).

## Tests (déterministes, sans réseau)

- `parser` : mini-package synthétique → graphe attendu.
- `cycles` : package avec cycle → cycle détecté ; sans cycle → vide.
- `layers` : violation `core → features` détectée ; direction valide → aucune.
- `source` : chemin local résolu ; le clone GitHub est mocké/ignoré en test.

## Points d'attention

- **Clone** : nécessite `git` + réseau, **dépôts publics** seulement au départ ; dossier
  temporaire nettoyé après analyse.
- L'analyse `ast` est **statique** : imports dynamiques/conditionnels non couverts.
- Les ré-exports dans les `__init__.py` créent des arêtes réelles (attendu).

## Étapes d'implémentation (petits pushes)

1. ✅ Note de design (ce document)
2. ✅ `parser` (ast → graphe) + test
3. ✅ `cycles` + test
4. ✅ `layers` (règles) + test
5. ✅ `source` (chemin local + clone GitHub) + test
6. ✅ Outil `analyze_dependencies` (rapport) + agent + roadmap
7. 🟦 PR vers `develop`
