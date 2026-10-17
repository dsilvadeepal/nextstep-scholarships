import pytest
from nextstep.db import metadata
from nextstep.ingest.publish import Publisher
from nextstep.models import Chunk, Scholarship
from nextstep.repository import Repository
from sqlalchemy import create_engine


class Embeddings:
    model = "fixture"
    dimensions = 3

    def __init__(self):
        self.texts = []

    def embed(self, texts):
        self.texts.extend(texts)
        return [[1.0, 0.0, 0.0] for _ in texts]


class Vectors:
    def __init__(self):
        self.data = {}
        self.fail = False

    def upsert(self, version, chunks, vectors):
        if self.fail:
            raise RuntimeError("offline")
        self.data[version] = {c.id for c in chunks}

    def ready(self, version, ids):
        return self.data.get(version) == set(ids)


def stage(repo, version):
    repo.stage_catalog(version, [Scholarship(id="a", name="A", corpus_version=version)])
    repo.stage_chunks(
        version,
        [
            Chunk(
                id="c",
                program_id="a",
                source_id="s",
                corpus_version=version,
                text="Seniors",
                heading="A",
                section_ids=["s"],
                token_count=2,
            )
        ],
    )


def test_failed_publication_preserves_active_and_cache_and_rollback(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/pub.db")
    metadata.create_all(engine)
    repo = Repository(engine)
    embed = Embeddings()
    vectors = Vectors()
    publisher = Publisher(repo, embed, vectors)
    stage(repo, "one")
    publisher.publish_corpus("one", None)
    stage(repo, "two")
    vectors.fail = True
    with pytest.raises(RuntimeError):
        publisher.publish_corpus("two", "one")
    assert repo.active_version() == "one"
    assert repo.get_chunks("one")[0].corpus_version == "one"
    vectors.fail = False
    publisher.publish_corpus("two", "one")
    assert len(embed.texts) == 1
    publisher.rollback("one", "two")
    assert repo.active_version() == "one"
    assert repo.list_scholarships("one")[0].corpus_version == "one"


def test_bad_dimension_never_activates(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/pub.db")
    metadata.create_all(engine)
    repo = Repository(engine)
    stage(repo, "one")
    embed = Embeddings()
    embed.dimensions = 4
    with pytest.raises(ValueError, match="dimension"):
        Publisher(repo, embed, Vectors()).publish_corpus("one", None)
    assert repo.active_version() is None


def test_manifest_is_frozen_before_external_indexing(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/pub.db")
    metadata.create_all(engine)
    repo = Repository(engine)
    stage(repo, "one")

    class RacingVectors(Vectors):
        def upsert(self, version, chunks, vectors):
            replacement = chunks[0].model_copy(
                update={"id": "replacement", "text": "Changed rule"}
            )
            with pytest.raises(ValueError, match="immutable|frozen"):
                repo.stage_chunks(version, [replacement])
            super().upsert(version, chunks, vectors)

    vectors = RacingVectors()
    Publisher(repo, Embeddings(), vectors).publish_corpus("one", None)
    assert {c.id for c in repo.get_chunks("one")} == vectors.data["one"]
