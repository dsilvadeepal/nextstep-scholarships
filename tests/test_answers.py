import pytest
from nextstep.models import AnswerBlock, AnswerResult, RetrievedEvidence
from nextstep.rag.answer import validate_answer


def test_unknown_citations_and_uncited_facts_rejected():
    for refs in [[], ["invented"]]:
        answer = AnswerResult(
            blocks=[AnswerBlock(text="Deadline is tomorrow", evidence_ids=refs)],
            corpus_version="v",
            method="semantic",
            evidence=RetrievedEvidence(chunks=[]),
        )
        with pytest.raises(ValueError):
            validate_answer(answer)


def test_gap_only_answer_allowed():
    answer = AnswerResult(
        blocks=[],
        gaps=["No evidence available. Check the official sponsor."],
        corpus_version="v",
        method="semantic",
        evidence=RetrievedEvidence(chunks=[]),
    )
    assert validate_answer(answer) == answer


def test_answer_flow_preserves_deterministic_unknowns_and_uses_lcel():
    from nextstep.models import (
        Chunk,
        Condition,
        RetrievalRequest,
        Scholarship,
        StudentProfile,
    )
    from nextstep.rag.answer import AnswerService

    class Retriever:
        def retrieve(self, request):
            return RetrievedEvidence(
                chunks=[
                    Chunk(
                        id="c",
                        program_id="a",
                        source_id="s",
                        corpus_version="v",
                        text="GPA 3.5 required.",
                        heading="A",
                        section_ids=["s"],
                        token_count=5,
                    )
                ]
            )

    class Model:
        def invoke(self, schema, instructions, payload, max_output):
            # Model cannot replace deterministic fit outcomes; output contains only cited claims.
            return schema(
                blocks=[AnswerBlock(text="GPA 3.5 required.", evidence_ids=["c"])],
                gaps=[],
            ), {}

    records = [
        Scholarship(
            id="a",
            name="A",
            corpus_version="v",
            information_status="automatically_extracted",
            conditions=[
                Condition(
                    id="gpa",
                    kind="gpa",
                    operator="gte",
                    value={"value": 3.5, "scale": 4, "type": "unweighted"},
                )
            ],
        )
    ]
    result = AnswerService(Retriever(), Model(), records).answer_question(
        StudentProfile(),
        RetrievalRequest(
            question="Can I apply?", program_ids=["a"], corpus_version="v"
        ),
        [],
    )
    assert result.blocks[0].evidence_ids == ["c"]
    assert any("gpa" in gap.lower() for gap in result.gaps)
    assert result.corpus_version == "v"


def test_followup_retrieval_includes_bounded_prior_user_context():
    from nextstep.models import ChatTurn, RetrievalRequest, StudentProfile
    from nextstep.rag.answer import AnswerService

    class Retrieval:
        def retrieve(self, request):
            assert "Coolidge" in request.question and "deadline" in request.question
            assert "unsupported assistant claim" not in request.question
            assert len(request.question) <= 2000
            return RetrievedEvidence(chunks=[])

    AnswerService(Retrieval(), None, []).answer_question(
        StudentProfile(),
        RetrievalRequest(question="What about its deadline?", corpus_version="v"),
        [
            ChatTurn(role="user", content="Tell me about Coolidge"),
            ChatTurn(role="assistant", content="unsupported assistant claim"),
        ],
    )
