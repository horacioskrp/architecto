from architecto.features.memory.router import list_decisions, list_projects
from architecto.features.memory.schemas import DecisionsList, ProjectsList


async def test_list_projects_mappe_le_store(monkeypatch):
    from architecto.features.memory import router as mod
    from architecto.features.memory.ports import ProjectSummary

    class _FakeStore:
        def list_projects(self):
            return [ProjectSummary(slug="erp", name="erp", decision_count=3)]

    monkeypatch.setattr(mod, "SqlDecisionStore", _FakeStore)
    out = await list_projects()
    assert isinstance(out, ProjectsList)
    assert out.projects[0].slug == "erp"
    assert out.projects[0].decision_count == 3


async def test_list_decisions_mappe_le_store(monkeypatch):
    from architecto.features.memory import router as mod
    from architecto.features.memory.ports import StoredDecision

    class _FakeStore:
        def list_by_project(self, project):
            assert project == "erp"
            return [StoredDecision("1", "Base", "Accepted", "ctx", "pgvector", "cq")]

    monkeypatch.setattr(mod, "SqlDecisionStore", _FakeStore)
    out = await list_decisions(project="erp")
    assert isinstance(out, DecisionsList)
    assert out.decisions[0].title == "Base"
    assert out.decisions[0].decision == "pgvector"
