from architecto.features.architecture import tools
from architecto.features.architecture.prompts import build_system_prompt
from architecto.features.architecture.tools import generate_architecture


def test_prompt_impose_le_raisonnement_compromis():
    p = build_system_prompt()
    assert "## Style retenu" in p
    assert "## Découpage en modules" in p
    assert "## Compromis" in p
    assert "Frontière" in p and "Couplages" in p


def test_prompt_sans_style_pas_de_contrainte():
    assert "Contrainte" not in build_system_prompt()
    assert "Contrainte" not in build_system_prompt("   ")


def test_prompt_avec_style_ajoute_la_contrainte():
    p = build_system_prompt("microservices")
    assert "microservices" in p
    assert "Contrainte" in p


class _FakeMsg:
    def __init__(self, content: str):
        self.content = content


class _FakeLLM:
    def __init__(self, content: str):
        self._content = content
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return _FakeMsg(self._content)


def test_generate_architecture_renvoie_le_contenu(monkeypatch):
    fake = _FakeLLM("## Style retenu\nMonolithe modulaire\n")
    monkeypatch.setattr(tools, "get_chat_model", lambda: fake)

    out = generate_architecture.invoke({"description": "ERP hospitalier", "style": "microservices"})

    assert out.startswith("## Style retenu")
    # la description part bien en message humain, le style est dans le système
    assert fake.last_messages[1].content == "ERP hospitalier"
    assert "microservices" in fake.last_messages[0].content
