"""Manual ingestion. Collection is free; extraction/publication require explicit live access."""

import argparse
import json
import sys
from pathlib import Path

import yaml
from nextstep.config import Settings
from nextstep.ingest.chunk import make_chunks
from nextstep.ingest.collect import SourceSpec, collect_source
from nextstep.ingest.extract import associate_sections, extract_scholarships
from nextstep.ingest.parse import parse_source
from nextstep.ingest.publish import Publisher
from nextstep.ingest.reconcile import bind_program_ids, reconcile_records
from nextstep.limits import BudgetLedger
from nextstep.models import NormalizedDocument, Scholarship
from nextstep.providers import OpenAIEmbeddingProvider, PaidModel, PineconeStore
from nextstep.repository import Repository
from nextstep.storage import LocalArtifactStore, ReplitArtifactStore
from sqlalchemy import create_engine


def collect_all(path, store):
    reports = []
    documents = []
    for raw in yaml.safe_load(Path(path).read_text())["sources"]:
        source = SourceSpec(**raw)
        collected = collect_source(source, store)
        report = collected.model_dump(mode="json")
        if collected.status == "collected":
            key = f"normalized/{source.id}/{collected.content_hash}.parser-v2.json"
            try:
                try:
                    document = NormalizedDocument.model_validate_json(store.get(key))
                except (FileNotFoundError, KeyError):
                    document = parse_source(collected, store)
                    store.put(key, document.model_dump_json(indent=2).encode())
                report.update(
                    status="parsed",
                    normalized_key=key,
                    sections=len(document.sections),
                    characters=sum(len(s.text) for s in document.sections),
                )
                documents.append(document)
            except Exception as exc:  # noqa: BLE001 - retain processing failures in report
                report.update(status="parse_failed", error=type(exc).__name__)
        reports.append(report)
        store.put("reports/collection.json", json.dumps(reports, indent=2).encode())
        print(source.id, report["status"], flush=True)
    return documents, reports


def stage_or_resume(repo, version, records, chunks):
    def same(left, right):
        return sorted(r.model_dump_json() for r in left) == sorted(
            r.model_dump_json() for r in right
        )

    existing = repo.list_scholarships(version)
    if existing:
        if not same(existing, records):
            raise ValueError("Version already exists with different catalog")
        saved = repo.get_chunks(version)
        if saved:
            if not same(saved, chunks):
                raise ValueError("Version already exists with different chunks")
            return
    else:
        repo.stage_catalog(version, records)
    repo.stage_chunks(version, chunks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("collect", "run", "publish", "rollback"):
        command = sub.add_parser(name)
        command.add_argument("--sources", default="data/sources.yaml")
        command.add_argument("--version", required=name != "collect")
        command.add_argument("--artifacts", default="artifacts")
        command.add_argument("--app-storage", action="store_true")
    args = parser.parse_args(argv)
    settings = Settings()
    if args.command in ("run", "publish") and (
        not settings.live_calls_enabled
        or settings.openai_run_budget_usd <= 0
        or settings.openai_total_budget_usd <= 0
    ):
        parser.error(
            "Live calls are disabled; approved access and numerical budgets are required"
        )
    store = (
        ReplitArtifactStore(settings.app_storage_bucket_id)
        if args.app_storage
        else LocalArtifactStore(args.artifacts)
    )
    if args.command == "collect":
        collect_all(args.sources, store)
        return
    if not settings.database_url:
        parser.error("DATABASE_URL is required; migrate the selected database first")
    repo = Repository(create_engine(settings.database_url, pool_pre_ping=True))
    if args.command == "rollback":
        if not repo.is_ready(args.version):
            parser.error("Rollback requires a retained ready corpus")
        repo.activate_version(repo.active_version(), args.version)
        print(json.dumps({"status": "rolled_back", "version": args.version}))
        return
    ledger = BudgetLedger(
        repo.engine,
        settings.openai_run_budget_usd,
        settings.openai_total_budget_usd,
        enabled=True,
        run_id=args.version,
    )
    if args.command == "run":
        docs, reports = collect_all(args.sources, store)
        sources = {
            s["id"]: SourceSpec(**s)
            for s in yaml.safe_load(Path(args.sources).read_text())["sources"]
        }
        records = []
        chunks = []
        model = PaidModel(settings, ledger)
        for doc in docs:
            key = f"extracted/{doc.source_id}/{doc.content_hash}-{settings.answer_model}-units-v6.json"
            try:
                try:
                    extracted = [
                        Scholarship.model_validate(r)
                        for r in json.loads(store.get(key))
                    ]
                except (FileNotFoundError, KeyError):
                    extracted = extract_scholarships(doc, model)
                    store.put(
                        key,
                        json.dumps(
                            [r.model_dump(mode="json") for r in extracted], indent=2
                        ).encode(),
                    )
                extracted = bind_program_ids(extracted, sources[doc.source_id])
                for record in extracted:
                    record.corpus_version = args.version
                associated = associate_sections(
                    doc,
                    extracted,
                    partitions=sources[doc.source_id].section_partitions,
                    expected_hash=sources[doc.source_id].expected_content_hash,
                )
                passages = make_chunks(associated, extracted, args.version)
                records.extend(extracted)
                chunks.extend(passages)
            except Exception as exc:
                store.put(
                    f"reports/{args.version}-failure.json",
                    json.dumps(
                        {
                            "source_id": doc.source_id,
                            "error": type(exc).__name__,
                            "status": "interrupted",
                            "paid_retry_requires_review": True,
                        }
                    ).encode(),
                )
                raise
        records, reconciliation = reconcile_records(records)
        if any(r["status"] != "parsed" for r in reports):
            parser.error(
                "Some sources failed. Review the report and explicitly curate the source register before staging"
            )
        stage_or_resume(repo, args.version, records, chunks)
        store.put(
            f"reports/{args.version}.json",
            json.dumps(
                {
                    "version": args.version,
                    "status": "staged",
                    "programs": len(records),
                    "chunks": len(chunks),
                    "sources": len(docs),
                    "reconciliation": reconciliation,
                }
            ).encode(),
        )
        return
    publisher = Publisher(
        repo,
        OpenAIEmbeddingProvider(settings, ledger),
        PineconeStore(settings, OpenAIEmbeddingProvider(settings, ledger)),
    )
    previous = repo.active_version()
    if args.command == "publish":
        report = publisher.publish_corpus(args.version, previous)
        store.put(
            f"reports/{args.version}-published.json",
            json.dumps(report.__dict__).encode(),
        )
        print(json.dumps(report.__dict__))
    else:
        publisher.rollback(args.version, previous)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - CLI avoids accidental provider secret output
        print(
            f"Ingestion stopped: {type(exc).__name__}. Inspect saved reports; no automatic paid retry.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
