from architecto.features.knowledge.ingestion.chunking import chunk_id
from architecto.features.knowledge.ingestion.ingestor import Ingestor, SourceRecord
from architecto.features.knowledge.ingestion.loaders import load_bytes


class FakeStore:
    def __init__(self) -> None:
        self.records: dict[str, SourceRecord] = {}
        self.cleared = False

    def get(self, source):
        return self.records.get(source)

    def save(self, source, title, content_hash, chunk_count) -> None:
        self.records[source] = SourceRecord(source, content_hash, chunk_count)

    def clear(self) -> None:
        self.records.clear()
        self.cleared = True


class FakeIndex:
    def __init__(self) -> None:
        self.added_ids: list[str] = []
        self.deleted_ids: list[str] = []
        self.cleared = False

    def add(self, chunks) -> None:
        self.added_ids.extend(c.id for c in chunks)

    def delete(self, ids) -> None:
        self.deleted_ids.extend(ids)

    def clear(self) -> None:
        self.cleared = True


# --- loaders.load_bytes -------------------------------------------------------


def test_load_bytes_markdown_extrait_le_titre():
    doc = load_bytes("guide.md", b"# Mon Guide\n\nDu contenu.")
    assert doc is not None
    assert doc.source == "guide.md"  # nom d'origine, pas un chemin temporaire
    assert doc.title == "Mon Guide"
    assert "Du contenu." in doc.text


def test_load_bytes_txt_titre_par_defaut_le_nom():
    doc = load_bytes("notes.txt", b"texte simple")
    assert doc is not None
    assert doc.title == "notes"


def test_load_bytes_extension_non_supportee():
    assert load_bytes("image.png", b"\x89PNG") is None


def test_load_bytes_contenu_vide():
    assert load_bytes("vide.md", b"   \n  ") is None


# --- Ingestor.ingest_documents ------------------------------------------------


def _long(text: str) -> bytes:
    return text.encode("utf-8")


def test_ingest_documents_nouvelle_source():
    store, index = FakeStore(), FakeIndex()
    ingestor = Ingestor(store, index, chunk_size=50, chunk_overlap=5)
    doc = load_bytes("a.md", _long("# A\n\n" + "phrase. " * 40))

    summary = ingestor.ingest_documents([doc])

    assert summary.processed == 1
    assert summary.chunks > 1
    assert len(index.added_ids) == summary.chunks
    assert "a.md" in store.records


def test_ingest_documents_reingestion_inchangee_ignoree():
    store, index = FakeStore(), FakeIndex()
    ingestor = Ingestor(store, index, chunk_size=50, chunk_overlap=5)
    doc = load_bytes("a.md", _long("# A\n\n" + "phrase. " * 40))

    ingestor.ingest_documents([doc])
    added = list(index.added_ids)
    summary2 = ingestor.ingest_documents([load_bytes("a.md", _long("# A\n\n" + "phrase. " * 40))])

    assert summary2.skipped_unchanged == 1
    assert summary2.processed == 0
    assert index.added_ids == added


def test_ingest_documents_source_modifiee_remplace_les_chunks():
    store, index = FakeStore(), FakeIndex()
    ingestor = Ingestor(store, index, chunk_size=50, chunk_overlap=5)

    ingestor.ingest_documents([load_bytes("a.md", _long("# A\n\n" + "phrase. " * 40))])
    old_count = store.records["a.md"].chunk_count

    ingestor.ingest_documents([load_bytes("a.md", _long("# A\n\ncourt"))])

    assert index.deleted_ids == [chunk_id("a.md", i) for i in range(old_count)]
    assert store.records["a.md"].chunk_count == 1


def test_ingest_documents_none_compte_comme_vide():
    store, index = FakeStore(), FakeIndex()
    ingestor = Ingestor(store, index, chunk_size=50, chunk_overlap=5)

    summary = ingestor.ingest_documents([None])

    assert summary.skipped_empty == 1
    assert summary.processed == 0
