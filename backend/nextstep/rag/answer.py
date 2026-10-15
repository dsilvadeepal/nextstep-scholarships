"""Citation resolution gate. Semantic support still requires evaluation."""


def validate_answer(answer):
    supplied = {c.id for c in answer.evidence.chunks}
    supplied.update(ref.id for c in answer.evidence.chunks for ref in c.evidence)
    if any(c.corpus_version != answer.corpus_version for c in answer.evidence.chunks):
        raise ValueError("Mixed corpus versions")
    by_id = {c.id: c for c in answer.evidence.chunks}
    for block in answer.blocks:
        if not block.evidence_ids or not set(block.evidence_ids).issubset(supplied):
            raise ValueError("Answer has missing or unresolved citations")
        if block.kind == "explanation":
            if len(block.evidence_ids) != len(block.supporting_quotes):
                raise ValueError("Explanation support mismatch")
            for cid, quote in zip(block.evidence_ids, block.supporting_quotes):
                chunk = by_id.get(cid)
                if (
                    not chunk
                    or chunk.program_id != block.program_id
                    or not quote
                    or quote not in chunk.text
                ):
                    raise ValueError("Explanation has invalid program or quotation")
    if not answer.blocks and not answer.gaps:
        raise ValueError("Empty answer")
    return answer


import json
import re
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from langchain_core.runnables import RunnableLambda
from langsmith import tracing_context
from nextstep.matching import match_catalog
from nextstep.models import AnswerResult, RetrievedEvidence
from nextstep.rag.construction import construct


@lru_cache(maxsize=1)
def _coverage_register():
    path = (
        Path(__file__).resolve().parents[3] / "data/reviewed-coverage-2026-10-14.json"
    )
    return json.loads(path.read_text())


def deferred_coverage(question, version):
    register = _coverage_register()
    if register["corpus_version"] != version:
        return []
    gaps = []
    for entry in register["deferred"]:
        matches = [
            alias
            for alias in entry["aliases"]
            if re.search(
                r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
                question,
                flags=0 if alias == "HOPE" else re.IGNORECASE,
            )
        ]
        if matches:
            name = max(matches, key=len)
            gaps.append(f"{name} is not in this verified corpus. {entry['reason']}")
    return gaps


def coverage_links(question, version):
    register = _coverage_register()
    if register["corpus_version"] != version:
        return []
    return [
        link
        for entry in register["deferred"]
        if any(
            re.search(
                r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
                question,
                flags=0 if alias == "HOPE" else re.IGNORECASE,
            )
            for alias in entry["aliases"]
        )
        for link in entry.get("official_links", [])
    ]


class AnswerService:
    def __init__(self, retriever, model, records):
        self.retriever, self.model, self.records = retriever, model, records

    def answer_question(self, profile, request, history, as_of=None):
        if not request.corpus_version:
            raise ValueError("Answer corpus must be pinned")
        if len(history) > 6 or sum(len(turn.content) for turn in history) > 8000:
            raise ValueError("Conversation history exceeds limits")
        started = time.monotonic()
        coverage_gaps = deferred_coverage(request.question, request.corpus_version)
        if coverage_gaps:
            return validate_answer(
                AnswerResult(
                    blocks=[],
                    gaps=coverage_gaps,
                    corpus_version=request.corpus_version,
                    method=request.method,
                    evidence=RetrievedEvidence(chunks=[]),
                    timings={"answer_seconds": time.monotonic() - started},
                    usage={},
                    retrieval_policy=request.retrieval_policy,
                    source_links=coverage_links(
                        request.question, request.corpus_version
                    ),
                )
            )
        records = [
            r
            for r in self.records
            if not request.program_ids or r.id in request.program_ids
        ]

        def retrieve(_):
            prior = " ".join(t.content for t in history if t.role == "user")[-600:]
            question = request.question
            remaining = 2000 - len(question) - 20
            if prior and remaining > 0:
                question = f"{prior[-remaining:]}\nFollow-up: {question}"
            return self.retriever.retrieve(
                request.model_copy(update={"question": question})
            )

        def generate(evidence):
            if not evidence.chunks:
                return [], [], {}, {}, evidence
            relevant = [
                r for r in records if r.id in {c.program_id for c in evidence.chunks}
            ]
            checks = match_catalog(
                relevant,
                profile,
                as_of or datetime.now(ZoneInfo("America/New_York")).date(),
            )
            payload = {
                "question": request.question,
                "profile": profile.model_dump(mode="json"),
                "history": [t.model_dump() for t in history if t.role == "user"],
                "condition_checks": [r.model_dump(mode="json") for r in checks],
                "catalog_scope": [
                    {"program_id": r.id, "name": r.name, "cycle": r.cycle}
                    for r in relevant
                ],
                "evidence": [
                    {
                        "id": c.id,
                        "text": c.text,
                        "heading": c.heading,
                        "program_id": c.program_id,
                        "cycle": c.cycle,
                        "cycle_metadata": c.cycle_metadata.model_dump(),
                    }
                    for c in evidence.chunks
                ],
            }
            blocks, gaps, usage, review = construct(self.model, payload)
            return blocks, gaps, usage, review, evidence

        chain = RunnableLambda(retrieve) | RunnableLambda(generate)
        with tracing_context(enabled=False):
            blocks, answer_gaps, usage, review, evidence = chain.invoke(None)
        cited_chunks = {i for block in blocks for i in block.evidence_ids}
        relevant_programs = set(request.program_ids) or {
            c.program_id for c in evidence.chunks if c.id in cited_chunks
        }
        relevant = [r for r in records if r.id in relevant_programs]
        matches = match_catalog(
            relevant,
            profile,
            as_of or datetime.now(ZoneInfo("America/New_York")).date(),
        )
        gaps = answer_gaps + [
            f"{r.scholarship_id}: {q}" for r in matches for q in r.followups
        ]
        gaps.extend(
            f"{r.name}: {r.information_status} evidence; confirm current rules with the official sponsor."
            for r in relevant
            if r.information_status in ("incomplete", "historical", "conflicting")
        )
        if not blocks:
            gaps.append(
                "The available evidence does not establish an answer. Check the official sponsor source or contact the sponsor."
            )
        answer = AnswerResult(
            blocks=blocks,
            gaps=list(dict.fromkeys(gaps)),
            corpus_version=request.corpus_version,
            method=request.method,
            evidence=evidence,
            timings={**evidence.timings, "answer_seconds": time.monotonic() - started},
            usage=usage,
            retrieval_policy=request.retrieval_policy,
            review=review,
        )
        return validate_answer(answer)
