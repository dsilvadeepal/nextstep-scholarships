"""Stage and verify new Pinecone vectors; do not change the active corpus pointer."""

import hashlib
import json
import math

from nextstep.ingest.cli import stage_or_resume
from nextstep.limits import BudgetLedger
from nextstep.providers import OpenAIEmbeddingProvider, PineconeStore
from nextstep.repository import Repository
from reviewed_runtime import ROOT, live_settings, load_bundle
from sqlalchemy import create_engine


def main():
    data, records, chunks = load_bundle()
    settings = live_settings()
    repo = Repository(create_engine(settings.database_url))
    version = data["version"]
    stage_or_resume(repo, version, records, chunks)
    ledger = BudgetLedger(
        repo.engine,
        settings.openai_run_budget_usd,
        settings.openai_total_budget_usd,
        enabled=True,
        run_id=version,
    )
    embeddings = OpenAIEmbeddingProvider(settings, ledger)
    store = PineconeStore(settings, embeddings)
    vectors = []
    new = 0
    for i, chunk in enumerate(chunks):
        text = f"{chunk.heading}\n{chunk.text}"
        key = hashlib.sha256(
            f"{embeddings.model}:{embeddings.dimensions}:{text}".encode()
        ).hexdigest()
        vector = repo.cached_embedding(key)
        if vector is None:
            vector = embeddings.embed([text])[0]
            repo.cache_embedding(key, vector)
            new += 1
        assert len(vector) == embeddings.dimensions and all(
            math.isfinite(v) for v in vector
        )
        vectors.append(vector)
        if (i + 1) % 25 == 0:
            print(f"Prepared {i + 1}/{len(chunks)} vectors", flush=True)
    store.upsert(version, chunks, vectors)
    ready = store.ready(version, [c.id for c in chunks])
    if ready:
        repo.mark_ready(version)
    report = {
        "version": version,
        "programs": len(records),
        "chunks": len(chunks),
        "new_embeddings": new,
        "query_ready": ready,
        "active_version_unchanged": repo.active_version(),
        "spent_usd": str(ledger.spent()),
    }
    (ROOT / f"artifacts/reports/{version}-staged-index.json").write_text(
        json.dumps(report, indent=2)
    )
    print(json.dumps(report))
    if not ready:
        raise SystemExit(
            "Index not query-ready; no activation. A read-only readiness check can be repeated."
        )


if __name__ == "__main__":
    main()
