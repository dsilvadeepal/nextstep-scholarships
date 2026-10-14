from concurrent.futures import ThreadPoolExecutor

import pytest
from nextstep.db import metadata
from nextstep.evals.runner import EvalRunner
from sqlalchemy import create_engine


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
