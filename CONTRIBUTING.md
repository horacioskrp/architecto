# Contribuer — workflow Git (Gitflow)

Le dépôt suit **Gitflow**.

## Branches

| Branche | Rôle | Reçoit |
|---------|------|--------|
| `main` | Production (releases) | uniquement des merges de `release/*` ou `hotfix/*` |
| `develop` | Intégration continue | les merges de `feature/*` |
| `feature/*` | Développement d'une fonctionnalité | part de `develop`, retourne dans `develop` |
| `release/*` | Préparation d'une release | part de `develop`, retourne dans `main` **et** `develop` |
| `hotfix/*` | Correctif urgent en prod | part de `main`, retourne dans `main` **et** `develop` |

## Nommage

- `feature/<sujet-kebab>` — ex. `feature/streaming-sse`, `feature/auth-jwt`
- `release/<version>` — ex. `release/0.2.0`
- `hotfix/<sujet>` — ex. `hotfix/cors-prod`

## Créer une fonctionnalité

```bash
git checkout develop
git pull --ff-only origin develop
git checkout -b feature/mon-sujet
# … commits …
git push -u origin feature/mon-sujet
```

Puis ouvrir une **Pull Request vers `develop`**.

## Messages de commit

Préfixe explicite : `Feat:`, `Fix:`, `Refactor:`, `Docs:`, `Build:`, `Test:`, `Chore:`.
Impératif, concis, en français.

## Release

```bash
git checkout -b release/0.2.0 develop
# bump de version, correctifs finaux
git checkout main && git merge --no-ff release/0.2.0 && git tag v0.2.0
git checkout develop && git merge --no-ff release/0.2.0
```

`main` est toujours déployable ; `develop` porte le prochain incrément.
