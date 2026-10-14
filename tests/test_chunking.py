from datetime import datetime, timezone
import pytest
from nextstep.models import NormalizedDocument, Section, Scholarship
from nextstep.ingest.chunk import make_chunks


def document(sections):
    return NormalizedDocument(
        id="doc",
        content_hash="hash",
        source_id="source",
        url="https://example.org",
        fetched_at=datetime.now(timezone.utc),
        sections=sections,
    )


def test_program_boundaries_and_long_section_budget():
    doc = document(
        [
            Section(
                id="a",
                heading="A rules",
                text="First program sentence. " * 1000,
                program_id="a",
            ),
            Section(
                id="b",
                heading="B FAQ",
                text="Who can apply? Seniors.",
                program_id="b",
                kind="faq",
            ),
        ]
    )
    records = [Scholarship(id=x, name=x, corpus_version="v") for x in ["a", "b"]]
    chunks = make_chunks(doc, records, "v")
    assert len([c for c in chunks if c.program_id == "b"]) == 1
    assert all(c.token_count <= 500 for c in chunks)
    assert all("Who can apply?" not in c.text for c in chunks if c.program_id == "a")
    assert all(
        ref.quote
        == next(s.text for s in doc.sections if s.id == ref.section_id)[
            ref.start : ref.end
        ]
        for c in chunks
        for ref in c.evidence
    )


def test_unassigned_sections_fail_closed():
    doc = document([Section(id="a", heading="Unknown", text="Unassigned requirements")])
    with pytest.raises(ValueError, match="association"):
        make_chunks(doc, [Scholarship(id="a", name="A", corpus_version="v")], "v")


def test_repeated_text_offsets_do_not_create_excessive_overlap():
    import tiktoken

    encoding = tiktoken.get_encoding("cl100k_base")
    text = "Repeated identical sentence. " * 1000
    doc = document([Section(id="a", heading="A", text=text, program_id="a")])
    chunks = make_chunks(doc, [Scholarship(id="a", name="A", corpus_version="v")], "v")
    for previous, current in zip(chunks, chunks[1:]):
        left, right = previous.evidence[0], current.evidence[0]
        overlap = text[right.start : left.end] if right.start < left.end else ""
        assert len(encoding.encode(overlap)) <= 75
    assert chunks[-1].evidence[0].end >= len(text.rstrip())
