"""Transactional, request-driven evaluation execution; never automatically retry paid work."""

import time
import uuid

from nextstep.db import eval_results, eval_runs, serialized
from sqlalchemy import and_, insert, select, update


def key_for(run_id, case_id, method):
    return and_(
        eval_results.c.run_id == run_id,
        eval_results.c.case_id == case_id,
        eval_results.c.method == method,
    )


class EvalRunner:
    def __init__(self, engine):
        self.engine = engine

    def start_run(self, config):
        if not all(config.get(k) for k in ("corpus_version", "cases", "methods")):
            raise ValueError("Immutable corpus, cases and methods required")
        if any(len(config[k]) != len(set(config[k])) for k in ("cases", "methods")):
            raise ValueError("Duplicate cases/methods")
        with serialized(self.engine) as conn:
            if config.get("split") == "heldout" and any(
                old.get("split") == "heldout"
                and old.get("suite_hash") == config.get("suite_hash")
                for old in conn.execute(select(eval_runs.c.config)).scalars()
            ):
                raise ValueError(
                    "This heldout suite has already been opened; resume its saved run"
                )
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
        return self._claim(run_id, case_id, method, now)[0]

    def _claim(self, run_id, case_id, method, now=None):
        now = time.time() if now is None else now
        key = key_for(run_id, case_id, method)
        failure, stored, token = None, None, str(uuid.uuid4())
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
            if row and row["status"] == "completed":
                return row["result"], None
            if run["status"] != "active":
                raise ValueError("Run is not active")
            if row and row["status"] != "pending":
                if row["status"] == "running" and row["lease_until"] > now:
                    failure = "Case is already running"
                else:
                    conn.execute(
                        update(eval_results)
                        .where(key)
                        .values(status="interrupted", lease_token=None)
                    )
                    failure = (
                        "Interrupted case has ambiguous cost; explicit retry required"
                    )
            elif row:
                conn.execute(
                    update(eval_results)
                    .where(key)
                    .values(status="running", lease_until=now + 60, lease_token=token)
                )
            else:
                conn.execute(
                    insert(eval_results).values(
                        run_id=run_id,
                        case_id=case_id,
                        method=method,
                        status="running",
                        lease_until=now + 60,
                        lease_token=token,
                        attempts=[],
                    )
                )
        if failure:
            raise ValueError(failure)
        return stored, token

    def execute_case(self, run_id, case_id, method, execute, now=None, after_save=None):
        stored, token = self._claim(run_id, case_id, method, now)
        if stored is not None:
            return stored
        try:
            result, status = execute(), "completed"
        except Exception as exc:  # noqa: BLE001 - persist only sanitized exception category
            result, status = {"error": type(exc).__name__}, "error"
        with serialized(self.engine) as conn:
            updated = conn.execute(
                update(eval_results)
                .where(
                    key_for(run_id, case_id, method),
                    eval_results.c.lease_token == token,
                    eval_results.c.status == "running",
                )
                .values(status=status, result=result, lease_token=None)
            )
            if updated.rowcount != 1:
                raise ValueError(
                    "Case lease lost; result cannot replace a newer attempt"
                )
            config = conn.execute(
                select(eval_runs.c.config).where(eval_runs.c.id == run_id)
            ).scalar_one()
            statuses = (
                conn.execute(
                    select(eval_results.c.status).where(eval_results.c.run_id == run_id)
                )
                .scalars()
                .all()
            )
            if len(statuses) == len(config["cases"]) * len(config["methods"]) and all(
                s == "completed" for s in statuses
            ):
                conn.execute(
                    update(eval_runs)
                    .where(eval_runs.c.id == run_id, eval_runs.c.status == "active")
                    .values(status="completed")
                )
        if after_save and status == "completed":
            try:
                result.update(after_save(result) or {})
            except Exception as exc:  # noqa: BLE001 - trace failure never discards durable paid work
                result["trace_status"] = "upload_failed:" + type(exc).__name__
            with serialized(self.engine) as conn:
                conn.execute(
                    update(eval_results)
                    .where(
                        key_for(run_id, case_id, method),
                        eval_results.c.status == "completed",
                    )
                    .values(result=result)
                )
        return result

    def retry_case(self, run_id, case_id, method, acknowledge_cost=False, now=None):
        if not acknowledge_cost:
            raise ValueError(
                "Acknowledge possible duplicate provider cost before retry"
            )
        now = time.time() if now is None else now
        key = key_for(run_id, case_id, method)
        with serialized(self.engine) as conn:
            conn.execute(
                select(eval_runs).where(eval_runs.c.id == run_id)
            ).mappings().one()
            row = conn.execute(select(eval_results).where(key)).mappings().one()
            if row["status"] in ("completed", "pending") or (
                row["status"] == "running" and row["lease_until"] > now
            ):
                raise ValueError("Only interrupted or failed attempts can be retried")
            if conn.execute(
                select(eval_runs.c.id).where(
                    eval_runs.c.status == "active", eval_runs.c.id != run_id
                )
            ).first():
                raise ValueError("Another run is active")
            attempts = [
                *(row["attempts"] or []),
                {
                    "status": row["status"],
                    "result": row["result"],
                    "retry_acknowledged_at": now,
                },
            ]
            conn.execute(
                update(eval_results)
                .where(key)
                .values(
                    status="pending",
                    lease_token=None,
                    lease_until=None,
                    result=None,
                    attempts=attempts,
                )
            )
            conn.execute(
                update(eval_runs)
                .where(eval_runs.c.id == run_id)
                .values(status="active")
            )

    def cancel(self, run_id):
        with serialized(self.engine) as conn:
            conn.execute(
                update(eval_runs)
                .where(eval_runs.c.id == run_id, eval_runs.c.status == "active")
                .values(status="cancelled")
            )
            conn.execute(
                update(eval_results)
                .where(
                    eval_results.c.run_id == run_id,
                    eval_results.c.status.in_(["running", "pending"]),
                )
                .values(status="interrupted", lease_token=None)
            )

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
        # Expose expired work without pretending that it is still running. Claim/retry perform transactional changes.
        for row in run["results"]:
            if row["status"] == "running" and row["lease_until"] < time.time():
                row["status"] = "interrupted"
        return run

    def list_runs(self):
        with self.engine.connect() as conn:
            return [dict(r) for r in conn.execute(select(eval_runs)).mappings()]
