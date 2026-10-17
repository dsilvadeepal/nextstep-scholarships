"""Free candidate contract regressions; no provider clients or raw-archive dependency."""

import json
from pathlib import Path

import pytest
from nextstep.models import Chunk, NormalizedDocument, Scholarship
from nextstep.rag.answer import deferred_coverage

ROOT = Path(__file__).resolve().parents[1]


def candidate():
    return json.loads((ROOT / "data/expanded-corpus-2026-10-16.json").read_text())


def test_every_admitted_award_name_passes_its_candidate_coverage_guard():
    bundle = candidate()
    blocked = {
        r["id"]: deferred_coverage(r["name"], bundle["version"])
        for r in bundle["records"]
        if deferred_coverage(r["name"], bundle["version"])
    }
    assert blocked == {}


@pytest.mark.parametrize(
    "question",
    [
        "UNC Charlotte Levine scholarship",
        "Morehead-Cain at Chapel Hill",
        "Robertson at Duke",
        "University of Alabama at Birmingham merit scholarships",
        "Florida State Presidential Scholars",
    ],
)
def test_admitted_program_full_name_variants_are_not_stale_coverage_gaps(question):
    assert not deferred_coverage(question, candidate()["version"])


def test_candidate_citations_and_metadata_resolve_to_admitted_original_spans():
    bundle = candidate()
    records = {r["id"]: Scholarship.model_validate(r) for r in bundle["records"]}
    docs = {
        d["source_id"]: NormalizedDocument.model_validate(d) for d in bundle["sources"]
    }
    selections = {
        (s["program_id"], s["source"]): s["spans"] for s in bundle["selections"]
    }
    for raw in bundle["chunks"]:
        chunk = Chunk.model_validate(raw)
        record = records[chunk.program_id]
        assert chunk.corpus_version == record.corpus_version == bundle["version"]
        assert chunk.cycle_metadata == record.cycle_metadata
        assert chunk.source_checked_at == record.source_checked_at
        assert chunk.text == "\n\n".join(
            f"{r.title}\n{r.quote}" for r in chunk.evidence
        )
        for ref in chunk.evidence:
            doc = docs[ref.source_id]
            section = next(s for s in doc.sections if s.id == ref.section_id)
            assert ref.source_id == chunk.source_id
            assert doc.content_hash == ref.document_version
            assert section.text[ref.start : ref.end] == ref.quote
            assert section.heading == ref.title
            assert any(
                s["section_id"] == ref.section_id
                and s["start"] <= ref.start < ref.end <= s["end"]
                for s in selections[(record.id, doc.source_id)]
            )
