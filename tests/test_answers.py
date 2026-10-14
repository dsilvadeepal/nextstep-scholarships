import pytest
from nextstep.models import AnswerResult, AnswerBlock, RetrievedEvidence
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
