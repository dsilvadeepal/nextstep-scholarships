"""Run the frozen fictional comparison with durable results and the shared $5 cap."""

import argparse
import json

from nextstep.evals.runner import EvalRunner
from nextstep.evals.score import summarize_run
from nextstep.evals.service import EvaluationService
from nextstep.evals.suite import snapshot
from nextstep.limits import BudgetLedger
from nextstep.repository import Repository
from reviewed_runtime import ROOT, live_settings, load_bundle
from sqlalchemy import create_engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", choices=["tuning", "heldout"])
    parser.add_argument("--run-id")
    parser.add_argument("--weighted-hybrid", action="store_true", help="Tuning-only 60/40 variant")
    args = parser.parse_args()
    settings = live_settings()
    bundle, _, _ = load_bundle()
    engine = create_engine(settings.database_url)
    repo = Repository(engine)
    assert repo.is_ready(bundle["version"])
    runner = EvalRunner(engine)
    if args.weighted_hybrid and args.split != "tuning":
        parser.error("The 60/40 experiment is restricted to tuning cases")
    methods = ["hybrid_60_40"] if args.weighted_hybrid else None
    config = snapshot(settings, bundle["version"], args.split, methods)
    if args.run_id:
        run_id = args.run_id
        saved = runner.status(run_id)
        assert saved["config"] == config
    else:
        run_id = runner.start_run(config)
    print("Run", run_id, args.split, flush=True)
    service = EvaluationService(settings, repo)
    for method in config["methods"]:
        for case_id in config["cases"]:
            existing = next(
                (
                    row for row in runner.status(run_id)["results"]
                    if row["case_id"] == case_id and row["method"] == method
                ),
                None,
            )
            if existing and existing["status"] == "error" and args.weighted_hybrid:
                print(method, case_id, "saved_error", flush=True)
                continue
            result = runner.execute_case(
                run_id,
                case_id,
                method,
                lambda case_id=case_id, method=method: service(
                    {**config, "run_id": run_id}, case_id, method
                ),
            )
            print(
                method,
                case_id,
                result.get("scores", {}).get("passed"),
                result.get("error", ""),
                flush=True,
            )
            state = runner.status(run_id)
            (ROOT / f"artifacts/reports/{run_id}.json").write_text(
                json.dumps(state, indent=2, default=str)
            )
            if result.get("error"):
                print("Provider failure persisted; no automatic retry", flush=True)
                return
    state = runner.status(run_id)
    summary = summarize_run(state)
    ledger = BudgetLedger(
        engine, settings.openai_run_budget_usd, settings.openai_total_budget_usd
    )
    out = {
        "run_id": run_id,
        "version": bundle["version"],
        "split": args.split,
        "metrics": summary,
        "spent_usd": str(ledger.spent()),
    }
    (ROOT / f"artifacts/reports/{run_id}-summary.json").write_text(
        json.dumps(out, indent=2)
    )
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
