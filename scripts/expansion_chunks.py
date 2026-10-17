"""Pack reviewed operational spans with exact, multi-section provenance."""

import hashlib
import re
from itertools import pairwise

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from nextstep.models import Chunk, EvidenceRef

ENCODING = tiktoken.get_encoding("cl100k_base")


def tokens(text):
    return len(ENCODING.encode(text, disallowed_special=()))


def make_reviewed_chunks(document, record, spans):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=440,
        chunk_overlap=75,
        length_function=tokens,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    units = []
    for span in spans:
        section = next(s for s in document.sections if s.id == span["section_id"])
        start, end = span["start"], span["end"]
        text = section.text[start:end]
        # Standalone tables remain intact; FAQs divide at question boundaries.
        boundaries = [0]
        if section.kind != "table" and section.page is None:
            boundaries += [
                m.start()
                for m in re.finditer(r"(?m)^(?:Q: )?[^\n]{8,240}\?\s*$", text)
                if m.start()
            ]
        boundaries += [len(text)]
        for a, z in pairwise(boundaries):
            unit = text[a:z]
            pieces = [unit] if section.kind == "table" else splitter.split_text(unit)
            cursor = -1
            previous_end = 0
            for piece in pieces:
                offset = unit.find(piece, cursor + 1)
                while (
                    offset >= 0
                    and offset < previous_end
                    and tokens(unit[offset:previous_end]) > 75
                ):
                    offset = unit.find(piece, offset + 1)
                if offset < 0:
                    raise ValueError("Exact source offset lost")
                cursor = offset
                previous_end = offset + len(piece)
                units.append((section, start + a + offset, piece))

    def render(batch):
        return "\n\n".join(f"{s.heading}\n{text}" for s, _, text in batch)

    batches, pending = [], []
    for unit in units:
        if pending and tokens(render(pending + [unit])) > 500:
            batches.append(pending)
            pending = []
        pending.append(unit)
    if pending:
        batches.append(pending)
    if len(batches) > 1 and tokens(render(batches[-1])) < 75:
        previous, last = batches[-2:]
        if (
            len(previous) > 1
            and tokens(render(previous[:-1])) >= 75
            and tokens(render(previous[-1:] + last)) <= 500
        ):
            batches[-2], batches[-1] = previous[:-1], previous[-1:] + last

    chunks = []
    seen = set()
    for batch in batches:
        text = render(batch)
        if text in seen:
            continue
        seen.add(text)
        identity = f"{record.corpus_version}:{record.id}:{document.content_hash}:{[(s.id, a) for s, a, _ in batch]}:{text}"
        cid = hashlib.sha256(identity.encode()).hexdigest()[:24]
        refs = [
            EvidenceRef(
                id=f"{cid}-{i}",
                source_id=document.source_id,
                document_version=document.content_hash,
                section_id=s.id,
                page=s.page,
                quote=piece,
                start=a,
                end=a + len(piece),
                url=document.url,
                fetched_at=document.fetched_at,
                title=s.heading,
                cycle=record.cycle,
            )
            for i, (s, a, piece) in enumerate(batch)
        ]
        chunks.append(
            Chunk(
                id=cid,
                program_id=record.id,
                source_id=document.source_id,
                corpus_version=record.corpus_version,
                text=text,
                heading=f"{record.name} — "
                + " / ".join(dict.fromkeys(s.heading for s, _, _ in batch)),
                section_ids=list(dict.fromkeys(s.id for s, _, _ in batch)),
                token_count=tokens(text),
                evidence=refs,
                indivisible=len(batch) == 1
                and batch[0][0].kind == "table"
                and tokens(text) > 500,
                cycle=record.cycle,
                cycle_metadata=record.cycle_metadata,
                information_status=record.information_status,
                source_checked_at=record.source_checked_at,
            )
        )
    # Neighbors within a document/program only; they are not evidence by themselves.
    for i, chunk in enumerate(chunks):
        chunk.neighbors = [chunks[j].id for j in (i - 1, i + 1) if 0 <= j < len(chunks)]
    return chunks
