from architecto.features.diagrams import tools
from architecto.features.diagrams.tools import (
    generate_diagram,
    resolve_type,
    strip_code_fences,
    wrap_mermaid,
)


def test_resolve_type_connu_et_repli():
    assert resolve_type("sequence") == "sequenceDiagram"
    assert resolve_type("CLASS") == "classDiagram"  # insensible à la casse
    assert resolve_type("inconnu") == "classDiagram"  # repli


def test_strip_code_fences():
    assert strip_code_fences("```mermaid\nclassDiagram\n  A\n```") == "classDiagram\n  A"
    assert strip_code_fences("```\nflowchart TD\n```") == "flowchart TD"
    assert strip_code_fences("classDiagram\n  A") == "classDiagram\n  A"  # sans fence


def test_wrap_mermaid():
    assert wrap_mermaid("classDiagram") == "```mermaid\nclassDiagram\n```"


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


def test_generate_diagram_normalise_la_sortie(monkeypatch):
    # le LLM renvoie du Mermaid entouré de fences parasites
    fake = _FakeLLM("```mermaid\nclassDiagram\n  Patient --> Consultation\n```")
    monkeypatch.setattr(tools, "get_chat_model", lambda: fake)

    out = generate_diagram.invoke({"description": "Patient et consultation", "diagram_type": "class"})

    assert out.startswith("```mermaid\n")
    assert out.endswith("\n```")
    assert "classDiagram" in out
    assert "Patient --> Consultation" in out
    # une seule paire de fences (pas de double encadrement)
    assert out.count("```") == 2


def test_generate_diagram_passe_le_bon_type(monkeypatch):
    fake = _FakeLLM("sequenceDiagram\n  A->>B: ping")
    monkeypatch.setattr(tools, "get_chat_model", lambda: fake)

    generate_diagram.invoke({"description": "ping pong", "diagram_type": "sequence"})

    system_msg = fake.last_messages[0].content
    assert "sequenceDiagram" in system_msg
