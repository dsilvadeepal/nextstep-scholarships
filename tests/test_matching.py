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


def test_explicit_non_georgia_resident_is_unmet_only_for_georgia_rule():
    profile = StudentProfile(context={"georgia_resident": False})
    assert evaluate_condition(rule("state", "eq", "GA"), profile, TODAY).status == "unmet"
    assert evaluate_condition(rule("state", "eq", "AL"), profile, TODAY).status == "unknown"
    assert evaluate_condition(rule("state", "eq", "GA"), StudentProfile(), TODAY).status == "unknown"


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
    assert by_id["1"].fit == "Explore"
    assert "senior-year" in by_id["1"].fit_reason
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
    assert results["a"].fit == "Explore"
    assert "Club" in results["b"].followups[0]


def test_match_tiers_come_from_reviewed_rules():
    records = [
        Scholarship(
            id="strong",
            name="Strong",
            corpus_version="v",
            information_status="source_checked",
            conditions=[rule("grade", "eq", 12)],
        ),
        Scholarship(
            id="possible",
            name="Possible",
            corpus_version="v",
            information_status="source_checked",
            conditions=[
                rule("grade", "eq", 12),
                rule("citizenship", "eq", "US citizen"),
            ],
        ),
        Scholarship(
            id="explore",
            name="Explore",
            corpus_version="v",
            information_status="source_checked",
        ),
        Scholarship(
            id="unmet",
            name="Unmet",
            corpus_version="v",
            information_status="source_checked",
            conditions=[rule("grade", "eq", 11)],
        ),
    ]
    results = {
        result.scholarship_id: result
        for result in match_catalog(records, StudentProfile(grade=12), TODAY)
    }
    assert results["strong"].fit == "Strong match"
    assert results["possible"].fit == "Possible match"
    assert results["explore"].fit == "Explore"
    assert results["unmet"].fit == "Not currently eligible"
    assert results["strong"].sort_key < results["possible"].sort_key
    assert results["possible"].sort_key < results["explore"].sort_key


def test_unspecified_college_requirement_cannot_be_marked_unmet():
    profile = StudentProfile(context={'accepted_colleges':['UGA']})
    assert evaluate_condition(rule('college','accepted',None),profile,TODAY).status == 'unknown'
