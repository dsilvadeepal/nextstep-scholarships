from concurrent.futures import ThreadPoolExecutor

import pytest
from nextstep.db import metadata
from nextstep.evals.runner import EvalRunner
from sqlalchemy import create_engine


def test_expected_evidence_gap_does_not_require_invented_eligibility_rules():
    from nextstep.evals.score import Judgment, score_case
    from nextstep.models import (
        AnswerBlock,
        AnswerResult,
        EvalCase,
        RetrievedEvidence,
        StudentProfile,
    )

    case = EvalCase(
        id="missing-program",
        question="Clemson rules?",
        profile=StudentProfile(),
        frozen_date="2026-10-14",
        expects_evidence_gap=True,
    )
    judgment = Judgment(
        required_facts_addressed=False,
        responsive=False,
        no_contradiction=True,
        unknowns_preserved=True,
        reason="Rules unavailable; expected coverage gap preserved",
        claims=[],
    )
    answer = AnswerResult(
        blocks=[],
        gaps=["Clemson is not in this verified corpus."],
        corpus_version="v",
        method="semantic",
        evidence=RetrievedEvidence(chunks=[]),
    )
    assert score_case(case, answer, judgment)["passed"] is True
    # A factual answer substituted for a required gap must still fail.
    answer.blocks = [AnswerBlock(text="Another award's rules", evidence_ids=[])]
    assert score_case(case, answer, judgment)["passed"] is False
    answer.blocks = []
    answer.gaps = []
    assert score_case(case, answer, judgment)["passed"] is False


def test_rubric_only_edits_do_not_make_exposed_heldout_questions_fresh(tmp_path):
    r = runner(tmp_path)
    case = {
        "question": "Missing program rules?",
        "profile": {},
        "program_ids": [],
        "frozen_date": "2026-10-14",
    }
    config = {
        "corpus_version": "v",
        "cases": ["a"],
        "methods": ["semantic"],
        "split": "heldout",
        "suite_hash": "before",
        "case_snapshots": {"a": case},
    }
    run = r.start_run(config)
    r.cancel(run)
    edited = {
        **config,
        "suite_hash": "after",
        "case_snapshots": {"a": {**case, "expects_evidence_gap": True}},
    }
    with pytest.raises(ValueError, match="heldout"):
        r.start_run(edited)


def runner(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/evals.db")
    metadata.create_all(engine)
    return EvalRunner(engine)


def test_single_active_run_and_completed_case_idempotency(tmp_path):
    r = runner(tmp_path)

    def start(_):
        try:
            return r.start_run(
                {"corpus_version": "v", "cases": ["one"], "methods": ["semantic"]}
            )
        except ValueError:
            return None

    with ThreadPoolExecutor(2) as pool:
        ids = list(pool.map(start, range(2)))
    assert sum(i is not None for i in ids) == 1
    run = next(i for i in ids if i)
    output = r.execute_case(
        run, "one", "semantic", lambda: {"answer": "fixture"}, now=100
    )
    assert output == {"answer": "fixture"}

    def must_not_run():
        raise AssertionError("duplicate provider call")

    assert r.execute_case(run, "one", "semantic", must_not_run, now=102) == output


def test_expired_lease_requires_explicit_retry(tmp_path):
    r = runner(tmp_path)
    run = r.start_run(
        {"corpus_version": "v", "cases": ["one"], "methods": ["semantic"]}
    )
    r.claim(run, "one", "semantic", now=0)
    with pytest.raises(ValueError, match="ambiguous"):
        r.execute_case(run, "one", "semantic", dict, now=61)
    assert r.status(run)["results"][0]["status"] == "interrupted"


def test_unknown_case_or_method_cannot_join_run(tmp_path):
    r = runner(tmp_path)
    run = r.start_run(
        {"corpus_version": "v", "cases": ["one"], "methods": ["semantic"]}
    )
    with pytest.raises(ValueError):
        r.claim(run, "other", "semantic", now=0)
    with pytest.raises(ValueError):
        r.claim(run, "one", "hybrid", now=0)


def test_explicit_retry_only_incomplete_cases_and_cancel_preserves_results(tmp_path):
    r = runner(tmp_path)
    run = r.start_run(
        {"corpus_version": "v", "cases": ["one", "two"], "methods": ["semantic"]}
    )
    r.execute_case(run, "one", "semantic", lambda: {"value": 1}, now=100)
    r.claim(run, "two", "semantic", now=100)
    with pytest.raises(ValueError):
        r.retry_case(run, "two", "semantic", acknowledge_cost=False, now=161)
    r.retry_case(run, "two", "semantic", acknowledge_cost=True, now=161)
    r.execute_case(run, "two", "semantic", lambda: {"value": 2}, now=162)
    assert r.status(run)["status"] == "completed"
    with pytest.raises(ValueError):
        r.retry_case(run, "one", "semantic", acknowledge_cost=True, now=200)


def test_score_errors_are_failures_and_no_claims_are_na():
    from nextstep.evals.score import score_case
    from nextstep.models import (
        AnswerResult,
        EvalCase,
        RetrievedEvidence,
        StudentProfile,
    )

    case = EvalCase(
        id="gap",
        profile=StudentProfile(),
        question="Unknown?",
        frozen_date="2026-10-14",
    )
    answer = AnswerResult(
        blocks=[],
        gaps=["No evidence"],
        corpus_version="v",
        method="semantic",
        evidence=RetrievedEvidence(chunks=[]),
    )
    score = score_case(case, answer, None)
    assert score["support_rate"] is None
    assert score["passed"] is False
    assert score["judge_error"] is not None


def test_cancel_prevents_late_result_and_new_claim(tmp_path):
    r = runner(tmp_path)
    run = r.start_run(
        {"corpus_version": "v", "cases": ["one", "two"], "methods": ["semantic"]}
    )
    r.execute_case(run, "one", "semantic", lambda: {"value": 1}, now=100)

    def cancel_during_call():
        r.cancel(run)
        return {"late": True}

    with pytest.raises(ValueError, match="lease"):
        r.execute_case(run, "two", "semantic", cancel_during_call, now=101)
    state = r.status(run)
    assert state["status"] == "cancelled"
    assert state["results"][0]["result"] == {"value": 1}
    assert state["results"][1]["status"] == "interrupted"
    with pytest.raises(ValueError):
        r.claim(run, "two", "semantic", now=102)


def test_score_missing_conditions_and_unscorable_claims_fail():
    from nextstep.evals.score import ClaimAssessment, Judgment, score_case
    from nextstep.models import (
        AnswerBlock,
        AnswerResult,
        EvalCase,
        RetrievedEvidence,
        StudentProfile,
    )

    case = EvalCase(
        id="rule",
        profile=StudentProfile(),
        question="Rule?",
        frozen_date="2026-10-14",
        expected_conditions={"grade": "unknown"},
    )
    answer = AnswerResult(
        blocks=[AnswerBlock(text="Invented", evidence_ids=[])],
        corpus_version="v",
        method="semantic",
        evidence=RetrievedEvidence(chunks=[]),
    )
    judge = Judgment(
        required_facts_addressed=True,
        no_contradiction=True,
        unknowns_preserved=True,
        responsive=True,
        reason="fixture",
        claims=[
            ClaimAssessment(
                text="Invented", supported=True, scorable=False, reason="missing source"
            )
        ],
    )
    score = score_case(case, answer, judge)
    assert score["passed"] is False and score["support_rate"] == 0
    assert score["condition_pass"] is False and score["citation_pass"] is False


def test_summary_counts_errors_and_pending_in_denominator():
    from nextstep.evals.score import summarize_run

    run = {
        "config": {
            "cases": ["a", "b"],
            "methods": ["semantic"],
            "case_snapshots": {"a": {"critical": True}, "b": {"critical": False}},
        },
        "results": [
            {
                "case_id": "a",
                "method": "semantic",
                "status": "completed",
                "result": {
                    "scores": {
                        "passed": True,
                        "checked_claims": 0,
                        "supported_claims": 0,
                        "evidence_found": 0,
                        "evidence_required": 0,
                        "citation_pass": True,
                    },
                    "answer": {"timings": {"answer_seconds": 2}},
                },
            }
        ],
    }
    metrics = summarize_run(run)["semantic"]
    assert metrics["answer_pass_rate"] == 0.5
    assert metrics["support_rate"] is None
    assert metrics["completion_rate"] == 0.5
    assert metrics["release_gate_passed"] is False


def test_finished_result_is_saved_after_lease_expiry_unless_attempt_was_replaced(
    tmp_path, monkeypatch
):
    r = runner(tmp_path)
    run = r.start_run({"corpus_version": "v", "cases": ["a"], "methods": ["semantic"]})
    monkeypatch.setattr("nextstep.evals.runner.time.time", lambda: 100)

    def slow():
        monkeypatch.setattr("nextstep.evals.runner.time.time", lambda: 500)
        return {"saved": "paid result"}

    assert r.execute_case(run, "a", "semantic", slow) == {"saved": "paid result"}
    assert r.status(run)["status"] == "completed"


def test_execution_settings_cannot_drift_and_expected_sources_do_not_filter():
    from nextstep.config import Settings
    from nextstep.evals.service import case_request, validate_configuration
    from nextstep.evals.suite import load_suite, snapshot

    s = Settings(_env_file=None)
    config = snapshot(s, "v", "tuning")
    validate_configuration(s, config)
    with pytest.raises(ValueError):
        validate_configuration(
            s.model_copy(update={"embedding_dimensions": 12}), config
        )
    with pytest.raises(ValueError):
        validate_configuration(
            s.model_copy(update={"input_usd_per_million": 1}), config
        )
    weighted = snapshot(s, "v", "tuning", ["hybrid_60_40"])
    assert weighted["retrieval_weights"] == {"hybrid_60_40": [0.6, 0.4]}
    validate_configuration(s, weighted)
    with pytest.raises(ValueError, match="Retrieval weights"):
        validate_configuration(
            s, {**weighted, "retrieval_weights": {"hybrid_60_40": [0.7, 0.3]}}
        )
    case = load_suite()[0][0].model_copy(update={"program_ids": []})
    assert case.checked_sources
    assert case_request(case, "v", "semantic").program_ids == []


def test_optional_trace_failure_happens_after_result_is_durable(tmp_path):
    r = runner(tmp_path)
    run = r.start_run({"corpus_version": "v", "cases": ["a"], "methods": ["semantic"]})

    def trace(result):
        assert r.status(run)["results"][0]["result"]["value"] == 1
        raise TimeoutError("trace unavailable")

    result = r.execute_case(
        run, "a", "semantic", lambda: {"value": 1}, after_save=trace
    )
    assert (
        result["value"] == 1 and result["trace_status"] == "upload_failed:TimeoutError"
    )
    assert r.status(run)["results"][0]["status"] == "completed"


def test_heldout_exposure_guard_is_transactional(tmp_path):
    r = runner(tmp_path)
    config = {
        "corpus_version": "v",
        "cases": ["a"],
        "methods": ["semantic"],
        "split": "heldout",
        "suite_hash": "fixed",
    }
    run = r.start_run(config)
    r.execute_case(run, "a", "semantic", lambda: {"done": True})
    with pytest.raises(ValueError, match="heldout"):
        r.start_run(config)
