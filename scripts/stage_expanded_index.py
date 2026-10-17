"""Stage the frozen candidate with full metadata readback; never activate it."""

import hashlib
import json
import math
from datetime import date
from decimal import Decimal

from expanded_runtime import BUNDLE_PATH, load_candidate
from expansion_chunks import tokens
from nextstep.db import eval_results, usage_ledger
from nextstep.ingest.cli import stage_or_resume
from nextstep.limits import BudgetLedger
from nextstep.providers import OpenAIEmbeddingProvider, PineconeStore
from nextstep.repository import Repository
from reviewed_runtime import ROOT, live_settings
from sqlalchemy import create_engine, func, select


class CandidateStore(PineconeStore):
    def __init__(self, settings, embeddings, records, families):
        super().__init__(settings, embeddings)
        self.records = {r.id: r for r in records}
        self.families = families

    def metadata_for(self, version, chunk):
        result = super().metadata_for(version, chunk)
        record = self.records[chunk.program_id]
        result.update(
            metadata_schema="reviewed-spans-v2",
            publication_status="inactive_candidate",
            operational_content=True,
            family_id=self.families[chunk.program_id],
            token_count=chunk.token_count,
            evidence_refs_json=json.dumps(
                [r.model_dump(mode="json") for r in chunk.evidence],
                separators=(",", ":"),
            ),
        )
        if record.deadline:
            result["deadline_date"] = record.deadline.isoformat()
        if record.timezone:
            result["deadline_timezone"] = record.timezone
        if record.opens:
            result["opens_date"] = record.opens.isoformat()
        result["timing_as_of"] = "2026-10-16"
        result["application_timing"] = (
            "closed"
            if record.deadline and record.deadline < date(2026, 10, 16)
            else "upcoming"
            if record.opens and record.opens > date(2026, 10, 16)
            else "open"
            if record.opens
            and record.deadline
            and record.opens <= date(2026, 10, 16) <= record.deadline
            else "unknown"
        )
        assert len(json.dumps(result).encode()) < 40000
        return result


def main():
    bundle, records, chunks = load_candidate(check_raw=True)
    frozen_hash = hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest()
    settings = live_settings("0.05").model_copy(
        update={"pricing_effective_date": "2026-10-16"}
    )
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        reserved = conn.execute(
            select(func.count())
            .select_from(usage_ledger)
            .where(usage_ledger.c.status == "reserved")
        ).scalar_one()
        running = conn.execute(
            select(func.count())
            .select_from(eval_results)
            .where(eval_results.c.status == "running")
        ).scalar_one()
    if reserved or running:
        raise ValueError(
            "Outstanding paid reservation or running evaluation; staging blocked"
        )
    version = bundle["version"]
    ledger = BudgetLedger(
        engine, Decimal("0.05"), Decimal(5), enabled=True, run_id=version
    )
    before = ledger.spent()
    repo = Repository(engine)
    active_before = repo.active_version()
    embeddings = OpenAIEmbeddingProvider(settings, ledger)
    # Verify Pinecone access before making any embedding request.
    store = CandidateStore(settings, embeddings, records, bundle["program_families"])
    stage_or_resume(repo, version, records, chunks)
    vectors = {}
    pending = []
    new = 0
    requested_tokens = 0

    def flush():
        nonlocal new, requested_tokens
        if not pending:
            return
        result = embeddings.embed([text for _, _, text in pending])
        assert len(result) == len(pending)
        for (chunk, key, text), vector in zip(pending, result):
            assert len(vector) == embeddings.dimensions and all(
                math.isfinite(v) for v in vector
            )
            repo.cache_embedding(key, vector)
            vectors[chunk.id] = vector
            new += 1
            requested_tokens += tokens(text)
        pending.clear()
        print(f"Prepared {len(vectors)}/{len(chunks)} vectors", flush=True)

    for chunk in chunks:
        text = f"{chunk.heading}\n{chunk.text}"
        key = hashlib.sha256(
            f"{embeddings.model}:{embeddings.dimensions}:{text}".encode()
        ).hexdigest()
        cached = repo.cached_embedding(key)
        if cached is not None:
            vectors[chunk.id] = cached
        else:
            if pending and sum(tokens(t) for _, _, t in pending) + tokens(text) > 15000:
                flush()
            pending.append((chunk, key, text))
    flush()
    assert hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest() == frozen_hash
    store.upsert(version, chunks, [vectors[c.id] for c in chunks])
    metadata_checked = 0
    for start in range(0, len(chunks), 100):
        batch = chunks[start : start + 100]
        response = store.index.fetch(namespace=version, ids=[c.id for c in batch])
        for chunk in batch:
            actual = response.vectors[chunk.id].metadata
            expected = store.metadata_for(version, chunk)
            assert actual == expected, chunk.id
            assert json.loads(actual["evidence_refs_json"]) == [
                r.model_dump(mode="json") for r in chunk.evidence
            ]
            metadata_checked += 1
    ready = store.ready(version, [c.id for c in chunks])
    if ready:
        repo.mark_ready(version)
    assert repo.active_version() == active_before
    report = {
        "version": version,
        "bundle_sha256": frozen_hash,
        "families": len(set(bundle["program_families"].values())),
        "programs": len(records),
        "documents": len(bundle["sources"]),
        "chunks": len(chunks),
        "new_embeddings": new,
        "embedding_input_tokens": requested_tokens,
        "metadata_readback_checked": metadata_checked,
        "query_ready": ready,
        "active_version_unchanged": active_before,
        "spent_before_usd": str(before),
        "incremental_usd": str(ledger.spent() - before),
        "cumulative_spent_usd": str(ledger.spent()),
        "budget_cap_usd": "5.00",
        "pricing_checked_on": "2026-10-16",
        "pricing_source": "https://developers.openai.com/api/docs/models/text-embedding-3-small",
        "activated": False,
    }
    (ROOT / f"artifacts/reports/{version}-staged-index.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
    if not ready:
        raise SystemExit(
            "Staged but not query ready; repeat read-only verification, not paid embedding"
        )


if __name__ == "__main__":
    main()
