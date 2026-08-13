from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

_GITHUB = re.compile(r"^(https?://|git@)[^\s]*github\.com", re.IGNORECASE)


def is_github_url(source: str) -> bool:
    s = source.strip()
    return bool(_GITHUB.match(s)) or s.endswith(".git")


@contextmanager
def resolve_source(source: str) -> Iterator[Path]:
    """Fournit un dossier à analyser : chemin local, ou clone GitHub superficiel.

    Le clone (dépôts publics) est fait dans un dossier temporaire, nettoyé à la sortie.
    """
    src = source.strip()
    if is_github_url(src):
        tmp = Path(tempfile.mkdtemp(prefix="architecto-analysis-"))
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", src, str(tmp)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            yield tmp
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        path = Path(src).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"chemin introuvable : {src}")
        yield path
