from pathlib import Path

from architecto.features.knowledge.ingestion import loaders
from architecto.features.knowledge.ingestion.loaders import (
    LoadedDocument,
    is_supported,
    iter_files,
    load_file,
)


def test_is_supported():
    assert is_supported(Path("a.md"))
    assert is_supported(Path("a.txt"))
    assert is_supported(Path("a.PDF"))  # insensible à la casse
    assert not is_supported(Path("a.docx"))


def test_load_markdown_title_depuis_h1(tmp_path: Path):
    f = tmp_path / "doc.md"
    f.write_text("# Vrai titre\n\nDu contenu.", encoding="utf-8")
    doc = load_file(f)
    assert isinstance(doc, LoadedDocument)
    assert doc.title == "Vrai titre"
    assert doc.source == str(f.resolve())
    assert "Du contenu." in doc.text


def test_load_txt_titre_depuis_nom_de_fichier(tmp_path: Path):
    f = tmp_path / "notes.txt"
    f.write_text("juste du texte", encoding="utf-8")
    doc = load_file(f)
    assert doc is not None
    assert doc.title == "notes"


def test_load_markdown_sans_h1_utilise_le_nom(tmp_path: Path):
    f = tmp_path / "readme.md"
    f.write_text("pas de titre h1 ici", encoding="utf-8")
    doc = load_file(f)
    assert doc is not None
    assert doc.title == "readme"


def test_fichier_vide_renvoie_none(tmp_path: Path):
    f = tmp_path / "vide.md"
    f.write_text("   \n  ", encoding="utf-8")
    assert load_file(f) is None


def test_format_non_supporte_renvoie_none(tmp_path: Path):
    f = tmp_path / "a.docx"
    f.write_text("x", encoding="utf-8")
    assert load_file(f) is None


def test_load_pdf_concatene_les_pages(tmp_path: Path, monkeypatch):
    class _Page:
        def __init__(self, text: str):
            self._text = text

        def extract_text(self):
            return self._text

    class _Reader:
        def __init__(self, _path):
            self.pages = [_Page("Page 1"), _Page("   "), _Page("Page 2")]

    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", _Reader)

    f = tmp_path / "spec.pdf"
    f.write_bytes(b"%PDF-1.4 fake")
    doc = load_file(f)
    assert doc is not None
    assert "Page 1" in doc.text
    assert "Page 2" in doc.text
    assert doc.title == "spec"


def test_iter_files_dossier_recursif(tmp_path: Path):
    (tmp_path / "a.md").write_text("# a", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "ignore.docx").write_text("x", encoding="utf-8")

    found = sorted(p.name for p in iter_files(tmp_path))
    assert found == ["a.md", "b.txt"]


def test_iter_files_fichier_unique(tmp_path: Path):
    f = tmp_path / "only.md"
    f.write_text("# x", encoding="utf-8")
    assert [p.name for p in iter_files(f)] == ["only.md"]


def test_loaders_module_exporte_les_symboles():
    # garde-fou : l'API publique du module reste stable
    assert hasattr(loaders, "load_file")
    assert hasattr(loaders, "iter_files")
