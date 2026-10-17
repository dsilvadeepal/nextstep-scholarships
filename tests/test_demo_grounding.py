from nextstep.models import (
    ChatTurn,
    Chunk,
    RetrievalRequest,
    RetrievedEvidence,
    Scholarship,
    StudentProfile,
)
from nextstep.rag.answer import AnswerService
from nextstep.rag.construction import Claim, claim_boundary_error
from nextstep.rag.scope import scope_chunk


def test_junior_cannot_be_assigned_published_cycle_as_personal_deadline():
    claim = Claim(
        text="As a junior interested in Fall 2027 entry, you should apply by October 15, 2026.",
        program_id="tech",
        supports=[{"evidence_id": "c"}],
    )
    assert claim_boundary_error(claim, {"profile": {"grade": 11}})
    claim.text = "The published Fall 2027 cycle has an October 15, 2026 deadline; these are not your future application dates."
    assert claim_boundary_error(claim, {"profile": {"grade": 11}}) is None


def test_unweighted_gpa_and_unknown_enrollment_are_not_confirmed_by_model():
    claim = Claim(
        text="Your 3.7 unweighted GPA meets the minimum GPA, but Auburn may recalculate it.",
        program_id="p",
        supports=[{"evidence_id": "c"}],
    )
    data = {
        "profile": {"gpa": {"type": "unweighted"}},
        "evidence": [{"id": "c", "text": "Auburn will recalculate GPA."}],
    }
    assert "unweighted" in claim_boundary_error(claim, data)
    claim.text = (
        "As a senior planning full-time enrollment, you meet basic eligibility."
    )
    assert "enrollment" in claim_boundary_error(claim, data)
    claim.text = "Prepare a transcript and check the university GPA calculation."
    assert claim_boundary_error(claim, data) is None


def test_missing_app_scores_do_not_prove_incomplete_admission_file():
    claim = Claim(
        text="Without submitting official ACT scores, your application file is incomplete.",
        program_id="p",
        supports=[{"evidence_id": "c"}],
    )
    assert "provided test scores here" in claim_boundary_error(
        claim,
        {
            "question": "I haven’t provided SAT or ACT scores. How does that affect Auburn?"
        },
    )


def chunk(text, heading="Eligibility"):
    return Chunk(
        id="c",
        program_id="burger-king-general",
        source_id="s",
        corpus_version="v",
        text=text,
        heading="Burger King — " + heading,
        section_ids=["s"],
        token_count=100,
    )


def test_general_track_excludes_employee_rules_without_rewriting_source():
    original = chunk(
        "Eligibility\nBURGER KING\n®\nGeneral Track\nGPA 2.0 on 4.0.\nBURGER KING\n®\nEmployee-Based Track\nEmployee required."
    )
    scoped = scope_chunk(original)
    assert "GPA 2.0" in scoped.text and "Employee" not in scoped.text
    assert scoped.text in original.text
    assert "Employee" in original.text


def test_special_award_and_employee_continuations_cannot_supply_general_rules():
    assert (
        scope_chunk(
            chunk(
                "James W. McLamore WHOPPER Scholarship\nGeneral Track applicants selected with GPA 3.5",
                "Selection of Recipients",
            )
        )
        is None
    )
    assert scope_chunk(chunk("GPA 2.0. Employees and spouses may apply.")) is None
    selection = scope_chunk(
        chunk(
            "Selection of Recipients\nGeneral Track for high school seniors: academic record 33%.\nEmployee-Based Track: employee rules",
            "Selection of Recipients",
        )
    )
    assert "33%" in selection.text and "employee rules" not in selection.text


def test_focused_followup_does_not_retrieve_prior_comparison_award():
    class Retrieval:
        def retrieve(self, request):
            assert request.program_ids == ["auburn-charter"]
            assert (
                request.question
                == "I haven't provided SAT or ACT scores. What can you conclude about Auburn?"
            )
            return RetrievedEvidence(chunks=[])

    records = [
        Scholarship(id=i, name=n, corpus_version="v")
        for i, n in [
            ("auburn-charter", "Auburn Academic Charter"),
            ("burger-king-general", "Burger King General Track"),
        ]
    ]
    result = AnswerService(Retrieval(), None, records).answer_question(
        StudentProfile(grade=12),
        RetrievalRequest(
            question="I haven't provided SAT or ACT scores. What can you conclude about Auburn?",
            program_ids=[r.id for r in records],
            corpus_version="v",
        ),
        [ChatTurn(role="user", content="Compare my two saved scholarships.")],
    )
    assert not any("burger" in gap for gap in result.gaps)
