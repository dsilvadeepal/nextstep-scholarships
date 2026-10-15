import pytest
from nextstep.rag.construction import construct


def payload():
    return {
        "question": "Can a junior apply?",
        "profile": {"grade": 11},
        "evidence": [
            {
                "id": "c",
                "program_id": "p",
                "text": "Can seniors apply? No. Only juniors may apply.",
            }
        ],
    }


class Model:
    evidence_id = "c"
    program = "p"
    supported = True
    incomplete_review = False

    def invoke(self, schema, instructions, data, max_output):
        if "claims" in data:
            verdicts = (
                []
                if self.incomplete_review
                else [
                    {
                        "claim_index": 0,
                        "supported": self.supported,
                        "reason": "The question is about juniors, not seniors.",
                    }
                ]
            )
            return schema(verdicts=verdicts), {"input_tokens": 10, "output_tokens": 5}
        assert data["evidence"][0]["text"].startswith("Can seniors apply?")
        return schema(
            claims=[
                {
                    "text": "The junior-year condition fits your stated grade; other conditions still need checking.",
                    "program_id": self.program,
                    "supports": [
                        {"evidence_id": self.evidence_id, "quote": "ignored model text"}
                    ],
                }
            ]
        ), {"input_tokens": 20, "output_tokens": 8}


def test_whole_faq_and_supported_synthesis_with_usage():
    blocks, gaps, usage, review = construct(Model(), payload())
    assert blocks[0].kind == "explanation"
    assert blocks[0].supporting_quotes == [payload()["evidence"][0]["text"]]
    assert not gaps and review["accepted"] == 1
    assert usage["input_tokens"] == 30 and usage["output_tokens"] == 13


@pytest.mark.parametrize(
    "field,value", [("evidence_id", "invented"), ("program", "another-award")]
)
def test_unknown_id_or_cross_award_citation_withheld(field, value):
    model = Model()
    setattr(model, field, value)
    blocks, gaps, _, review = construct(model, payload())
    assert not blocks and gaps and review["accepted"] == 0


def test_review_rejection_is_withheld_without_retry():
    model = Model()
    model.supported = False
    blocks, gaps, _, review = construct(model, payload())
    assert not blocks and "withheld" in gaps[0]
    assert review["accepted"] == 0


def test_incomplete_review_fails_closed():
    model = Model()
    model.incomplete_review = True
    with pytest.raises(ValueError, match="every claim"):
        construct(model, payload())


def test_score_acceptance_cannot_establish_numeric_qualification():
    from nextstep.rag.construction import Claim, unsupported_score_conclusion

    claim = Claim(
        text="A superscore of 27 can satisfy the award score rule.",
        program_id="p",
        supports=[{"evidence_id": "c"}],
    )
    assert unsupported_score_conclusion(
        claim, {"c": {"text": "We accept ACT superscores."}}
    )
    assert not unsupported_score_conclusion(
        claim, {"c": {"text": "ACT Required | 27–28"}}
    )


def test_cross_award_text_and_affirmative_guarantees_rejected():
    from nextstep.rag.construction import Claim, claim_boundary_error

    data = {
        "catalog_scope": [
            {"program_id": "a", "name": "Alabama Capstone"},
            {"program_id": "b", "name": "Auburn Heritage"},
        ]
    }
    claim = Claim(
        text="Alabama is automatic, Auburn depends on funding.",
        program_id="a",
        supports=[{"evidence_id": "x"}],
    )
    assert claim_boundary_error(claim, data)
    claim.text = "Alabama is guaranteed if your GPA qualifies."
    assert claim_boundary_error(claim, data)
    claim.text = "Alabama is automatic; this is not a guaranteed award for you."
    assert claim_boundary_error(claim, data) is None


def test_absence_of_information_is_a_gap_not_a_cited_fact():
    class MissingModel:
        def invoke(self, schema, instructions, data, max_output):
            assert "claims" not in data  # no review call for a gap-only answer
            return schema(
                claims=[
                    {
                        "text": "The evidence does not provide a bank routing number.",
                        "program_id": "p",
                        "supports": [{"evidence_id": "c"}],
                    }
                ]
            ), {}

    blocks, gaps, _, _ = construct(MissingModel(), payload())
    assert not blocks and "routing" in gaps[0]
