from pathlib import Path

import pytest

import architecto.features.analysis.source as source_mod
from architecto.features.analysis.source import is_github_url, resolve_source


def test_is_github_url():
    assert is_github_url("https://github.com/owner/repo")
    assert is_github_url("git@github.com:owner/repo.git")
    assert is_github_url("https://example.com/repo.git")  # https distant -> clone
    assert not is_github_url("/chemin/local")
    assert not is_github_url("C:/Users/x/projet")


def test_is_github_url_rejette_transports_dangereux():
    # Vecteur d'exécution de commande via git clone : doit être refusé.
    assert not is_github_url("ext::sh -c 'touch /tmp/x' #.git")
    assert not is_github_url("ext::sh#.git")
    assert not is_github_url("file:///etc/passwd")
    assert not is_github_url("http://github.com/owner/repo")  # http non-TLS refusé


def test_resolve_local(tmp_path: Path):
    with resolve_source(str(tmp_path)) as path:
        assert path == tmp_path


def test_resolve_local_introuvable():
    with pytest.raises(FileNotFoundError), resolve_source("/chemin/qui/nexiste/pas/xyz"):
        pass


def test_resolve_github_clone_et_nettoyage(monkeypatch):
    recorded: dict[str, list[str]] = {}

    def fake_run(cmd, **_kwargs):
        recorded["cmd"] = cmd

    monkeypatch.setattr(source_mod.subprocess, "run", fake_run)

    seen: Path | None = None
    with resolve_source("https://github.com/owner/repo") as path:
        seen = path
        assert path.exists()  # dossier temporaire créé
        assert "clone" in recorded["cmd"] and "--depth" in recorded["cmd"]

    assert seen is not None and not seen.exists()  # nettoyé à la sortie
