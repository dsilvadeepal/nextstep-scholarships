"""Explicit local live settings; keys stay in .env, which this module never writes.

All operations share the pre-existing cumulative SQLite ledger. Hosted settings and
deployment remain separate. Pricing was rechecked against the official model pages.
"""

from decimal import Decimal
from pathlib import Path

from nextstep.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def live_settings(run_cap="1.00"):
    return Settings(
        _env_file=ROOT / ".env",
        database_url=f"sqlite:///{ROOT / 'artifacts/nextstep-live.db'}",
        live_calls_enabled=True,
        openai_run_budget_usd=Decimal(run_cap),
        openai_total_budget_usd=Decimal("5.00"),
        pricing_effective_date="2026-10-14",
        input_usd_per_million=Decimal("0.40"),
        output_usd_per_million=Decimal("1.60"),
        embedding_usd_per_million=Decimal("0.02"),
    )


def load_bundle():
    import json

    from nextstep.models import Chunk, NormalizedDocument, Scholarship

    data = json.loads((ROOT / "data/reviewed-corpus-2026-10-14.json").read_text())
    docs = {
        d["source_id"]: NormalizedDocument.model_validate(d) for d in data["sources"]
    }
    records = [Scholarship.model_validate(r) for r in data["records"]]
    chunks = [Chunk.model_validate(c) for c in data["chunks"]]
    version = data["version"]
    assert len({r.id for r in records}) == len(records)
    assert len({c.id for c in chunks}) == len(chunks)
    assert {r.id for r in records} == {c.program_id for c in chunks}
    allowed = {
        (s["program_id"], s["source"], sid)
        for s in data["selections"]
        for sid in s["sections"]
    }
    for record in records:
        assert record.corpus_version == version
        refs = {r.id: r for r in record.evidence}
        for ids in record.field_evidence.values():
            assert ids and set(ids).issubset(refs)
        for condition in record.conditions:
            assert condition.evidence
        for ref in record.evidence:
            doc = docs[ref.source_id]
            section = next(s for s in doc.sections if s.id == ref.section_id)
            assert ref.document_version == doc.content_hash
            assert ref.url == doc.url
            assert section.text[ref.start : ref.end] == ref.quote
    for chunk in chunks:
        assert chunk.corpus_version == version
        for ref in chunk.evidence:
            assert (chunk.program_id, ref.source_id, ref.section_id) in allowed
            doc = docs[ref.source_id]
            section = next(s for s in doc.sections if s.id == ref.section_id)
            assert ref.document_version == doc.content_hash
            assert section.text[ref.start : ref.end] == ref.quote == chunk.text
    return data, records, chunks
