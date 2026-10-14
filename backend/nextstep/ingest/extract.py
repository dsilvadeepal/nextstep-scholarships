"""Deterministic evidence checks; they establish resolution, not truth."""

from nextstep.models import NormalizedDocument, EvidenceRef


def validate_evidence(document: NormalizedDocument, ref: EvidenceRef) -> None:
    sections = {s.id: s for s in document.sections}
    section = sections.get(ref.section_id)
    if (
        ref.source_id != document.source_id
        or ref.document_version != document.content_hash
        or ref.url != document.url
        or ref.fetched_at != document.fetched_at
        or section is None
        or ref.page != section.page
        or ref.start >= ref.end
        or ref.end > len(section.text)
        or section.text[ref.start : ref.end] != ref.quote
    ):
        raise ValueError("Evidence does not resolve to exact normalized source text")
