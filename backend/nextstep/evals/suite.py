"""Checked fictional cases; freeze full content into each run, never read mutable cases mid-run."""

import hashlib
import json
from pathlib import Path
from typing import Literal

from nextstep.models import EvalCase, Model

ROOT = Path(__file__).resolve().parents[3] / "evals"


class RunRequest(Model):
    split: Literal["tuning", "heldout"] = "tuning"


def load_suite(split="tuning"):
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


def snapshot(settings, version, split, methods=None):
    from nextstep.rag.retrieve import HYBRID_WEIGHTS

    cases, digest = load_suite(split)
    methods = methods or ["semantic", "hybrid"]
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
        "prompt_version": "grounded-answer-v1-review-v1/judge-v1",
        "scoring_version": "explicit-evidence-gap-v2",
        "coverage_register_hash": hashlib.sha256(
            (ROOT.parent / "data/reviewed-coverage-2026-10-14.json").read_bytes()
        ).hexdigest(),
        "chunking": "500/75/section-v1",
        "retrieval": "40 candidates or 20+20 RRF60; 8 passages/5000 tokens",
        "pricing_date": settings.pricing_effective_date,
        "input_usd_per_million": str(settings.input_usd_per_million),
        "output_usd_per_million": str(settings.output_usd_per_million),
        "embedding_usd_per_million": str(settings.embedding_usd_per_million),
        "run_budget_usd": str(settings.openai_run_budget_usd),
        "total_budget_usd": str(settings.openai_total_budget_usd),
    }
    if "hybrid_60_40" in methods:
        config["retrieval_weights"] = {
            method: list(HYBRID_WEIGHTS[method])
            for method in methods
            if method in HYBRID_WEIGHTS
        }
    return config
