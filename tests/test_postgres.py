import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest
from nextstep.db import metadata
from nextstep.limits import BudgetLedger
from nextstep.models import Scholarship
from nextstep.repository import Repository
from sqlalchemy import create_engine, text


@pytest.mark.postgres
def test_postgres_isolated_schema_transactions_and_jsonb():
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set TEST_POSTGRES_URL for isolated PostgreSQL integration")
    schema = "nextstep_test_" + uuid.uuid4().hex
    root = create_engine(url)
    with root.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        metadata.create_all(engine)
        repo = Repository(engine)
        repo.stage_catalog(
            "v", [Scholarship(id="s", name="Source", corpus_version="v")]
        )
        assert repo.list_scholarships("v")[0].name == "Source"
        budget = BudgetLedger(engine, Decimal(1), Decimal(1), enabled=True)

        def reserve(n):
            try:
                budget.reserve_budget(str(n), Decimal(".6"))
                return True
            except ValueError:
                return False

        with ThreadPoolExecutor(2) as pool:
            assert sum(pool.map(reserve, range(2))) == 1
        with engine.connect() as conn:
            assert (
                conn.execute(
                    text(
                        "SELECT data_type FROM information_schema.columns WHERE table_schema=:s AND table_name='scholarships' AND column_name='data'"
                    ),
                    {"s": schema},
                ).scalar_one()
                == "jsonb"
            )
    finally:
        engine.dispose()
        with root.begin() as conn:
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        root.dispose()


@pytest.mark.postgres
def test_postgres_eval_browser_resume_and_concurrent_start():
    from nextstep.evals.runner import EvalRunner

    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set TEST_POSTGRES_URL")
    schema = "nextstep_eval_" + uuid.uuid4().hex
    root = create_engine(url)
    with root.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        metadata.create_all(engine)
        config = {
            "corpus_version": "fixture",
            "cases": ["a", "b"],
            "methods": ["semantic"],
        }

        def start(_):
            try:
                return EvalRunner(engine).start_run(config)
            except ValueError:
                return None

        with ThreadPoolExecutor(2) as pool:
            ids = list(pool.map(start, range(2)))
        assert sum(x is not None for x in ids) == 1
        run = next(x for x in ids if x)
        EvalRunner(engine).execute_case(
            run, "a", "semantic", lambda: {"value": "durable"}
        )
        resumed = EvalRunner(engine)

        def forbidden():
            raise AssertionError("completed case replayed")

        assert resumed.execute_case(run, "a", "semantic", forbidden) == {
            "value": "durable"
        }
        resumed.execute_case(run, "b", "semantic", lambda: {"value": "remaining"})
        assert resumed.status(run)["status"] == "completed"
    finally:
        engine.dispose()
        with root.begin() as conn:
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        root.dispose()
