import pytest
from nextstep.models import AnswerBlock, AnswerResult, RetrievedEvidence
from nextstep.rag.answer import validate_answer


def test_explicit_catalog_acronym_narrows_unselected_search():
    from nextstep.models import RetrievalRequest, Scholarship, StudentProfile
    from nextstep.rag.answer import AnswerService

    class CaptureRetriever:
        def retrieve(self, request):
            self.request = request
            return RetrievedEvidence(chunks=[])

    retriever = CaptureRetriever()
    records = [
        Scholarship(id="uab", name="UAB Freshman Scholarships", corpus_version="v"),
        Scholarship(id="uah", name="UAH Freshman Scholarships", corpus_version="v"),
    ]
    service = AnswerService(retriever, None, records)
    service.answer_question(
        StudentProfile(),
        RetrievalRequest(question="Does UAB superscore ACT?", corpus_version="v"),
        [],
    )
    assert retriever.request.program_ids == ["uab"]
    service.answer_question(
        StudentProfile(),
        RetrievalRequest(question="Compare UAB and UAH", corpus_version="v"),
        [],
    )
    assert retriever.request.program_ids == ["uab", "uah"]
    service.answer_question(
        StudentProfile(),
        RetrievalRequest(
            question="Does UAB superscore ACT?", corpus_version="v", program_ids=["uah"]
        ),
        [],
    )
    assert retriever.request.program_ids == ["uah"]


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
            if "claims" in payload:
                return schema(
                    verdicts=[
                        {"claim_index": i, "supported": True, "reason": "fixture"}
                        for i, _ in enumerate(payload["claims"])
                    ]
                ), {}
            unit = payload["evidence"][0]
            assert "profile" in payload and "condition_checks" in payload
            return schema(
                claims=[
                    {
                        "text": unit["text"],
                        "program_id": unit["program_id"],
                        "supports": [
                            {"evidence_id": unit["id"], "quote": unit["text"]}
                        ],
                    }
                ]
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


def test_answer_selection_rejects_invented_units_and_preserves_unicode():
    from nextstep.models import Chunk, RetrievalRequest, StudentProfile
    from nextstep.rag.answer import AnswerService

    class Retriever:
        def retrieve(self, request):
            return RetrievedEvidence(
                chunks=[
                    Chunk(
                        id="c",
                        program_id="p",
                        source_id="s",
                        corpus_version="v",
                        text="A student’s award. Juniors only.",
                        heading="Award",
                        section_ids=["s"],
                        token_count=8,
                    )
                ]
            )

    class Model:
        invalid = False

        def invoke(self, schema, instructions, payload, max_output):
            if "claims" in payload:
                return schema(
                    verdicts=[
                        {"claim_index": 0, "supported": True, "reason": "fixture"}
                    ]
                ), {}
            unit = payload["evidence"][0]
            return schema(
                claims=[
                    {
                        "text": unit["text"],
                        "program_id": unit["program_id"],
                        "supports": [
                            {
                                "evidence_id": "invented"
                                if self.invalid
                                else unit["id"],
                                "quote": unit["text"],
                            }
                        ],
                    }
                ]
            ), {}

    model = Model()
    service = AnswerService(Retriever(), model, [])
    request = RetrievalRequest(question="What is it?", corpus_version="v")
    assert (
        service.answer_question(StudentProfile(), request, []).blocks[0].text
        == "A student’s award. Juniors only."
    )
    model.invalid = True
    result = service.answer_question(StudentProfile(), request, [])
    assert not result.blocks and any("withheld" in g for g in result.gaps)


def test_deferred_named_program_never_substitutes_related_university_rules():
    from nextstep.models import RetrievalRequest, StudentProfile
    from nextstep.rag.answer import AnswerService

    class Forbidden:
        def retrieve(self, request):
            raise AssertionError(
                "Deferred program must not retrieve unrelated scholarships"
            )

    answer = AnswerService(Forbidden(), None, []).answer_question(
        StudentProfile(),
        RetrievalRequest(
            question="What are the confirmed 2027–28 HOPE Scholarship rules?",
            corpus_version="verified-2026-10-14-v2",
        ),
        [],
    )
    assert answer.blocks == []
    assert any("2027–28" in gap and "not" in gap for gap in answer.gaps)
    assert answer.evidence.chunks == []


def test_coverage_guard_is_versioned_and_does_not_match_ordinary_hope():
    from nextstep.rag.answer import deferred_coverage

    assert not deferred_coverage(
        "I hope to qualify for Alabama", "verified-2026-10-14-v2"
    )
    assert not deferred_coverage("HOPE Scholarship", "synthetic-fixture")
    assert deferred_coverage(
        "Can I get a Clemson scholarship?", "verified-2026-10-14-v2"
    )

    assert deferred_coverage(
        "Can I get a Clemson scholarship?", "candidate-2026-10-16-v4"
    )
    assert not deferred_coverage(
        "What are Georgia Tech's Stamps rules?", "candidate-2026-10-16-v4"
    )
    assert not deferred_coverage(
        "What are Florida State Presidential Scholars rules?",
        "candidate-2026-10-16-v4",
    )
    assert deferred_coverage(
        "What are University of Florida scholarships?",
        "candidate-2026-10-16-v4",
    )


def test_reviewed_conflicts_identify_each_unresolved_field_in_answer_gaps():
    from nextstep.models import (
        RetrievalRequest,
        RetrievedEvidence,
        Scholarship,
        StudentProfile,
    )
    from nextstep.rag.answer import AnswerService

    class EmptyRetriever:
        def retrieve(self, request):
            return RetrievedEvidence(chunks=[])

    record = Scholarship(
        id="p",
        name="Award",
        corpus_version="v",
        information_status="conflicting",
        conflicts={
            "transcript_requirement": [
                "Unofficial initially",
                "Official via counselor",
            ],
            "income_measure": ["Gross income", "Adjusted gross income"],
        },
    )
    answer = AnswerService(EmptyRetriever(), None, [record]).answer_question(
        StudentProfile(),
        RetrievalRequest(
            question="Which transcript and income definition should I use?",
            program_ids=["p"],
            corpus_version="v",
        ),
        [],
    )
    text = " ".join(answer.gaps).lower()
    assert (
        "transcript" in text
        and "unofficial" in text
        and "official via counselor" in text
    )
    assert (
        "income" in text and "gross income" in text and "adjusted gross income" in text
    )
