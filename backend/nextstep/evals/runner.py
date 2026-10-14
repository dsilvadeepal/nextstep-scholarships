import time
import uuid
from sqlalchemy import select, insert, update, and_
from nextstep.db import eval_runs, eval_results, serialized


class EvalRunner:
    def __init__(self, engine):
        self.engine = engine

    def start_run(self, config):
        if (
            not config.get("corpus_version")
            or not config.get("cases")
            or not config.get("methods")
        ):
            raise ValueError("Immutable corpus, cases and methods required")
        with serialized(self.engine) as conn:
            if conn.execute(
                select(eval_runs.c.id).where(eval_runs.c.status == "active")
            ).first():
                raise ValueError("An evaluation run is already active")
            run_id = str(uuid.uuid4())
            conn.execute(
                insert(eval_runs).values(id=run_id, status="active", config=config)
            )
            return run_id

    def claim(self, run_id, case_id, method, now=None):
        now = time.time() if now is None else now
        key = and_(
            eval_results.c.run_id == run_id,
            eval_results.c.case_id == case_id,
            eval_results.c.method == method,
        )
        failure = None
        stored = None
        with serialized(self.engine) as conn:
            run = (
                conn.execute(select(eval_runs).where(eval_runs.c.id == run_id))
                .mappings()
                .one()
            )
            if (
                case_id not in run["config"]["cases"]
                or method not in run["config"]["methods"]
            ):
                raise ValueError("Case/method is outside immutable configuration")
            row = conn.execute(select(eval_results).where(key)).mappings().first()
            if row:
                if row["status"] == "completed":
                    stored = row["result"]
                elif row["status"] == "running" and row["lease_until"] > now:
                    failure = "Case is already running"
                else:
                    conn.execute(
                        update(eval_results).where(key).values(status="interrupted")
                    )
                    failure = (
                        "Interrupted case has ambiguous cost; explicit retry required"
                    )
            else:
                conn.execute(
                    insert(eval_results).values(
                        run_id=run_id,
                        case_id=case_id,
                        method=method,
                        status="running",
                        lease_until=now + 60,
                    )
                )
        if failure:
            raise ValueError(failure)
        return stored

    def execute_case(self, run_id, case_id, method, execute, now=None):
        stored = self.claim(run_id, case_id, method, now)
        if stored is not None:
            return stored
        key = and_(
            eval_results.c.run_id == run_id,
            eval_results.c.case_id == case_id,
            eval_results.c.method == method,
        )
        try:
            result = execute()
            status = "completed"
        except Exception as exc:
            result = {"error": type(exc).__name__}
            status = "error"
        with serialized(self.engine) as conn:
            conn.execute(
                update(eval_results).where(key).values(status=status, result=result)
            )
            config = conn.execute(
                select(eval_runs.c.config).where(eval_runs.c.id == run_id)
            ).scalar_one()
            rows = (
                conn.execute(
                    select(eval_results.c.status).where(eval_results.c.run_id == run_id)
                )
                .scalars()
                .all()
            )
            if len(rows) == len(config["cases"]) * len(config["methods"]) and all(
                s == "completed" for s in rows
            ):
                conn.execute(
                    update(eval_runs)
                    .where(eval_runs.c.id == run_id)
                    .values(status="completed")
                )
        return result

    def status(self, run_id):
        with self.engine.connect() as conn:
            run = dict(
                conn.execute(select(eval_runs).where(eval_runs.c.id == run_id))
                .mappings()
                .one()
            )
            run["results"] = [
                dict(r)
                for r in conn.execute(
                    select(eval_results).where(eval_results.c.run_id == run_id)
                ).mappings()
            ]
            return run
