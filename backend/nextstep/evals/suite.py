"""Checked fictional cases; freeze full content into each run, never read mutable cases mid-run."""

import hashlib
import json
from pathlib import Path
from typing import Literal

from nextstep.models import EvalCase, EvidenceRef, Model

ROOT = Path(__file__).resolve().parents[3] / "evals"
EXPANDED_SUITES = {"expanded", "expanded_regression"}


class RunRequest(Model):
    split: Literal["tuning", "heldout"] = "tuning"


def add_admitted_context(cases, bundle):
    for case in cases:
        programs = set(case.program_ids)
        if not programs:
            sources = {ref.source_id for ref in case.checked_sources}
            programs = {
                c["program_id"] for c in bundle["chunks"] if c["source_id"] in sources
            }
        refs = {ref.id: ref for ref in case.checked_sources}
        units = {
            (
                ref.source_id,
                ref.document_version,
                ref.section_id,
                ref.start,
                ref.end,
                ref.quote,
            )
            for ref in refs.values()
        }
        for chunk in bundle["chunks"]:
            if chunk["program_id"] in programs:
                for raw in chunk["evidence"]:
                    ref = EvidenceRef.model_validate(raw)
                    key = (
                        ref.source_id,
                        ref.document_version,
                        ref.section_id,
                        ref.start,
                        ref.end,
                        ref.quote,
                    )
                    if key not in units:
                        refs[ref.id] = ref
                        units.add(key)
        case.checked_sources = list(refs.values())


def load_suite(split="tuning", suite="reviewed", version=None):
    if suite == "expanded_regression":
        _, candidate_digest = load_suite(split, "expanded", version)
        cases, original_digest = load_suite("tuning", "reviewed")
        bundle = json.loads(
            (ROOT.parent / "data/expanded-corpus-2026-10-16.json").read_bytes()
        )
        add_admitted_context(cases, bundle)
        return cases, hashlib.sha256(
            (candidate_digest + original_digest).encode()
        ).hexdigest()
    if suite == "expanded":
        if split != "tuning" or version is None:
            raise ValueError("Expanded references are exposed tuning cases only")
        path = ROOT.parent / "data/expanded-eval-reference-2026-10-16.json"
        content = path.read_bytes()
        source = json.loads(content)
        bundle = ROOT.parent / "data/expanded-corpus-2026-10-16.json"
        if (
            source["corpus_version"] != version
            or source["bundle_sha256"]
            != hashlib.sha256(bundle.read_bytes()).hexdigest()
            or source["split"] != "tuning"
            or not source["not_held_out"]
        ):
            raise ValueError("Expanded cases do not match the frozen candidate")
        cases = [
            EvalCase(
                id=row["id"],
                program_ids=row["program_ids"],
                profile=row["fictional_profile"],
                question=row["question"],
                frozen_date=row["as_of"],
                checked_sources=[ref["evidence"] for ref in row["checked_references"]],
                expected_evidence=[
                    ref["evidence"]["id"] for ref in row["checked_references"]
                ],
                expected_claims=[row["expected_behavior"]]
                + [f"Must not: {claim}" for claim in row["prohibited_behavior"]],
                critical=True,
                synthetic=True,
            )
            for row in source["cases"]
        ]
        if len({c.id for c in cases}) != len(cases):
            raise ValueError("Duplicate expanded reference case")
        add_admitted_context(cases, json.loads(bundle.read_bytes()))
        return cases, hashlib.sha256(content).hexdigest()
    if suite != "reviewed":
        raise ValueError("Unknown evaluation suite")
    path = ROOT / ("cases.jsonl" if split == "tuning" else "heldout.jsonl")
    content = path.read_bytes()
    cases = [
        EvalCase.model_validate(json.loads(line))
        for line in content.splitlines()
        if line.strip()
    ]
    if len({c.id for c in cases}) != len(cases):
        raise ValueError("Duplicate reference case")
    return cases, hashlib.sha256(content).hexdigest()


def snapshot(settings, version, split, methods=None, suite="reviewed"):
    from nextstep.rag.retrieve import HYBRID_WEIGHTS

    cases, digest = load_suite(split, suite, version)
    methods = methods or ["semantic", "hybrid"]
    if suite in EXPANDED_SUITES and methods != ["hybrid"]:
        raise ValueError("Expanded candidate is evaluated on the 50/50 hybrid default")
    coverage_path = ROOT.parent / (
        "data/expanded-coverage-2026-10-16.json"
        if suite in EXPANDED_SUITES
        else "data/reviewed-coverage-2026-10-14.json"
    )
    if (
        suite in EXPANDED_SUITES
        and json.loads(coverage_path.read_text())["corpus_version"] != version
    ):
        raise ValueError("Expanded coverage does not match the candidate")
    config = {
        "corpus_version": version,
        "cases": [c.id for c in cases],
        "case_snapshots": {c.id: c.model_dump(mode="json") for c in cases},
        "methods": methods,
        "split": split,
        "suite_hash": digest,
        "model": settings.answer_model,
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "pinecone_index": settings.pinecone_index,
        "prompt_version": "grounded-answer-v3-review-v2/judge-v9",
        "scoring_version": "explicit-evidence-gap-v5",
        "coverage_register_hash": hashlib.sha256(
            coverage_path.read_bytes()
        ).hexdigest(),
        "chunking": "500/75/section-v1",
        "retrieval": "40 candidates or 20+20 RRF60; targeted facet coverage for selected programs; 8 passages/5000 tokens",
        "answer_code_hash": hashlib.sha256(
            b"".join(
                (ROOT.parent / "backend/nextstep/rag" / name).read_bytes()
                for name in (
                    "answer.py",
                    "construction.py",
                    "comparisons.py",
                    "retrieve.py",
                    "target.py",
                )
            )
        ).hexdigest(),
        "pricing_date": settings.pricing_effective_date,
        "input_usd_per_million": str(settings.input_usd_per_million),
        "output_usd_per_million": str(settings.output_usd_per_million),
        "embedding_usd_per_million": str(settings.embedding_usd_per_million),
        "run_budget_usd": str(settings.openai_run_budget_usd),
        "total_budget_usd": str(settings.openai_total_budget_usd),
    }
    if suite in EXPANDED_SUITES:
        config.update(
            suite=suite,
            bundle_sha256=hashlib.sha256(
                (ROOT.parent / "data/expanded-corpus-2026-10-16.json").read_bytes()
            ).hexdigest(),
            content_policy_hash=hashlib.sha256(
                (ROOT.parent / "data/content-exclusions-2026-10-16.json").read_bytes()
            ).hexdigest(),
        )
    if "hybrid_60_40" in methods:
        config["retrieval_weights"] = {
            method: list(HYBRID_WEIGHTS[method])
            for method in methods
            if method in HYBRID_WEIGHTS
        }
    return config
