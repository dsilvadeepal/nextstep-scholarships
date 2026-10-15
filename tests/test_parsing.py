from datetime import UTC, datetime

import pytest
from nextstep.ingest.parse import parse_html, parse_pdf, sections_as_documents
from nextstep.storage import LocalArtifactStore


def test_html_keeps_exceptions_and_separates_programs():
    html = b"<nav>Menu</nav><main><h2>A Award</h2><p>GPA 3.0 except renewed awards.</p><h2>B Award</h2><p>Senior applicants only.</p></main>"
    doc = parse_html(
        html,
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
    )
    assert len(doc.sections) == 2
    assert "except renewed" in doc.sections[0].text
    assert "Senior" not in doc.sections[0].text
    assert "Menu" not in "".join(s.text for s in doc.sections)
    assert sections_as_documents(doc)[0].metadata["section_id"] == doc.sections[0].id


def test_empty_pdf_needs_ocr():
    import io

    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=600, height=800)
    buf = io.BytesIO()
    writer.write(buf)
    with pytest.raises(ValueError, match="needs_ocr"):
        parse_pdf(
            buf.getvalue(),
            source_id="s",
            url="https://example.org",
            fetched_at=datetime.now(UTC),
        )


def test_artifacts_stable_and_confined(tmp_path):
    store = LocalArtifactStore(tmp_path)
    assert store.put("originals/abc.html", b"original") == store.put(
        "originals/abc.html", b"original"
    )
    assert store.get("originals/abc.html") == b"original"
    with pytest.raises(ValueError):
        store.put("../escape", b"no")


def test_direct_container_text_preserves_exclusions():
    doc = parse_html(
        b"<main><h2>Award</h2><p>Minimum GPA 3.0.</p><div>Exception: employees are ineligible.</div><dl><dt>Residency</dt><dd>Georgia only.</dd></dl></main>",
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
    )
    text = "\n".join(s.text for s in doc.sections)
    assert "employees are ineligible" in text
    assert "Georgia only" in text


def test_table_without_header_never_promotes_first_data_row_to_schema():
    doc = parse_html(
        b"<table><tr><td>A Award</td><td>3.0</td></tr><tr><td>B Award</td><td>2.5</td></tr></table>",
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(UTC),
    )
    assert doc.sections[0].table_headers == []
    assert doc.sections[0].table_rows[0] == ["A Award", "3.0"]
    assert doc.sections[0].warnings
