"""Shared public contracts. Unknown source/profile facts stay null."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GPA(Model):
    value: float = Field(ge=0, le=100)
    scale: float | None = Field(default=None, gt=0)
    type: Literal["weighted", "unweighted", "unknown"] = "unknown"
    estimated: bool | None = None
    as_of: date | None = None


class StudentProfile(Model):
    grade: Literal[11, 12] | None = None
    graduation_year: int | None = None
    residence: dict[str, str] = Field(default_factory=dict)
    gpa: GPA | None = None
    interests: list[str] = Field(default_factory=list, max_length=20)
    prospective_colleges: list[str] = Field(default_factory=list, max_length=3)
    context: dict[str, Any] = Field(default_factory=dict)


class Scenario(Model):
    overrides: dict[str, Any] = Field(default_factory=dict)


class EvidenceRef(Model):
    id: str
    source_id: str
    document_version: str
    section_id: str
    page: int | None = None
    quote: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    url: str
    fetched_at: datetime
    title: str = ""
    cycle: str | None = None


class Condition(Model):
    id: str
    kind: str
    operator: str
    value: Any = None
    required: bool = True
    evidence: list[EvidenceRef] = Field(default_factory=list)
    children: list["Condition"] = Field(default_factory=list)
    reason: str | None = None


class ConditionResult(Model):
    condition_id: str
    status: Literal["met", "unmet", "unknown"]
    reason: str


class CycleMetadata(Model):
    application_cycle: str | None = None
    college_entry_year: int | None = None
    award_academic_year: str | None = None
    regulation_academic_year: str | None = None
    high_school_graduation_year: int | None = None


class Scholarship(Model):
    id: str
    corpus_version: str
    name: str
    sponsor: str | None = None
    scope: str | None = None
    cycle: str | None = None
    cycle_metadata: CycleMetadata = Field(default_factory=CycleMetadata)
    source_checked_at: date | None = None
    conditions: list[Condition] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    deadline: date | None = None
    opens: date | None = None
    timezone: str | None = None
    date_precision: str | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)
    information_status: Literal[
        "automatically_extracted",
        "incomplete",
        "historical",
        "conflicting",
        "source_checked",
    ] = "incomplete"
    official_url: str | None = None
    field_evidence: dict[str, list[str]] = Field(default_factory=dict)
    conflicts: dict[str, list[Any]] = Field(default_factory=dict)


class Section(Model):
    id: str
    heading: str
    page: int | None = None
    text: str
    table_headers: list[str] = Field(default_factory=list)
    table_rows: list[list[str]] = Field(default_factory=list)
    program_id: str | None = None
    kind: str = "text"
    warnings: list[str] = Field(default_factory=list)
    start_offset: int = Field(default=0, ge=0)


class NormalizedDocument(Model):
    id: str
    content_hash: str
    source_id: str
    url: str
    fetched_at: datetime
    sections: list[Section]


class Chunk(Model):
    id: str
    program_id: str
    source_id: str
    corpus_version: str
    text: str
    heading: str
    section_ids: list[str]
    token_count: int
    evidence: list[EvidenceRef] = Field(default_factory=list)
    neighbors: list[str] = Field(default_factory=list)
    indivisible: bool = False
    cycle: str | None = None
    cycle_metadata: CycleMetadata = Field(default_factory=CycleMetadata)
    information_status: str | None = None
    source_checked_at: date | None = None


class MatchResult(Model):
    scholarship_id: str
    conditions: list[ConditionResult]
    group: Literal["matches", "prepare", "explore", "unmet"]
    fit: str
    fit_reason: str
    timing: str
    evidence_label: str
    followups: list[str] = Field(default_factory=list)
    sort_key: tuple[int, int, str, str]


class RetrievalRequest(Model):
    question: str = Field(min_length=1, max_length=2000)
    program_ids: list[str] = Field(default_factory=list, max_length=4)
    corpus_version: str | None = None
    method: Literal["semantic", "hybrid", "hybrid_60_40"] = "hybrid"
    retrieval_policy: Literal["baseline", "targeted"] = "targeted"

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value):
        if not value.strip():
            raise ValueError("Question must contain non-whitespace text")
        return value


class RetrievedEvidence(Model):
    selection_details: dict[str, dict[str, str]] = Field(default_factory=dict)
    chunks: list[Chunk]
    ranks: dict[str, float] = Field(default_factory=dict)
    timings: dict[str, float] = Field(default_factory=dict)


class AnswerBlock(Model):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)
    program_id: str | None = None
    kind: Literal["quote", "explanation"] = "quote"
    supporting_quotes: list[str] = Field(default_factory=list)


class SourceLink(Model):
    title: str
    url: str


class AnswerResult(Model):
    construction_version: str = "grounded-v1"
    retrieval_policy: str = "baseline"
    source_links: list[SourceLink] = Field(default_factory=list)
    review: dict[str, Any] = Field(default_factory=dict)
    blocks: list[AnswerBlock]
    gaps: list[str] = Field(default_factory=list)
    corpus_version: str
    method: str
    evidence: RetrievedEvidence
    timings: dict[str, float] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)


class ChatTurn(Model):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=8000)


class EvalCase(Model):
    id: str
    program_ids: list[str] = Field(default_factory=list, max_length=4)
    profile: StudentProfile
    question: str
    frozen_date: date
    expected_conditions: dict[str, str] = Field(default_factory=dict)
    expected_evidence: list[str] = Field(default_factory=list)
    expected_claims: list[str] = Field(default_factory=list)
    expects_evidence_gap: bool = False
    critical: bool = False
    checked_sources: list[EvidenceRef] = Field(default_factory=list)
    synthetic: bool = False


class EvalResult(Model):
    run_id: str
    case_id: str
    method: str
    answer: AnswerResult | None = None
    scores: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    timings: dict[str, float] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
