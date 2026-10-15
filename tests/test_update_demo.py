"""Synthetic controlled update only; never represents sponsor policy."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from nextstep.db import metadata
from nextstep.ingest.chunk import make_chunks
from nextstep.ingest.parse import parse_html
from nextstep.ingest.publish import Publisher
from nextstep.matching import match_catalog
from nextstep.models import (
    GPA,
    AnswerBlock,
    Condition,
    RetrievalRequest,
    Scholarship,
    StudentProfile,
)
from nextstep.rag.answer import AnswerService
from nextstep.rag.retrieve import Retriever
from nextstep.repository import Repository
from sqlalchemy import create_engine
from test_publication import Embeddings, Vectors


def test_synthetic_update_changes_matching_and_cited_answer_together(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/update.db")
    metadata.create_all(engine)
    repo = Repository(engine)
    vectors = Vectors()
    publisher = Publisher(repo, Embeddings(), vectors)
    for version, gpa, deadline in [
        ("synthetic-old", 3.0, date(2026, 11, 1)),
        ("synthetic-new", 3.5, date(2026, 10, 1)),
    ]:
        doc = parse_html(
            Path(f"data/synthetic_update/{version}.html").read_bytes(),
            source_id="synthetic-only",
            url="https://example.org/synthetic-only",
            fetched_at=datetime(2026, 10, 14, tzinfo=UTC),
        )
        for section in doc.sections:
            section.program_id = "synthetic-award"
        record = Scholarship(
            id="synthetic-award",
            name="SYNTHETIC TEST AWARD",
            corpus_version=version,
            deadline=deadline,
            information_status="automatically_extracted",
            conditions=[
                Condition(
                    id="gpa",
                    kind="gpa",
                    operator="gte",
                    value={"value": gpa, "scale": 4, "type": "unweighted"},
                )
            ],
        )
        repo.stage_catalog(version, [record])
        repo.stage_chunks(version, make_chunks(doc, [record], version))
    publisher.publish_corpus("synthetic-old", None)
    profile = StudentProfile(grade=12, gpa=GPA(value=3.2, scale=4, type="unweighted"))

    def read():
        version = repo.active_version()
        records = repo.list_scholarships(version)
        chunks = repo.get_chunks(version)

        class Dense:
            def search(self, *args):
                return [c.id for c in chunks]

        class Model:
            def invoke(self, schema, instructions, payload, max_output):
                return schema(
                    blocks=[
                        AnswerBlock(text=chunks[0].text, evidence_ids=[chunks[0].id])
                    ]
                ), {}

        answer = AnswerService(
            Retriever(chunks, Dense()), Model(), records
        ).answer_question(
            profile,
            RetrievalRequest(question="Rules?", corpus_version=version),
            [],
            as_of=date(2026, 10, 14),
        )
        return match_catalog(records, profile, date(2026, 10, 14))[0], answer

    before, answer = read()
    assert before.group == "matches" and "3.0" in answer.blocks[0].text
    vectors.fail = True
    with pytest.raises(RuntimeError):
        publisher.publish_corpus("synthetic-new", "synthetic-old")
    assert read()[1].corpus_version == "synthetic-old"
    vectors.fail = False
    publisher.publish_corpus("synthetic-new", "synthetic-old")
    after, answer = read()
    assert after.group == "unmet" and after.timing == "closed"
    assert "3.5" in answer.blocks[0].text and answer.corpus_version == "synthetic-new"
    publisher.rollback("synthetic-old", "synthetic-new")
    assert read()[0].group == "matches"
