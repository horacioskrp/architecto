from architecto.core.llm.providers.local import DEFAULT_LOCAL_MODEL, LocalEmbedding
from architecto.core.llm.registry import _EMBED, _EXTRAS, _resolve


def test_provider_local_enregistre():
    assert "local" in _EMBED
    adapter = _resolve(_EMBED, "local", "embeddings")
    assert adapter.provider == "local"


def test_extra_local_mappe_fastembed():
    assert _EXTRAS["local"] == "fastembed"


class _Cfg:
    def __init__(self, model: str):
        self.model = model


def test_choix_du_modele_local(monkeypatch):
    captured: dict[str, str] = {}

    class _Fake:
        def __init__(self, model_name: str):
            captured["model"] = model_name

    # évite tout téléchargement : on remplace l'implémentation fastembed
    import architecto.core.llm.providers.local as mod

    monkeypatch.setattr(mod, "_FastEmbedEmbeddings", _Fake)

    LocalEmbedding().build(_Cfg("text-embedding-3-small"))  # pas un id fastembed -> défaut
    assert captured["model"] == DEFAULT_LOCAL_MODEL

    LocalEmbedding().build(_Cfg("intfloat/multilingual-e5-small"))  # id fastembed -> conservé
    assert captured["model"] == "intfloat/multilingual-e5-small"
