from architecto.features.database import tools
from architecto.features.database.sql import extract_sql, validate_sql
from architecto.features.database.tools import design_database

VALID_DDL = (
    "CREATE TABLE patients (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL);\n"
    "CREATE TABLE consultations (\n"
    "  id SERIAL PRIMARY KEY,\n"
    "  patient_id INTEGER NOT NULL REFERENCES patients(id),\n"
    "  date TIMESTAMP NOT NULL\n"
    ");\n"
    "CREATE INDEX idx_consultations_patient ON consultations(patient_id);"
)


def test_extract_sql_depuis_bloc():
    text = f"## Modèle\nblabla\n\n## SQL\n```sql\n{VALID_DDL}\n```"
    assert extract_sql(text).startswith("CREATE TABLE patients")
    assert "CREATE INDEX" in extract_sql(text)


def test_extract_sql_repli_sans_bloc():
    assert extract_sql("CREATE TABLE t (id INT);") == "CREATE TABLE t (id INT);"


def test_validate_sql_valide():
    ok, error = validate_sql(VALID_DDL)
    assert ok is True
    assert error == ""


def test_validate_sql_invalide():
    ok, error = validate_sql("CREATE TABLE (( bad sql ][")
    assert ok is False
    assert error


def test_validate_sql_vide():
    ok, _error = validate_sql("   ")
    assert ok is False


class _FakeMsg:
    def __init__(self, content: str):
        self.content = content


class _FakeLLM:
    def __init__(self, content: str):
        self._content = content

    def invoke(self, messages):
        return _FakeMsg(self._content)


def test_design_database_signale_sql_valide(monkeypatch):
    monkeypatch.setattr(tools, "get_chat_model", lambda: _FakeLLM(f"## SQL\n```sql\n{VALID_DDL}\n```"))
    out = design_database.invoke({"description": "patients et consultations"})
    assert "✅" in out
    assert "syntaxiquement valide" in out


def test_design_database_signale_sql_invalide(monkeypatch):
    monkeypatch.setattr(tools, "get_chat_model", lambda: _FakeLLM("```sql\nCREATE TABLE (( nope\n```"))
    out = design_database.invoke({"description": "n'importe quoi"})
    assert "⚠️" in out
    assert "Erreur de syntaxe" in out
