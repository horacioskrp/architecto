from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

# N'accepte que des URL distantes http(s) / ssh « propres ». Refuse tout ce qui
# contient `::` (transports git dangereux : ext::, file::…) ou une espace :
# c'est le vecteur d'exécution de commande via `git clone`.
_REMOTE = re.compile(r"^(https://|git@)[^\s]+$", re.IGNORECASE)


def is_github_url(source: str) -> bool:
    s = source.strip()
    if "::" in s or any(c.isspace() for c in s):
        return False
    return bool(_REMOTE.match(s))


@contextmanager
def resolve_source(source: str) -> Iterator[Path]:
    """Fournit un dossier à analyser : chemin local, ou clone GitHub superficiel.

    Le clone (dépôts publics) est fait dans un dossier temporaire, nettoyé à la sortie.
    """
    src = source.strip()
    if is_github_url(src):
        tmp = Path(tempfile.mkdtemp(prefix="architecto-analysis-"))
        # Défense en profondeur : restreint les transports git (bloque ext::,
        # file::…) et coupe les prompts ; `--` empêche l'URL d'être lue comme une option.
        env = {
            **os.environ,
            "GIT_ALLOW_PROTOCOL": "https:ssh",
            "GIT_TERMINAL_PROMPT": "0",
        }
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--", src, str(tmp)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )
            yield tmp
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        path = Path(src).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"chemin introuvable : {src}")
        yield path
