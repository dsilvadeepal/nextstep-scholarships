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
