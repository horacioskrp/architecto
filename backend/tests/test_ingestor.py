from pathlib import Path

from architecto.features.knowledge.ingestion.chunking import chunk_id
from architecto.features.knowledge.ingestion.ingestor import (
    Ingestor,
    SourceRecord,
)


class FakeStore:
    def __init__(self) -> None:
        self.records: dict[str, SourceRecord] = {}
        self.cleared = False

    def get(self, source: str) -> SourceRecord | None:
        return self.records.get(source)

    def save(self, source: str, title: str, content_hash: str, chunk_count: int) -> None:
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


def _ingestor(store: FakeStore, index: FakeIndex) -> Ingestor:
    # petits chunks pour forcer plusieurs fragments
    return Ingestor(store, index, chunk_size=50, chunk_overlap=5)


def test_nouvelle_source_est_ingeree(tmp_path: Path):
    (tmp_path / "a.md").write_text("# A\n\n" + "phrase. " * 40, encoding="utf-8")
    store, index = FakeStore(), FakeIndex()

    summary = _ingestor(store, index).ingest_path(tmp_path)

    assert summary.processed == 1
    assert summary.chunks > 1
    assert len(index.added_ids) == summary.chunks
    assert index.deleted_ids == []
    src = str(tmp_path / "a.md")
    assert src in store.records
    assert store.records[src].chunk_count == summary.chunks


def test_reingestion_inchangee_est_ignoree(tmp_path: Path):
    (tmp_path / "a.md").write_text("# A\n\n" + "phrase. " * 40, encoding="utf-8")
    store, index = FakeStore(), FakeIndex()

    _ingestor(store, index).ingest_path(tmp_path)
    added_after_first = list(index.added_ids)

    summary2 = _ingestor(store, index).ingest_path(tmp_path)

    assert summary2.skipped_unchanged == 1
    assert summary2.processed == 0
    assert index.added_ids == added_after_first  # aucun ajout supplémentaire
    assert index.deleted_ids == []  # rien à supprimer


def test_source_modifiee_supprime_puis_reinsere(tmp_path: Path):
    f = tmp_path / "a.md"
    f.write_text("# A\n\n" + "phrase. " * 40, encoding="utf-8")
    store, index = FakeStore(), FakeIndex()

    first = _ingestor(store, index).ingest_path(tmp_path)
    old_count = store.records[str(f)].chunk_count

    # contenu plus court -> hash différent, moins de chunks
    f.write_text("# A\n\ncourt", encoding="utf-8")
    summary2 = _ingestor(store, index).ingest_path(tmp_path)

    assert summary2.processed == 1
    # les anciens ids (range(old_count)) ont été supprimés
    assert index.deleted_ids == [chunk_id(str(f), i) for i in range(old_count)]
    assert store.records[str(f)].chunk_count == 1
    assert first.chunks > 1


def test_reset_purge_index_et_store(tmp_path: Path):
    (tmp_path / "a.md").write_text("# A\n\ncontenu", encoding="utf-8")
    store, index = FakeStore(), FakeIndex()

    _ingestor(store, index).ingest_path(tmp_path, reset=True)

    assert index.cleared is True
    assert store.cleared is True


def test_fichier_vide_est_compte_comme_ignore(tmp_path: Path):
    (tmp_path / "vide.md").write_text("   ", encoding="utf-8")
    store, index = FakeStore(), FakeIndex()

    summary = _ingestor(store, index).ingest_path(tmp_path)

    assert summary.skipped_empty == 1
    assert summary.processed == 0
    assert index.added_ids == []
