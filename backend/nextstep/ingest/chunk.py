import hashlib

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from nextstep.models import Chunk, EvidenceRef


def make_chunks(document, records, corpus_version):
    encoding = tiktoken.get_encoding("cl100k_base")
    count = lambda text: len(encoding.encode(text, disallowed_special=()))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=75,
        length_function=count,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    programs = {r.id: r for r in records}
    chunks = []
    for section in document.sections:
        if section.program_id not in programs:
            raise ValueError(f"Unresolved program association in {section.id}")
        indivisible = section.kind in ("table", "faq", "exception")
        pieces = [section.text] if indivisible else splitter.split_text(section.text)
        section_chunks = []
        previous_start = -1
        previous_end = 0
        for piece in pieces:
            start = section.text.find(piece, max(0, previous_start + 1))
            while (
                start >= 0
                and start < previous_end
                and count(section.text[start:previous_end]) > 75
            ):
                start = section.text.find(piece, start + 1)
            if start < 0:
                raise ValueError("Split passage lost exact provenance")
            previous_start = start
            previous_end = start + len(piece)
            identity = f"{corpus_version}:{document.content_hash}:{section.program_id}:{section.id}:{start + section.start_offset}:{piece}"
            chunk_id = hashlib.sha256(identity.encode()).hexdigest()[:24]
            ref = EvidenceRef(
                id=chunk_id,
                source_id=document.source_id,
                document_version=document.content_hash,
                section_id=section.id,
                page=section.page,
                quote=piece,
                start=start + section.start_offset,
                end=start + section.start_offset + len(piece),
                url=document.url,
                fetched_at=document.fetched_at,
                title=section.heading,
                cycle=programs[section.program_id].cycle,
            )
            section_chunks.append(
                Chunk(
                    id=chunk_id,
                    program_id=section.program_id,
                    source_id=document.source_id,
                    corpus_version=corpus_version,
                    text=piece,
                    heading=f"{programs[section.program_id].name} — {section.heading}",
                    section_ids=[section.id],
                    token_count=count(piece),
                    evidence=[ref],
                    indivisible=indivisible and count(piece) > 500,
                    cycle=programs[section.program_id].cycle,
                    cycle_metadata=programs[section.program_id].cycle_metadata,
                    information_status=programs[section.program_id].information_status,
                    source_checked_at=programs[section.program_id].source_checked_at,
                )
            )
        for i, chunk in enumerate(section_chunks):
            chunk.neighbors = [
                section_chunks[j].id
                for j in (i - 1, i + 1)
                if 0 <= j < len(section_chunks)
            ]
        chunks.extend(section_chunks)
    return chunks
