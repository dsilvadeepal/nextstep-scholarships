from datetime import date

import pytest
from nextstep.matching import evaluate_condition, match_catalog
from nextstep.models import Condition, Scholarship, StudentProfile

TODAY = date(2026, 10, 14)


def rule(kind="gpa", operator="gte", value=None, **kwargs):
    return Condition(id="rule", kind=kind, operator=operator, value=value, **kwargs)


@pytest.mark.parametrize(
    "profile",
    [
        {},
        {"gpa": {"value": 3.8}},
        {"gpa": {"value": 3.8, "scale": 4, "type": "weighted"}},
    ],
)
def test_gpa_missing_or_incompatible_is_unknown(profile):
    assert (
        evaluate_condition(
            rule(value={"value": 3.5, "scale": 4, "type": "unweighted"}),
            StudentProfile(**profile),
            TODAY,
        ).status
        == "unknown"
    )


def test_prospective_is_not_admission():
    p = StudentProfile(prospective_colleges=["UGA"])
    assert (
        evaluate_condition(rule("college", "enrolled", "UGA"), p, TODAY).status
        == "unknown"
    )


@pytest.mark.parametrize(
    "operator,children,want",
    [
        ("and", [("grade", "eq", 12), ("membership", "eq", "Club")], "unknown"),
        ("or", [("grade", "eq", 12), ("membership", "eq", "Club")], "met"),
        ("not", [("membership", "eq", "Club")], "unknown"),
    ],
)
def test_groups(operator, children, want):
    c = rule("group", operator, children=[rule(k, o, v) for k, o, v in children])
    assert evaluate_condition(c, StudentProfile(grade=12), TODAY).status == want


def test_unsupported_is_unknown():
    assert (
        evaluate_condition(rule("gpa", "magic", 4), StudentProfile(), TODAY).status
        == "unknown"
    )


def test_full_catalog_closed_and_junior_groups():
    records = [
        Scholarship(
            id=str(i),
            name=f"Award {i}",
            corpus_version="v",
            information_status="automatically_extracted",
        )
        for i in range(12)
    ]
    records[0].deadline = date(2026, 1, 1)
    records[1].conditions = [rule("grade", "eq", 12)]
    results = match_catalog(
        records, StudentProfile(grade=11, interests=["science"]), TODAY
    )
    by_id = {r.scholarship_id: r for r in results}
    assert len(results) == 12  # Matching is independent of any top-8 retrieval.
    assert by_id["0"].timing == "closed"
    assert by_id["1"].group == "prepare"
    assert "conditional" in by_id["1"].fit.lower()
    assert by_id["11"].group == "matches"


def test_incomplete_and_unknown_followup():
    records = [
        Scholarship(id="a", name="A", corpus_version="v"),
        Scholarship(
            id="b",
            name="B",
            corpus_version="v",
            information_status="automatically_extracted",
            conditions=[rule("membership", "eq", "Club")],
        ),
    ]
    results = {
        r.scholarship_id: r for r in match_catalog(records, StudentProfile(), TODAY)
    }
    assert results["a"].group == "explore"
    assert "Club" in results["b"].followups[0]
