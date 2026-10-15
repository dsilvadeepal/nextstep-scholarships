"""Paid, bounded comparison on exposed demo cases, preserving per-case evidence and costs."""

import argparse
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
import time

from sqlalchemy import create_engine
from nextstep.limits import BudgetLedger
from nextstep.models import StudentProfile, RetrievalRequest, ChatTurn
from nextstep.providers import PaidModel, OpenAIEmbeddingProvider, PineconeStore
from nextstep.rag.answer import AnswerService
from nextstep.rag.retrieve import Retriever
from reviewed_runtime import ROOT, live_settings, load_bundle


class RecordedModel:
    def __init__(self, model, directory):
        self.model, self.directory, self.calls = model, directory, 0

    def invoke(self, schema, instructions, payload, max_output):
        self.calls += 1
        result, usage = self.model.invoke(schema, instructions, payload, max_output)
        (self.directory / f"model-{self.calls}-{schema.__name__}.json").write_text(
            json.dumps(
                {"output": result.model_dump(mode="json"), "usage": usage}, indent=2
            )
        )
        return result, usage


class CachedDense:
    def __init__(self, settings, ledger, path):
        self.settings, self.ledger, self.path = settings, ledger, path
        self.cache = json.loads(path.read_text()) if path.exists() else {}
        self.store = None

    def search(self, question, version, program_id, limit):
        key = json.dumps([question, version, program_id, limit])
        if key not in self.cache:
            if self.store is None:
                self.store = PineconeStore(
                    self.settings, OpenAIEmbeddingProvider(self.settings, self.ledger)
                )
            self.cache[key] = self.store.search(question, version, program_id, limit)
            self.path.write_text(json.dumps(self.cache, indent=2))
        return self.cache[key]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=["baseline", "targeted"], required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--cases", default="evals/demo-regression.json")
    args = parser.parse_args()
    settings = live_settings("0.50")
    engine = create_engine(settings.database_url)
    ledger = BudgetLedger(
        engine, Decimal("0.50"), Decimal("5.00"), enabled=True, run_id=args.run
    )
    bundle, records, chunks = load_bundle()
    report_dir = ROOT / "artifacts/reports" / args.run
    report_dir.mkdir(parents=True, exist_ok=True)
    dense = CachedDense(
        settings, ledger, ROOT / "artifacts/reports/rag-comparison-dense-cache.json"
    )
    service = AnswerService(
        Retriever(chunks, dense),
        RecordedModel(PaidModel(settings, ledger), report_dir),
        records,
    )
    cases = json.loads((ROOT / args.cases).read_text())
    for index, case in enumerate(cases):
        target = report_dir / f"{args.policy}-{index}.json"
        if target.exists():
            print(case["case"], "already saved; not replayed", flush=True)
            continue
        data = case["input"]
        request = RetrievalRequest.model_validate(
            {**data["request"], "retrieval_policy": args.policy}
        )
        before, start = ledger.spent(), time.monotonic()
        result = {
            "case": case["case"],
            "input": data,
            "rubric": case["rubric"],
            "policy": args.policy,
            "corpus_version": bundle["version"],
            "ledger_before_usd": str(before),
        }
        try:
            answer = service.answer_question(
                StudentProfile.model_validate(data["profile"]),
                request,
                [ChatTurn.model_validate(t) for t in data["history"]],
                as_of=date(2026, 10, 15),
            )
            result["output"] = answer.model_dump(mode="json")
        except Exception as exc:
            # Never persist provider payloads or credential-bearing exception strings.
            result["error_type"] = type(exc).__name__
            import traceback

            result["error_frames"] = [
                {"file": Path(f.filename).name, "line": f.lineno, "function": f.name}
                for f in traceback.extract_tb(exc.__traceback__)
            ]
            if type(exc) is ValueError and str(exc) in (
                "Provider structured output did not validate",
                "Answer review did not cover every claim exactly once",
                "Model input exceeds bounded context",
            ):
                result["error_detail"] = str(exc)
        result.update(
            ledger_after_usd=str(ledger.spent()),
            query_cost_usd=str(ledger.spent() - before),
            seconds=round(time.monotonic() - start, 3),
        )
        target.write_text(json.dumps(result, indent=2) + "\n")
        print(
            case["case"],
            result.get("error_type", "saved"),
            result["query_cost_usd"],
            result["seconds"],
            flush=True,
        )
        if "error_type" in result:
            raise SystemExit("Stopped on saved failure; inspect before retrying.")


if __name__ == "__main__":
    main()
