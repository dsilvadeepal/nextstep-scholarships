from fastapi import APIRouter, Depends, HTTPException, Request
from nextstep.auth import require_admin
from nextstep.evals.runner import EvalRunner
from nextstep.evals.suite import RunRequest, load_suite, snapshot
from nextstep.models import Model
from sqlalchemy.exc import NoResultFound

router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])


def runner(request):
    repo = getattr(request.app.state, "repository", None)
    if repo is None:
        raise HTTPException(503, "Evaluation database not configured")
    return EvalRunner(repo.engine)


@router.get("/suite")
def suite():
    return {
        split: {"count": len(load_suite(split)[0]), "hash": load_suite(split)[1]}
        for split in ["tuning", "heldout"]
    }


@router.get("/runs")
def runs(request: Request):
    return runner(request).list_runs()


@router.post("/runs")
def start(payload: RunRequest, request: Request):
    if not getattr(request.app.state, "eval_execute", None):
        raise HTTPException(
            503, "Live evaluation access and approved budget are not configured"
        )
    repo = request.app.state.repository
    version = repo.active_version()
    if not version:
        raise HTTPException(503, "No published corpus")
    config = snapshot(request.app.state.settings, version, payload.split)
    r = runner(request)
    if payload.split == "heldout" and any(
        x["config"].get("split") == "heldout"
        and x["config"].get("suite_hash") == config["suite_hash"]
        for x in r.list_runs()
    ):
        raise HTTPException(
            409,
            "This heldout suite has already been opened. Resume that run; create a fresh suite before claiming a new heldout result.",
        )
    try:
        return {"id": r.start_run(config)}
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from None


@router.get("/runs/{run_id}")
def status(run_id: str, request: Request):
    try:
        state = runner(request).status(run_id)
        from nextstep.evals.score import summarize_run

        state["metrics"] = summarize_run(state)
        state["historical"] = (
            state["config"]["corpus_version"]
            != request.app.state.repository.active_version()
        )
        return state
    except NoResultFound:
        raise HTTPException(404, "Run not found") from None


@router.post("/runs/{run_id}/cases/{case_id}")
def execute(run_id: str, case_id: str, method: str, request: Request):
    r = runner(request)
    config = status(run_id, request)["config"]
    service = getattr(request.app.state, "eval_execute", None)
    if service is None:
        raise HTTPException(503, "Evaluation service unavailable")
    try:
        return r.execute_case(
            run_id,
            case_id,
            method,
            lambda: service({**config, "run_id": run_id}, case_id, method),
            after_save=(
                lambda result: service.trace_result(result, config, case_id, method)
            )
            if hasattr(service, "trace_result")
            else None,
        )
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from None


class RetryRequest(Model):
    acknowledge_cost: bool = False


@router.post("/runs/{run_id}/cases/{case_id}/retry")
def retry(
    run_id: str, case_id: str, method: str, payload: RetryRequest, request: Request
):
    try:
        runner(request).retry_case(run_id, case_id, method, payload.acknowledge_cost)
        return {"status": "pending"}
    except (ValueError, NoResultFound) as exc:
        raise HTTPException(
            409, str(exc) if isinstance(exc, ValueError) else "Attempt not found"
        ) from None


@router.post("/runs/{run_id}/cancel")
def cancel(run_id: str, request: Request):
    status(run_id, request)
    runner(request).cancel(run_id)
    return {"status": "cancelled"}


@router.get("/ingestion")
def ingestion(request: Request):
    # Never accept arbitrary file paths from a browser. Only fixed, sanitized summary fields.
    import json
    from pathlib import Path

    from nextstep.storage import LocalArtifactStore, ReplitArtifactStore

    settings = request.app.state.settings
    store = (
        ReplitArtifactStore(settings.app_storage_bucket_id)
        if settings.app_storage_bucket_id
        else LocalArtifactStore(Path(__file__).resolve().parents[3] / "artifacts")
    )
    try:
        rows = json.loads(store.get("reports/collection.json"))
    except FileNotFoundError:
        return {"reports": [], "note": "No collection report has been saved yet"}
    except Exception:  # noqa: BLE001 - do not expose storage credentials/errors
        raise HTTPException(503, "Ingestion report storage is unavailable") from None
    allowed = {
        "source_id",
        "status",
        "sections",
        "characters",
        "error",
        "url",
        "content_hash",
        "fetched_at",
    }
    sanitized = []
    for row in rows:
        flat = {
            **row,
            "source_id": row.get("source", {}).get("id", row.get("source_id")),
            "url": row.get("source", {}).get("url", row.get("url")),
        }
        sanitized.append({k: v for k, v in flat.items() if k in allowed})
    return {"reports": sanitized}
