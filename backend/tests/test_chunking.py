from architecto.features.knowledge.ingestion.chunking import (
    Chunk,
    chunk_document,
    chunk_id,
    content_hash,
    source_key,
)
from architecto.features.knowledge.ingestion.loaders import LoadedDocument


def _doc(text: str, source: str = "/docs/a.md", title: str = "A") -> LoadedDocument:
    return LoadedDocument(source=source, title=title, text=text)


def test_content_hash_stable_et_sensible():
    assert content_hash("abc") == content_hash("abc")
    assert content_hash("abc") != content_hash("abd")
    assert len(content_hash("abc")) == 64  # sha256 hex


def test_chunk_id_deterministe():
    assert chunk_id("/docs/a.md", 0) == chunk_id("/docs/a.md", 0)
    assert chunk_id("/docs/a.md", 0).endswith(":0")
    assert chunk_id("/docs/a.md", 0).startswith(source_key("/docs/a.md"))
    assert chunk_id("/docs/a.md", 0) != chunk_id("/docs/b.md", 0)


def test_petit_texte_un_seul_chunk():
    chunks = chunk_document(_doc("court"), hash_="h")
    assert len(chunks) == 1
    assert isinstance(chunks[0], Chunk)
    assert chunks[0].text == "court"


def test_texte_long_plusieurs_chunks_et_metadonnees():
    long_text = "phrase. " * 500  # ~4000 caractères
    chunks = chunk_document(_doc(long_text), hash_="deadbeef", chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    # ids déterministes et ordonnés
    assert [c.id for c in chunks] == [chunk_id("/docs/a.md", i) for i in range(len(chunks))]
    # métadonnées attendues sur chaque chunk
    for i, c in enumerate(chunks):
        assert c.metadata["source"] == "/docs/a.md"
        assert c.metadata["title"] == "A"
        assert c.metadata["chunk_index"] == i
        assert c.metadata["content_hash"] == "deadbeef"
