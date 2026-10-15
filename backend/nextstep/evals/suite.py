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


def snapshot(settings, version, split):
    cases, digest = load_suite(split)
    return {
        "corpus_version": version,
        "cases": [c.id for c in cases],
        "case_snapshots": {c.id: c.model_dump(mode="json") for c in cases},
        "methods": ["semantic", "hybrid"],
        "split": split,
        "suite_hash": digest,
        "model": settings.answer_model,
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "pinecone_index": settings.pinecone_index,
        "prompt_version": "extractive-answer-v1/judge-v1",
        "chunking": "500/75/section-v1",
        "retrieval": "40 candidates or 20+20 RRF60; 8 passages/5000 tokens",
        "pricing_date": settings.pricing_effective_date,
        "input_usd_per_million": str(settings.input_usd_per_million),
        "output_usd_per_million": str(settings.output_usd_per_million),
        "embedding_usd_per_million": str(settings.embedding_usd_per_million),
        "run_budget_usd": str(settings.openai_run_budget_usd),
        "total_budget_usd": str(settings.openai_total_budget_usd),
    }
