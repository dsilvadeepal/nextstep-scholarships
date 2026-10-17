from nextstep.models import Chunk, RetrievedEvidence, Scholarship
from nextstep.rag.comparisons import score_comparisons


def evidence(text, heading="Example Heritage Scholarship — Heritage Scholarship"):
    return RetrievedEvidence(
        chunks=[
            Chunk(
                id="c",
                program_id="p",
                source_id="s",
                corpus_version="v",
                text=text,
                heading=heading,
                section_ids=["s"],
                token_count=20,
            )
        ]
    )


def test_negative_threshold_and_exact_program_citation():
    records = [
        Scholarship(id="p", name="Example Heritage Scholarship", corpus_version="v")
    ]
    result = score_comparisons(
        "My ACT superscore is 27.",
        evidence("Minimum GPA | 3.5\nACT Required* | 31–32"),
        records,
    )
    assert len(result) == 1 and "27 is below" in result[0].text
    assert result[0].evidence_ids == ["c"]
    assert not score_comparisons(
        "My ACT superscore is 31.", evidence("ACT Required | 31–32"), records
    )
    assert not score_comparisons(
        "My ACT superscore is 27, ACT score is 32.",
        evidence("ACT Required | 31–32"),
        records,
    )


def test_score_equivalency_and_other_award_rows_are_not_thresholds():
    records = [
        Scholarship(id="p", name="Example Heritage Scholarship", corpus_version="v")
    ]
    assert not score_comparisons(
        "My ACT score is 27.", evidence("ACT | SAT\n31 | 1390–1410"), records
    )
    assert not score_comparisons(
        "My ACT score is 27.",
        evidence("Scholarship | ACT\nOther Award | 31–32"),
        records,
    )
    result = score_comparisons(
        "My ACT score is 27.",
        evidence("Scholarship | ACT\nHeritage Scholarship | 31–32"),
        records,
    )
    assert result


def test_automatic_consideration_is_not_an_automatic_award():
    from nextstep.rag.comparisons import award_classification

    records = [
        Scholarship(id="p", name="Example Heritage Scholarship", corpus_version="v")
    ]
    assert not award_classification(
        "Is it guaranteed?",
        evidence("Automatic consideration is based on GPA."),
        records,
    )
    result = award_classification(
        "Is it guaranteed?",
        evidence(
            "Automatic merit scholarships are awarded based on standardized test scores and GPA."
        ),
        records,
    )
    assert result and "does not confirm an award" in result[0].text
    assert not award_classification(
        "If I miss the priority deadline, is there no possibility of automatic merit?",
        evidence("Automatic merit scholarships are awarded based on scores and GPA."),
        records,
    )


def test_reviewed_conflict_explanation_requires_both_retrieved_source_variants():
    from nextstep.models import Chunk, RetrievedEvidence, Scholarship
    from nextstep.rag.comparisons import reviewed_conflict_explanations

    record = Scholarship(
        id="cooke",
        name="Cooke",
        corpus_version="v",
        information_status="conflicting",
        conflicts={
            "transcript_requirement": [
                "How-to-apply: unofficial transcript",
                "FAQ: official transcript via counselor",
            ],
            "income_measure": ["annual gross income", "adjusted gross income"],
        },
    )
    chunks = [
        Chunk(
            id="apply",
            program_id="cooke",
            corpus_version="v",
            source_id="application",
            text="Submit an unofficial transcript. Annual gross income must be below the published limit.",
            heading="How to apply",
            section_ids=["s1"],
            token_count=20,
        ),
        Chunk(
            id="faq",
            program_id="cooke",
            corpus_version="v",
            source_id="faq",
            text="Counselors submit an official transcript. Adjusted gross income is used.",
            heading="FAQ",
            section_ids=["s2"],
            token_count=20,
        ),
    ]
    result = reviewed_conflict_explanations(
        "Official or unofficial transcript? Is income AGI?",
        RetrievedEvidence(chunks=chunks),
        [record],
    )
    assert len(result) == 2
    assert all(set(block.evidence_ids) == {"apply", "faq"} for block in result)
    assert all(
        "distinction" in block.text.lower() and "sponsor" in block.text.lower()
        for block in result
    )
    assert not reviewed_conflict_explanations(
        "Official or unofficial transcript?",
        RetrievedEvidence(chunks=chunks[:1]),
        [record],
    )
    assert not reviewed_conflict_explanations(
        "What is the deadline?", RetrievedEvidence(chunks=chunks), [record]
    )
