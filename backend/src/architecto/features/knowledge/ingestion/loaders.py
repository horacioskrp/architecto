from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


@dataclass
class LoadedDocument:
    """Contenu textuel d'une source, prêt à être découpé."""

    source: str
    title: str
    text: str


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def iter_files(root: Path) -> Iterator[Path]:
    """Fichiers supportés d'un fichier unique ou d'un dossier (récursif, trié)."""
    if root.is_file():
        if is_supported(root):
            yield root
        return
    for path in sorted(root.rglob("*")):
        if path.is_file() and is_supported(path):
            yield path


def load_file(path: Path) -> LoadedDocument | None:
    """Charge un fichier -> texte + titre. None si format non supporté ou contenu vide."""
    ext = path.suffix.lower()
    if ext in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = _markdown_title(text) if ext == ".md" else None
    elif ext == ".pdf":
        text = _load_pdf(path)
        title = None
    else:
        return None

    text = text.strip()
    if not text:
        return None
    # source normalisée en chemin absolu -> idempotence robuste (relatif == absolu)
    return LoadedDocument(source=str(path.resolve()), title=title or path.stem, text=text)


def _markdown_title(text: str) -> str | None:
    """Premier titre H1 (`# ...`) rencontré, sinon None."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def _load_pdf(path: Path) -> str:
    """Concatène le texte extractible des pages (les pages vides sont ignorées)."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(part for part in parts if part.strip())
