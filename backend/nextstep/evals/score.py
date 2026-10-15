"""Separate deterministic evidence/condition checks from correlated automated judgment."""

from pydantic import BaseModel, Field


class ClaimAssessment(BaseModel):
    text: str
    supported: bool
    scorable: bool
    reason: str


class Judgment(BaseModel):
    required_facts_addressed: bool
    no_contradiction: bool
    unknowns_preserved: bool
    responsive: bool
    reason: str
    claims: list[ClaimAssessment] = Field(default_factory=list)


def score_case(case, answer, judgment, actual_conditions=None):
    evidence_ids = {
        i for c in answer.evidence.chunks for i in [c.id, *[e.id for e in c.evidence]]
    }
    cited = [i for b in answer.blocks for i in b.evidence_ids]
    required = set(case.expected_evidence)
    found = required & evidence_ids
    conditions = actual_conditions or {}
    condition_ok = all(
        conditions.get(k) == v for k, v in case.expected_conditions.items()
    )
    citation_ok = all(
        b.evidence_ids and set(b.evidence_ids) <= evidence_ids for b in answer.blocks
    )
    claims = judgment.claims if judgment else []
    supported = sum(c.supported and c.scorable for c in claims)
    checked = len(claims)
    rubric = bool(
        judgment
        and all(
            [
                judgment.required_facts_addressed,
                judgment.no_contradiction,
                judgment.unknowns_preserved,
                judgment.responsive,
            ]
        )
    )
    expected_gap_pass = None
    if case.expects_evidence_gap:
        # A checked expectation of missing evidence must not reward invented facts.
        # Contradiction/unknown and claim-support checks still apply to gap text.
        expected_gap_pass = bool(
            judgment
            and judgment.no_contradiction
            and judgment.unknowns_preserved
            and not answer.blocks
            and answer.gaps
            and not required
        )
        rubric = expected_gap_pass
    # A judge omitting claims from a factual answer cannot manufacture N/A or a pass.
    claim_coverage = not answer.blocks or checked > 0
    return {
        "passed": bool(
            rubric
            and condition_ok
            and citation_ok
            and required <= evidence_ids
            and claim_coverage
            and supported == checked
        ),
        "condition_pass": condition_ok,
        "expected_gap_pass": expected_gap_pass,
        "citation_resolution": sum(i in evidence_ids for i in cited) / len(cited)
        if cited
        else None,
        "citation_pass": citation_ok,
        "evidence_found": len(found),
        "evidence_required": len(required),
        "evidence_recall": len(found) / len(required) if required else None,
        "supported_claims": supported,
        "checked_claims": checked,
        "unscorable_claims": sum(not c.scorable for c in claims),
        "support_rate": supported / checked if checked else None,
        "judge_error": None if judgment else "Judge unavailable; case fails",
        "judge": judgment.model_dump() if judgment else None,
        "assessment_label": "Correlated automated assessment; source spot-check still required",
    }


def summarize_run(run):
    import math

    output = {}
    for method in run["config"]["methods"]:
        total = len(run["config"]["cases"])
        rows = [r for r in run["results"] if r["method"] == method]
        done = [
            r
            for r in rows
            if r["status"] == "completed" and (r.get("result") or {}).get("answer")
        ]
        scores = [(r.get("result") or {}).get("scores", {}) for r in rows]
        passed = sum(s.get("passed") is True for s in scores)
        checked = sum(s.get("checked_claims", 0) for s in scores)
        supported = sum(s.get("supported_claims", 0) for s in scores)
        required = sum(s.get("evidence_required", 0) for s in scores)
        found = sum(s.get("evidence_found", 0) for s in scores)
        times = sorted(
            r["result"]["answer"].get("timings", {}).get("answer_seconds", float("inf"))
            for r in done
        )
        critical = [
            id
            for id, case in run["config"].get("case_snapshots", {}).items()
            if case["critical"]
        ]
        critical_pass = all(
            any(
                r["case_id"] == id
                and (r.get("result") or {}).get("scores", {}).get("passed") is True
                for r in rows
            )
            for id in critical
        )
        support = supported / checked if checked else None
        recall = found / required if required else None
        citations = (
            all(s.get("citation_pass") is True for s in scores) and len(scores) == total
        )
        completion = len(done) / total if total else 0
        p95 = times[math.ceil(0.95 * len(times)) - 1] if times else None
        if p95 is not None and not math.isfinite(p95):
            p95 = None
        output[method] = {
            "total_cases": total,
            "passed_cases": passed,
            "answer_pass_rate": passed / total if total else None,
            "completion_rate": completion,
            "completed_answers": len(done),
            "completed_answer_p95_seconds": p95,
            "within_15_seconds_rate": sum(t <= 15 for t in times) / total
            if total
            else None,
            "checked_claims": checked,
            "supported_claims": supported,
            "support_rate": support,
            "evidence_required": required,
            "evidence_found": found,
            "evidence_recall": recall,
            "all_critical_pass": critical_pass,
            "all_citations_resolve": citations,
            "release_gate_passed": bool(
                total
                and completion == 1
                and critical_pass
                and passed / total >= 0.9
                and support is not None
                and support >= 0.95
                and recall is not None
                and recall >= 0.9
                and citations
                and sum(t <= 15 for t in times) / total >= 0.95
            ),
        }
    return output
