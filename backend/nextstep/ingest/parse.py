import hashlib
import io

import pdfplumber
from bs4 import BeautifulSoup, Comment, NavigableString
from langchain_core.documents import Document
from nextstep.models import NormalizedDocument, Section
from pypdf import PdfReader


def _document(data, sections, **source):
    digest = hashlib.sha256(data).hexdigest()
    return NormalizedDocument(
        id=f"{source['source_id']}:{digest}",
        content_hash=digest,
        sections=sections,
        **source,
    )


def parse_html(data: bytes, **source) -> NormalizedDocument:
    soup = BeautifulSoup(data, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    root = soup.find("main") or soup.find("article") or soup
    sections = []
    heading = "Document"
    lines = []

    def flush():
        if lines:
            sections.append(
                Section(
                    id=f"s{len(sections) + 1}", heading=heading, text="\n".join(lines)
                )
            )
            lines.clear()

    def walk(tag):
        nonlocal heading
        if isinstance(tag, Comment):
            return
        if isinstance(tag, NavigableString):
            text = str(tag).strip()
            if text:
                lines.append(text)
            return
        if tag.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            flush()
            heading = tag.get_text(" ", strip=True)
        elif tag.name == "table":
            flush()
            rows = [
                [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                for row in tag.find_all("tr")
            ]
            if rows:
                sections.append(
                    Section(
                        id=f"s{len(sections) + 1}",
                        heading=heading,
                        text="\n".join(" | ".join(row) for row in rows),
                        table_headers=rows[0],
                        table_rows=rows[1:],
                        kind="table",
                    )
                )
        else:
            for child in tag.children:
                walk(child)

    walk(root)
    flush()
    if not sections:
        raise ValueError("empty_or_unstructured_html")
    return _document(data, sections, **source)


def parse_pdf(data: bytes, **source) -> NormalizedDocument:
    sections = []
    reader = PdfReader(io.BytesIO(data))
    with pdfplumber.open(io.BytesIO(data)) as layout:
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if not text.strip():
                raise ValueError(f"needs_ocr: page {i + 1}")
            sections.append(
                Section(id=f"p{i + 1}", heading=f"Page {i + 1}", page=i + 1, text=text)
            )
            for j, table in enumerate(layout.pages[i].extract_tables()):
                rows = [[cell or "" for cell in row] for row in table]
                if rows:
                    sections.append(
                        Section(
                            id=f"p{i + 1}t{j + 1}",
                            heading=f"Page {i + 1} table {j + 1}",
                            page=i + 1,
                            text="\n".join(" | ".join(row) for row in rows),
                            table_headers=rows[0],
                            table_rows=rows[1:],
                            kind="table",
                        )
                    )
    return _document(data, sections, **source)


def sections_as_documents(document):
    return [
        Document(
            page_content=s.text,
            metadata={
                "section_id": s.id,
                "page": s.page,
                "source_id": document.source_id,
                "document_version": document.content_hash,
                "program_id": s.program_id,
                "url": document.url,
            },
        )
        for s in document.sections
    ]
