from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

# Graphe : module pointé -> ensemble de modules internes dont il dépend.
DependencyGraph = dict[str, set[str]]


def _is_package(directory: Path) -> bool:
    return (directory / "__init__.py").is_file()


def _find_top_packages(root: Path) -> dict[Path, str]:
    """Packages dont le parent n'est pas un package -> racine d'une hiérarchie.

    Ex. `.../architecto/__init__.py` avec parent `src` non-package -> {dir: "architecto"}.
    """
    tops: dict[Path, str] = {}
    for init in root.rglob("__init__.py"):
        pkg = init.parent
        if not _is_package(pkg.parent):
            tops[pkg] = pkg.name
    return tops


def _module_of(py: Path, tops: dict[Path, str]) -> tuple[str, str] | None:
    """(module pointé, package conteneur) d'un fichier, sinon None (hors packages)."""
    for top_dir, top_name in tops.items():
        try:
            rel = py.relative_to(top_dir)
        except ValueError:
            continue
        parts = list(rel.with_suffix("").parts)
        is_pkg = py.name == "__init__.py"
        if is_pkg:
            parts = parts[:-1]  # retire "__init__"
        module = ".".join([top_name, *parts]) if parts else top_name
        package = module if is_pkg else module.rsplit(".", 1)[0]
        return module, package
    return None


def _resolve_relative(package: str, level: int) -> str:
    """Résout le package de base d'un import relatif (`from . import`, `from ..x`)."""
    parts = package.split(".")
    up = level - 1
    if up > len(parts):
        return ""
    return ".".join(parts[: len(parts) - up])


def _import_targets(node: ast.AST, package: str) -> Iterator[str]:
    if isinstance(node, ast.Import):
        for alias in node.names:  # import a.b.c [as x]
            yield alias.name
    elif isinstance(node, ast.ImportFrom):
        if node.level and node.level > 0:  # import relatif
            base = _resolve_relative(package, node.level)
            if not base:
                return
            if node.module:  # from .mod import X -> base.mod
                yield f"{base}.{node.module}"
            else:  # from . import sous_module -> base.sous_module
                for alias in node.names:
                    yield f"{base}.{alias.name}"
        elif node.module:  # from a.b import X -> a.b
            yield node.module


def build_graph(root: Path) -> DependencyGraph:
    """Construit le graphe des dépendances **intra-projet** (deux passes)."""
    tops = _find_top_packages(root)
    top_names = set(tops.values())

    # 1ʳᵉ passe : modules du projet
    files: dict[Path, tuple[str, str]] = {}
    modules: set[str] = set()
    for py in sorted(root.rglob("*.py")):
        info = _module_of(py, tops)
        if info is not None:
            files[py] = info
            modules.add(info[0])

    # 2ᵉ passe : arêtes vers des modules réellement présents
    graph: DependencyGraph = {}
    for py, (module, package) in files.items():
        graph.setdefault(module, set())
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            for target in _import_targets(node, package):
                if (
                    target.split(".", 1)[0] in top_names
                    and target != module
                    and target in modules
                ):
                    graph[module].add(target)
    return graph
