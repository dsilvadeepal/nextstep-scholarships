from datetime import UTC, datetime

import pytest
from nextstep.ingest.extract import validate_evidence
from nextstep.models import EvidenceRef, NormalizedDocument, Section


def test_exact_evidence_rejects_fabrication_and_wrong_source():
    doc = NormalizedDocument(
        id="doc",
        content_hash="hash",
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
        sections=[Section(id="one", heading="Rules", text="Seniors only.")],
    )
    ref = EvidenceRef(
        id="e",
        source_id="s",
        document_version="hash",
        section_id="one",
        quote="Seniors",
        start=0,
        end=7,
        url=doc.url,
        fetched_at=doc.fetched_at,
    )
    validate_evidence(doc, ref)
    for overrides in [
        {"quote": "Juniors"},
        {"start": 1},
        {"document_version": "old"},
        {"source_id": "other"},
        {"url": "https://wrong.org"},
    ]:
        with pytest.raises(ValueError):
            validate_evidence(doc, ref.model_copy(update=overrides))


def test_extraction_validates_fields_and_never_certifies_model_output():
    from nextstep.ingest.extract import extract_scholarships

    doc = NormalizedDocument(
        id="doc",
        content_hash="hash",
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
        sections=[Section(id="one", heading="A", text="Award A. Seniors only.")],
    )
    ref = EvidenceRef(
        id="e",
        source_id="s",
        document_version="hash",
        section_id="one",
        quote="Award A. Seniors only.",
        start=0,
        end=23,
        url=doc.url,
        fetched_at=doc.fetched_at,
    )

    class Model:
        def extract(self, text):
            return {
                "records": [
                    {
                        "id": "a",
                        "corpus_version": "staged",
                        "name": "Award A",
                        "information_status": "source_checked",
                        "evidence": [ref.model_dump(mode="json")],
                        "field_evidence": {"name": ["e"]},
                    }
                ]
            }

    # Incorrect source offsets cannot pass just because the model returns a valid schema.
    with pytest.raises(ValueError):
        extract_scholarships(doc, Model())
    ref.end = len(doc.sections[0].text)
    records = extract_scholarships(doc, Model())
    assert records[0].information_status == "incomplete"
    assert records[0].deadline is None


def test_uncited_exception_retained_for_single_program_and_multisource_conflicts():
    from nextstep.ingest.extract import associate_sections
    from nextstep.models import Scholarship

    doc = NormalizedDocument(
        id="doc",
        content_hash="h",
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
        sections=[
            Section(id="rule", heading="A", text="GPA 3.0"),
            Section(id="exception", heading="Exclusions", text="Employees excluded"),
        ],
    )
    assigned = associate_sections(
        doc, [Scholarship(id="a", name="A", corpus_version="v")]
    )
    assert len(assigned.sections) == 2 and assigned.sections[1].program_id == "a"
    with pytest.raises(ValueError, match="unassigned|Unassigned"):
        associate_sections(
            doc,
            [
                Scholarship(id="a", name="A", corpus_version="v"),
                Scholarship(id="b", name="B", corpus_version="v"),
            ],
        )


def test_cross_source_reconciliation_keeps_conflicting_rules():
    from nextstep.ingest.reconcile import reconcile_records
    from nextstep.models import Condition, Scholarship

    records = [
        Scholarship(
            id="a",
            name="Award",
            sponsor="Sponsor",
            corpus_version="v",
            deadline="2026-11-01",
            conditions=[Condition(id="grade", kind="grade", operator="eq", value=12)],
        ),
        Scholarship(
            id="a",
            name="Award",
            sponsor="Sponsor",
            corpus_version="v",
            deadline="2026-12-01",
            conditions=[Condition(id="grade", kind="grade", operator="eq", value=11)],
        ),
    ]
    merged, report = reconcile_records(records)
    assert len(merged) == 1 and merged[0].information_status == "conflicting"
    assert merged[0].deadline is None and len(merged[0].conditions) == 2
    assert report["conflicts"] == ["a"] and report["duplicates_merged"] == 1


def test_reviewed_program_partition_preserves_original_offsets():
    from nextstep.ingest.chunk import make_chunks
    from nextstep.ingest.extract import associate_sections
    from nextstep.models import Scholarship

    doc = NormalizedDocument(
        id="d",
        content_hash="h",
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
        sections=[
            Section(
                id="rules", heading="Rules", text="Award A: GPA 3.0. Award B: GPA 3.5."
            )
        ],
    )
    records = [Scholarship(id=x, name=x, corpus_version="v") for x in ["a", "b"]]
    plans = {
        "rules": [
            {"start": 0, "end": 18, "program_ids": ["a"]},
            {"start": 18, "end": len(doc.sections[0].text), "program_ids": ["b"]},
        ]
    }
    assigned = associate_sections(doc, records, partitions=plans, expected_hash="h")
    chunks = make_chunks(assigned, records, "v")
    assert len(chunks) == 2
    for chunk in chunks:
        for ref in chunk.evidence:
            validate_evidence(doc, ref)
    assert chunks[1].evidence[0].start == 18
    with pytest.raises(ValueError, match="hash"):
        associate_sections(doc, records, partitions=plans, expected_hash="old")
