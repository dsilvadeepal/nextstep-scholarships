"""Candidate schema/provenance/operational-content gate; never activates a corpus."""

import hashlib
import json
from collections import Counter

from expansion_chunks import tokens
from nextstep.models import Chunk, NormalizedDocument, Scholarship
from reviewed_runtime import ROOT
from validate_content_exclusions import violations

BUNDLE_PATH = ROOT / "data/expanded-corpus-2026-10-16.json"


def load_candidate(check_raw=False):
    data = json.loads(BUNDLE_PATH.read_text())
    records = [Scholarship.model_validate(r) for r in data["records"]]
    chunks = [Chunk.model_validate(c) for c in data["chunks"]]
    docs = {
        d["source_id"]: NormalizedDocument.model_validate(d) for d in data["sources"]
    }
    assert data["status"] == "inactive_candidate"
    assert len({r.id for r in records}) == len(records)
    assert len({c.id for c in chunks}) == len(chunks)
    assert {c.program_id for c in chunks} == {r.id for r in records}
    assert set(docs) == {c.source_id for c in chunks}
    spans = {
        (row["program_id"], row["source"]): row["spans"] for row in data["selections"]
    }

    def validate_ref(pid, ref):
        doc = docs[ref.source_id]
        section = next(s for s in doc.sections if s.id == ref.section_id)
        assert ref.document_version == doc.content_hash
        assert ref.url == doc.url and ref.fetched_at == doc.fetched_at
        assert section.text[ref.start : ref.end] == ref.quote and ref.quote.strip()
        assert ref.title == section.heading
        assert any(
            s["section_id"] == ref.section_id
            and s["start"] <= ref.start < ref.end <= s["end"]
            for s in spans[(pid, ref.source_id)]
        )

    for record in records:
        assert record.corpus_version == data["version"] and record.source_checked_at
        refs = {r.id for r in record.evidence}
        assert refs and all(
            set(ids).issubset(refs) and ids for ids in record.field_evidence.values()
        )
        for condition in record.conditions:
            assert condition.evidence
            if condition.id == "gatech-ga-residency":
                assert {r.source_id for r in condition.evidence} == {"exp-gatech-2"}
                assert any(
                    "Georgia residents must apply by this date" in r.quote
                    for r in condition.evidence
                )
            for ref in condition.evidence:
                validate_ref(record.id, ref)
        for ref in record.evidence:
            validate_ref(record.id, ref)
    tiny_exceptions = {
        "exp-uah-1": "Source caveat next to indivisible threshold table",
        "exp-south-alabama-3": "Only current Fall 2027 priority-deadline calendar; excludes surrounding recipient spotlight",
    }
    by_id = {r.id: r for r in records}
    for chunk in chunks:
        assert chunk.corpus_version == data["version"]
        assert chunk.source_id in docs and chunk.evidence
        assert chunk.section_ids == list(
            dict.fromkeys(r.section_id for r in chunk.evidence)
        )
        assert {r.source_id for r in chunk.evidence} == {chunk.source_id}
        assert chunk.text == "\n\n".join(
            f"{r.title}\n{r.quote}" for r in chunk.evidence
        )
        assert chunk.token_count == tokens(chunk.text)
        assert chunk.token_count <= 500 or chunk.indivisible
        assert chunk.token_count >= 75 or chunk.source_id in tiny_exceptions
        assert chunk.cycle_metadata == by_id[chunk.program_id].cycle_metadata
        assert chunk.source_checked_at == by_id[chunk.program_id].source_checked_at
        for ref in chunk.evidence:
            validate_ref(chunk.program_id, ref)
    exclusions = json.loads(
        (ROOT / "data/content-exclusions-2026-10-16.json").read_text()
    )
    assert not violations(data, exclusions["exclusions"])
    if check_raw:
        originals = {
            p.stem: p
            for p in (ROOT / "artifacts/research").rglob("*")
            if p.is_file() and len(p.stem) == 64
        }
        for doc in docs.values():
            assert doc.content_hash in originals, (
                f"Missing raw archive: {doc.source_id}"
            )
            assert (
                hashlib.sha256(originals[doc.content_hash].read_bytes()).hexdigest()
                == doc.content_hash
            )
    return data, records, chunks


if __name__ == "__main__":
    data, records, chunks = load_candidate(check_raw=True)
    duplicated = Counter(c.text for c in chunks)
    report = {
        "passed": True,
        "version": data["version"],
        "bundle_sha256": hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest(),
        "records": len(records),
        "chunks": len(chunks),
        "unique_text_chunks": len(duplicated),
        "cross_award_shared_text_copies": sum(n - 1 for n in duplicated.values()),
        "documents": len(data["sources"]),
        "checks": [
            "schemas and unique IDs",
            "record/chunk version and program links",
            "raw-byte hashes",
            "exact admitted source spans and URLs",
            "all condition/field references resolve",
            "source headings and dates preserved",
            "registered content exclusions",
            "token counts, tiny-fragment exceptions and indivisible tables",
            "cycle metadata matches record",
        ],
        "limits": [
            "This validator performs no paid answer evaluation; see separate run receipts",
            "Two explicitly retained short source caveats/calendar chunks",
            "UAH 750-token table retained intact",
            "Shared UA/Auburn policy text is repeated for program isolation and excluded from unique coverage count",
        ],
    }
    path = ROOT / f"artifacts/reports/{data['version']}-validation.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
