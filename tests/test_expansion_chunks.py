from datetime import UTC, datetime
from itertools import pairwise

from nextstep.models import NormalizedDocument, Scholarship, Section

from scripts.expansion_chunks import make_reviewed_chunks, tokens


def document(sections):
    return NormalizedDocument(
        id="d",
        source_id="s",
        content_hash="hash",
        url="https://example.org/rules",
        fetched_at=datetime(2026, 10, 16, tzinfo=UTC),
        sections=sections,
    )


def test_packed_sections_keep_questions_dates_and_exact_source_spans():
    doc = document(
        [
            Section(id="a", heading="When is the deadline?", text="November 15, 2026."),
            Section(
                id="b",
                heading="Who can recommend me?",
                text="Teachers and relatives are excluded.",
            ),
        ]
    )
    chunks = make_reviewed_chunks(
        doc,
        Scholarship(id="p", name="Award", corpus_version="candidate"),
        [{"section_id": s.id, "start": 0, "end": len(s.text)} for s in doc.sections],
    )
    assert len(chunks) == 1 and chunks[0].section_ids == ["a", "b"]
    assert "When is the deadline?\nNovember 15, 2026." in chunks[0].text
    for ref in chunks[0].evidence:
        section = next(s for s in doc.sections if s.id == ref.section_id)
        assert section.text[ref.start : ref.end] == ref.quote


def test_repeated_long_text_has_at_most_75_token_overlap():
    text = (
        "A required application document must be submitted before the deadline.\n" * 220
    )
    doc = document([Section(id="a", heading="Requirements", text=text)])
    chunks = make_reviewed_chunks(
        doc,
        Scholarship(id="p", name="Award", corpus_version="candidate"),
        [{"section_id": "a", "start": 0, "end": len(text)}],
    )
    assert len(chunks) > 1
    for previous, current in pairwise(chunks):
        a, z = current.evidence[0].start, previous.evidence[-1].end
        assert a > previous.evidence[0].start
        assert a >= z or tokens(text[a:z]) <= 75
        assert current.token_count <= 500


def test_excluded_middle_never_enters_chunk_or_evidence():
    text = "Submit a transcript.\nWinner biography: Jane now attends Example College.\nNo late applications."
    doc = document([Section(id="a", heading="Rules", text=text)])
    chunks = make_reviewed_chunks(
        doc,
        Scholarship(id="p", name="Award", corpus_version="candidate"),
        [
            {"section_id": "a", "start": 0, "end": text.index("Winner")},
            {"section_id": "a", "start": text.index("No late"), "end": len(text)},
        ],
    )
    assert "Submit a transcript." in chunks[0].text
    assert "No late applications." in chunks[0].text
    assert all("Jane" not in c.text for c in chunks)
    assert all("Jane" not in r.quote for c in chunks for r in c.evidence)
