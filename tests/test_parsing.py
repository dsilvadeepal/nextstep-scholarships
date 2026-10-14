from datetime import datetime, timezone
import pytest
from nextstep.ingest.parse import parse_html, parse_pdf, sections_as_documents
from nextstep.storage import LocalArtifactStore


def test_html_keeps_exceptions_and_separates_programs():
    html = b"<nav>Menu</nav><main><h2>A Award</h2><p>GPA 3.0 except renewed awards.</p><h2>B Award</h2><p>Senior applicants only.</p></main>"
    doc = parse_html(
        html,
        source_id="s",
        url="https://example.org",
        fetched_at=datetime.now(timezone.utc),
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
            fetched_at=datetime.now(timezone.utc),
        )


def test_artifacts_stable_and_confined(tmp_path):
    store = LocalArtifactStore(tmp_path)
    assert store.put("originals/abc.html", b"original") == store.put(
        "originals/abc.html", b"original"
    )
    assert store.get("originals/abc.html") == b"original"
    with pytest.raises(ValueError):
        store.put("../escape", b"no")
