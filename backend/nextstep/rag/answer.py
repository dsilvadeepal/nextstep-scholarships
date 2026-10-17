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

from langsmith import tracing_context
from nextstep.matching import match_catalog
from nextstep.models import AnswerResult, RetrievedEvidence
from nextstep.rag.comparisons import (
    award_classification,
    reviewed_conflict_explanations,
    score_comparisons,
)
from nextstep.rag.construction import construct


@lru_cache(maxsize=4)
def _coverage_register(version):
    data_dir = Path(__file__).resolve().parents[3] / "data"
    for name in (
        "reviewed-coverage-2026-10-14.json",
        "expanded-coverage-2026-10-16.json",
    ):
        path = data_dir / name
        if path.exists():
            register = json.loads(path.read_text())
            if register["corpus_version"] == version:
                return register
    return None


def _deferred_entries(question, version):
    register = _coverage_register(version)
    if register is None:
        return
    for entry in register["deferred"]:
        aliases = [
            alias
            for alias in entry["aliases"]
            if re.search(
                r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
                question,
                flags=0 if alias == "HOPE" else re.IGNORECASE,
            )
        ]
        if aliases:
            yield entry, max(aliases, key=len)


def deferred_coverage(question, version):
    return [
        f"{name} is not in this verified corpus. {entry['reason']}"
        for entry, name in _deferred_entries(question, version)
    ]


def coverage_links(question, version):
    return [
        link
        for entry, _ in _deferred_entries(question, version)
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
        if not request.program_ids:
            explicit = []
            for record in self.records:
                acronym = re.match(r"^([A-Z]{2,5})\b", record.name)
                if acronym and re.search(
                    r"\b" + re.escape(acronym[1]) + r"\b",
                    request.question,
                    re.IGNORECASE,
                ):
                    explicit.append(record.id)
            if 0 < len(explicit) <= 4:
                request = request.model_copy(update={"program_ids": explicit})
        records = [
            r
            for r in self.records
            if not request.program_ids or r.id in request.program_ids
        ]

        # A focused follow-up overrides a previously saved comparison set.
        # Use distinctive leading institution/sponsor names, never residency words.
        focused_followup = False
        if history and len(request.program_ids) > 1:
            named = []
            for record in records:
                lead = record.name.split()[0]
                if (
                    len(lead) >= 4
                    and lead.lower()
                    not in {
                        "georgia",
                        "university",
                        "college",
                        "the",
                        "north",
                        "south",
                    }
                    and re.search(
                        r"\b" + re.escape(lead) + r"\b", request.question, re.IGNORECASE
                    )
                ):
                    named.append(record.id)
            if named:
                focused_followup = True
                request = request.model_copy(update={"program_ids": named})
                records = [r for r in records if r.id in named]

        blocks, answer_gaps, usage, review = [], [], {}, {}
        with tracing_context(enabled=False):
            prior = " ".join(t.content for t in history if t.role == "user")[-600:]
            question = request.question
            remaining = 2000 - len(question) - 20
            if prior and remaining > 0 and not focused_followup:
                question = f"{prior[-remaining:]}\nFollow-up: {question}"
            evidence = self.retriever.retrieve(
                request.model_copy(update={"question": question})
            )

            if evidence.chunks:
                relevant = [
                    r
                    for r in records
                    if r.id in {c.program_id for c in evidence.chunks}
                ]
                checks = match_catalog(
                    relevant,
                    profile,
                    as_of or datetime.now(ZoneInfo("America/New_York")).date(),
                )
                comparisons = (
                    score_comparisons(request.question, evidence, relevant)
                    + award_classification(request.question, evidence, relevant)
                    + reviewed_conflict_explanations(
                        request.question, evidence, relevant
                    )
                )
                payload = {
                    "as_of_date": str(
                        as_of or datetime.now(ZoneInfo("America/New_York")).date()
                    ),
                    "computed_comparisons": [b.model_dump() for b in comparisons],
                    "question": request.question,
                    "profile": profile.model_dump(mode="json"),
                    "history": [t.model_dump() for t in history if t.role == "user"],
                    "condition_checks": [r.model_dump(mode="json") for r in checks],
                    "catalog_scope": [
                        {
                            "program_id": r.id,
                            "name": r.name,
                            "cycle": r.cycle,
                            "reviewed_conflicts": r.conflicts,
                        }
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
                blocks = comparisons + blocks
                answer_gaps = gaps
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
        gaps.extend(
            f"{r.name}: conflicting {field.replace('_', ' ')} instructions: "
            + " versus ".join(str(value) for value in values)
            + ". Confirm this point with the official sponsor before applying."
            for r in relevant
            for field, values in r.conflicts.items()
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
