import hashlib
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PublishReport:
    version: str
    programs: int
    chunks: int
    new_embeddings: int


class Publisher:
    def __init__(self, repository, embeddings, vectors):
        self.repository, self.embeddings, self.vectors = repository, embeddings, vectors

    def publish_corpus(self, version: str, expected_old: str | None) -> PublishReport:
        repo = self.repository
        records, chunks = repo.freeze_manifest(version)
        if (
            not records
            or not chunks
            or {c.program_id for c in chunks} != {r.id for r in records}
        ):
            raise ValueError("Incomplete corpus manifest")
        vectors = []
        new = 0
        for chunk in chunks:
            text = f"{chunk.heading}\n{chunk.text}"
            key = hashlib.sha256(
                f"{self.embeddings.model}:{self.embeddings.dimensions}:{text}".encode()
            ).hexdigest()
            vector = repo.cached_embedding(key)
            if vector is None:
                output = self.embeddings.embed([text])
                if len(output) != 1:
                    raise ValueError("Embedding count mismatch")
                vector = output[0]
                new += 1
            if len(vector) != self.embeddings.dimensions or any(
                not math.isfinite(x) for x in vector
            ):
                raise ValueError("Embedding dimension or value mismatch")
            repo.cache_embedding(key, vector)
            vectors.append(vector)
        self.vectors.upsert(version, chunks, vectors)
        if not self.vectors.ready(version, [c.id for c in chunks]):
            raise ValueError("Vector index is not query-ready")
        repo.mark_ready(version)
        repo.activate_version(expected_old, version)
        return PublishReport(version, len(records), len(chunks), new)

    def rollback(self, version, expected_old):
        if not self.repository.is_ready(version):
            raise ValueError("Rollback requires retained ready corpus")
        self.repository.activate_version(expected_old, version)
