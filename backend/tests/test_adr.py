from architecto.features.adr.template import normalize_status, render_adr
from architecto.features.adr.tools import generate_adr


def test_render_adr_contient_les_sections():
    out = render_adr(
        title="Choix de la base de données",
        context="Besoin de recherche vectorielle.",
        decision="PostgreSQL + pgvector.",
        consequences="Une seule base à opérer.",
        alternatives="Pinecone, Weaviate.",
        status="Accepted",
        adr_date="2026-01-15",
    )
    assert out.startswith("# ADR : Choix de la base de données")
    assert "- **Statut** : Accepted" in out
    assert "- **Date** : 2026-01-15" in out
    for section in ["## Contexte", "## Décision", "## Conséquences", "## Alternatives considérées"]:
        assert section in out
    assert "PostgreSQL + pgvector." in out
    assert "Pinecone, Weaviate." in out


def test_alternatives_vides_donnent_un_tiret():
    out = render_adr(
        title="T",
        context="c",
        decision="d",
        consequences="cq",
        adr_date="2026-01-01",
    )
    assert "## Alternatives considérées\n\n—" in out


def test_normalize_status():
    assert normalize_status("Accepted") == "Accepted"
    assert normalize_status("n'importe quoi") == "Proposed"


def test_generate_adr_normalise_le_statut():
    out = generate_adr.invoke(
        {
            "title": "T",
            "context": "c",
            "decision": "d",
            "consequences": "cq",
            "status": "invalide",
        }
    )
    assert "- **Statut** : Proposed" in out
    assert out.startswith("# ADR : T")
