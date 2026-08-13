from architecto.features.security import tools
from architecto.features.security.prompts import OWASP_TOP_10, build_system_prompt
from architecto.features.security.tools import security_checklist


def test_owasp_top_10_complet():
    assert len(OWASP_TOP_10) == 10
    joined = " ".join(OWASP_TOP_10)
    assert "Broken Access Control" in joined
    assert "Injection" in joined
    assert "SSRF" in joined


def test_prompt_ancre_owasp_et_cadre_checklist():
    p = build_system_prompt()
    for code in ("A01:2021", "A03:2021", "A10:2021"):
        assert code in p
    assert "- [ ]" in p  # format checklist
    assert "pas un verdict" in p.lower()


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


def test_security_checklist_renvoie_le_contenu(monkeypatch):
    fake = _FakeLLM("## A01:2021 – Broken Access Control\n- [ ] Vérifier le RBAC\n")
    monkeypatch.setattr(tools, "get_chat_model", lambda: fake)

    out = security_checklist.invoke({"description": "API REST avec JWT"})

    assert "- [ ]" in out
    # les catégories OWASP partent bien dans le prompt système
    assert "A03:2021" in fake.last_messages[0].content
    assert fake.last_messages[1].content == "API REST avec JWT"
