"""Evaluate the staged expanded candidate without activating it or resetting spend.

Run exposed tuning cases only. Results live in a separate SQLite file so an
older unfinished evaluation run does not get mutated; provider charges still
use the original shared nextstep-live.db ledger.
"""

import argparse
import json

from expanded_runtime import load_candidate
from nextstep.db import metadata
from nextstep.evals.runner import EvalRunner
from nextstep.evals.score import summarize_run
from nextstep.evals.service import EvaluationService
from nextstep.evals.suite import snapshot
from nextstep.limits import BudgetLedger
from nextstep.repository import Repository
from reviewed_runtime import ROOT, live_settings
from sqlalchemy import create_engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-id", help="Resume this saved run; never replay completed calls"
    )
    parser.add_argument(
        "--case-id", help="Run one exposed tuning case from the frozen suite"
    )
    parser.add_argument(
        "--limit", type=int, default=26, help="Maximum cases this invocation"
    )
    parser.add_argument(
        "--regressions",
        action="store_true",
        help="Run the 26 previously exposed cases against the candidate",
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 26:
        parser.error("--limit must be between 1 and 26")

    data, _, _ = load_candidate(check_raw=True)
    settings = live_settings(run_cap="1.00").model_copy(
        update={"pricing_effective_date": "2026-10-16"}
    )
    repo = Repository(create_engine(settings.database_url))
    version = data["version"]
    if not repo.is_ready(version) or repo.active_version() == version:
        raise ValueError("Candidate must be staged and inactive")

    config = snapshot(
        settings,
        version,
        "tuning",
        ["hybrid"],
        suite="expanded_regression" if args.regressions else "expanded",
    )
    if args.case_id and args.case_id not in config["cases"]:
        parser.error("--case-id is outside the frozen suite")
    # A coverage or rubric change starts a new immutable result history.
    result_db = ROOT / (
        f"artifacts/expanded-eval-{config['coverage_register_hash'][:12]}-"
        f"{config['scoring_version']}-{config['prompt_version'].split('/')[-1]}.db"
    )
    result_engine = create_engine(f"sqlite:///{result_db}")
    metadata.create_all(result_engine)
    runner = EvalRunner(result_engine)
    if args.run_id:
        run_id = args.run_id
        if runner.status(run_id)["config"] != config:
            raise ValueError("Saved run configuration differs from frozen candidate")
    else:
        run_id = runner.start_run(config)
    print(
        f"run_id={run_id} version={version} active={repo.active_version()}", flush=True
    )

    service = EvaluationService(settings, repo)
    completed_this_invocation = 0
    for case_id in config["cases"]:
        if args.case_id and case_id != args.case_id:
            continue
        if completed_this_invocation >= args.limit:
            break
        state = runner.status(run_id)
        existing = next(
            (
                row
                for row in state["results"]
                if row["case_id"] == case_id and row["method"] == "hybrid"
            ),
            None,
        )
        if existing:
            if existing["status"] == "completed":
                continue
            raise ValueError(
                f"{case_id} is {existing['status']}; inspect cost and retry explicitly"
            )
        result = runner.execute_case(
            run_id,
            case_id,
            "hybrid",
            lambda case_id=case_id: service(
                {**config, "run_id": run_id}, case_id, "hybrid"
            ),
        )
        completed_this_invocation += 1
        state = runner.status(run_id)
        (ROOT / f"artifacts/reports/{run_id}-expanded.json").write_text(
            json.dumps(state, indent=2, default=str)
        )
        print(
            case_id,
            "passed=",
            result.get("scores", {}).get("passed"),
            "error=",
            result.get("error"),
            flush=True,
        )
        if result.get("error"):
            raise RuntimeError("Provider failure saved; no automatic retry")

    state = runner.status(run_id)
    ledger = BudgetLedger(
        repo.engine, settings.openai_run_budget_usd, settings.openai_total_budget_usd
    )
    report = {
        "run_id": run_id,
        "version": version,
        "split": "exposed_tuning",
        "completed": sum(r["status"] == "completed" for r in state["results"]),
        "total": len(config["cases"]),
        "metrics": summarize_run(state),
        "cumulative_spent_usd": str(ledger.spent()),
        "active_version_unchanged": repo.active_version(),
    }
    (ROOT / f"artifacts/reports/{run_id}-expanded-summary.json").write_text(
        json.dumps(report, indent=2, default=str)
    )
    print(json.dumps(report, indent=2, default=str), flush=True)


if __name__ == "__main__":
    main()
