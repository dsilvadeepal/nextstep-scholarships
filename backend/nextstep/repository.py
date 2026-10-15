from nextstep.db import (
    active_corpus,
    chunk_manifest,
    corpus_versions,
    scholarships,
    serialized,
)
from nextstep.models import Chunk, Scholarship
from sqlalchemy import delete, insert, select, update


class Repository:
    def __init__(self, engine):
        self.engine = engine

    def active_version(self):
        with self.engine.connect() as conn:
            return conn.execute(
                select(active_corpus.c.version).where(active_corpus.c.id == 1)
            ).scalar_one_or_none()

    def list_scholarships(self, version):
        with self.engine.connect() as conn:
            return [
                Scholarship.model_validate(row)
                for row in conn.execute(
                    select(scholarships.c.data).where(scholarships.c.version == version)
                ).scalars()
            ]

    def get_chunks(self, version, ids=None):
        query = select(chunk_manifest.c.data).where(chunk_manifest.c.version == version)
        if ids is not None:
            query = query.where(chunk_manifest.c.id.in_(ids))
        with self.engine.connect() as conn:
            return [Chunk.model_validate(row) for row in conn.execute(query).scalars()]

    def stage_catalog(self, version, records):
        if len({r.id for r in records}) != len(records) or any(
            r.corpus_version != version for r in records
        ):
            raise ValueError("Duplicate or inconsistent versioned records")
        with serialized(self.engine) as conn:
            status = conn.execute(
                select(corpus_versions.c.status).where(
                    corpus_versions.c.version == version
                )
            ).scalar_one_or_none()
            if status is not None:
                raise ValueError(
                    "Corpus version already exists; use a new immutable version"
                )
            conn.execute(
                insert(corpus_versions).values(version=version, status="staged")
            )
            if records:
                conn.execute(
                    insert(scholarships),
                    [
                        {
                            "version": version,
                            "id": r.id,
                            "data": r.model_dump(mode="json"),
                        }
                        for r in records
                    ],
                )

    def activate_version(self, expected_old, new):
        with serialized(self.engine) as conn:
            current = conn.execute(
                select(active_corpus.c.version).where(active_corpus.c.id == 1)
            ).scalar_one_or_none()
            ready = conn.execute(
                select(corpus_versions.c.status).where(corpus_versions.c.version == new)
            ).scalar_one_or_none()
            if ready != "ready":
                raise ValueError("Corpus must be ready before activation")
            if current != expected_old:
                raise ValueError("Active corpus changed")
            if (
                conn.execute(
                    select(corpus_versions.c.version).where(
                        corpus_versions.c.version == new
                    )
                ).scalar_one_or_none()
                is None
            ):
                raise ValueError("Unknown corpus")
            if current is None:
                conn.execute(insert(active_corpus).values(id=1, version=new))
            else:
                conn.execute(
                    update(active_corpus)
                    .where(active_corpus.c.id == 1)
                    .values(version=new)
                )

    def stage_chunks(self, version, chunks):
        if len({c.id for c in chunks}) != len(chunks) or any(
            c.corpus_version != version for c in chunks
        ):
            raise ValueError("Duplicate or inconsistent chunk versions")
        with serialized(self.engine) as conn:
            status = conn.execute(
                select(corpus_versions.c.status).where(
                    corpus_versions.c.version == version
                )
            ).scalar_one()
            if status != "staged":
                raise ValueError("Published corpus is immutable")
            conn.execute(
                delete(chunk_manifest).where(chunk_manifest.c.version == version)
            )
            if chunks:
                conn.execute(
                    insert(chunk_manifest),
                    [
                        {
                            "version": version,
                            "id": c.id,
                            "data": c.model_dump(mode="json"),
                        }
                        for c in chunks
                    ],
                )

    def cached_embedding(self, key):
        from nextstep.db import embedding_cache

        with self.engine.connect() as conn:
            return conn.execute(
                select(embedding_cache.c.vector).where(embedding_cache.c.key == key)
            ).scalar_one_or_none()

    def cache_embedding(self, key, vector):
        from nextstep.db import embedding_cache

        with serialized(self.engine) as conn:
            if (
                conn.execute(
                    select(embedding_cache.c.key).where(embedding_cache.c.key == key)
                ).scalar_one_or_none()
                is None
            ):
                conn.execute(insert(embedding_cache).values(key=key, vector=vector))

    def mark_ready(self, version):
        with serialized(self.engine) as conn:
            conn.execute(
                update(corpus_versions)
                .where(corpus_versions.c.version == version)
                .values(status="ready")
            )

    def is_ready(self, version):
        with self.engine.connect() as conn:
            return (
                conn.execute(
                    select(corpus_versions.c.status).where(
                        corpus_versions.c.version == version
                    )
                ).scalar_one_or_none()
                == "ready"
            )

    def freeze_manifest(self, version):
        """Freeze SQL inputs before provider I/O; retries reuse this immutable snapshot."""
        with serialized(self.engine) as conn:
            status = conn.execute(
                select(corpus_versions.c.status).where(
                    corpus_versions.c.version == version
                )
            ).scalar_one()
            if status not in ("staged", "publishing", "ready"):
                raise ValueError("Invalid publication state")
            records = [
                Scholarship.model_validate(row)
                for row in conn.execute(
                    select(scholarships.c.data).where(scholarships.c.version == version)
                ).scalars()
            ]
            chunks = [
                Chunk.model_validate(row)
                for row in conn.execute(
                    select(chunk_manifest.c.data).where(
                        chunk_manifest.c.version == version
                    )
                ).scalars()
            ]
            if (
                not records
                or not chunks
                or {c.program_id for c in chunks} != {r.id for r in records}
            ):
                raise ValueError("Incomplete corpus manifest")
            if status == "staged":
                conn.execute(
                    update(corpus_versions)
                    .where(corpus_versions.c.version == version)
                    .values(status="publishing")
                )
            return records, chunks
