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
    quote = "Only juniors may apply."
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
                    "supports": [{"evidence_id": "c", "quote": self.quote}],
                }
            ]
        ), {"input_tokens": 20, "output_tokens": 8}


def test_whole_faq_and_supported_synthesis_with_usage():
    blocks, gaps, usage, review = construct(Model(), payload())
    assert blocks[0].kind == "explanation"
    assert blocks[0].supporting_quotes == ["Only juniors may apply."]
    assert not gaps and review["accepted"] == 1
    assert usage["input_tokens"] == 30 and usage["output_tokens"] == 13


@pytest.mark.parametrize(
    "field,value", [("quote", "Seniors are eligible."), ("program", "another-award")]
)
def test_fabricated_quote_or_cross_award_citation_withheld(field, value):
    model = Model()
    setattr(model, field, value)
    blocks, gaps, _, review = construct(model, payload())
    assert not blocks and gaps and review["accepted"] == 0


def test_review_rejection_is_withheld_without_retry():
    model = Model()
    model.supported = False
    blocks, gaps, _, review = construct(model, payload())
    assert not blocks and "unsupported" in gaps[0]
    assert review["accepted"] == 0


def test_incomplete_review_fails_closed():
    model = Model()
    model.incomplete_review = True
    with pytest.raises(ValueError, match="every claim"):
        construct(model, payload())


def test_whitespace_normalization_preserves_source_without_changing_facts():
    from nextstep.rag.construction import exact_quote

    source = "Application due\nDecember 1, 2026 at 5:00 PM\nPacific Time."
    assert (
        exact_quote(source, "due December 1, 2026 at 5:00 PM Pacific Time.")
        == source[12:]
    )
    assert exact_quote(source, "due December 2, 2026") is None
    assert exact_quote("not eligible", "eligible for all awards") is None
