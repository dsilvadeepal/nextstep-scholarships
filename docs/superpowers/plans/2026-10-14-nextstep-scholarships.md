# NextStep Scholarships Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the approved Georgia scholarship discovery demo with a real ingestion/RAG pipeline, cited student guidance, and inspectable retrieval evaluations.

**Architecture:** One React application and FastAPI service, with PostgreSQL as the catalog, App Storage for artifacts, and Pinecone for passage retrieval. Manual ingestion publishes versioned corpora; deterministic matching and a fixed RAG flow serve students. Admin requests execute bounded evaluation cases and persist progress without a background worker.

**Tech Stack:** Python 3.12, uv, FastAPI, Pydantic, SQLAlchemy/psycopg and Alembic; React/TypeScript/Vite; OpenAI, LangChain core/OpenAI integration, Pinecone, LangSmith; Replit PostgreSQL, App Storage, and Autoscale. pytest, Vitest/Testing Library, and Playwright for focused checks.

**Spec:** [Approved PRD](../../../PRD.md) and [approved design](../../../DESIGN_SPEC.md). Both approved by the user on October 14, 2026. This is the approved historical implementation plan. The demo is now published; see [current build status](../../BUILD_STATUS.md). Unchecked boxes below preserve the original task breakdown and are not a current completion tracker.

## Global Constraints

- Georgia high-school juniors and seniors seeking funding for their first undergraduate education.
- Pursue broad discovery without an arbitrary 10–15-program cap. Report collected coverage honestly; exhaustive discovery is not a completion gate.
- Unknown answers remain unknown.
- No student account is required.
- Use automatically extracted structured eligibility conditions with deterministic checks for a bounded set of supported conditions.
- Matching across the catalog is independent of the limited number of passages retrieved for a conversational answer.
- Start with a target of 500 tokens and 75-token overlap for fragments of the same long section.
- Never mix scholarships in a chunk.
- Semantic and hybrid experiments use identical chunks.
- No Reserved VM, process supervisor, always-running worker, or general job queue is included.
- Keep provider keys and database credentials in server-side secrets.
- Do not persist real student profiles or trace their conversations by default.
- Reuse unchanged embeddings.
- Agentic RAG, GraphRAG/Neo4j, LangGraph orchestration, and long-term memory are outside the first build.

## Review Focus

1. Missing/incompatible GPA or prospective admission must not become eligibility: Task 3 tests unknowns and college status.
2. Source exceptions, mixed-program pages, or malicious instructions must not silently become incorrect rules: Tasks 4–5 test extraction and attribution.
3. A source update during an answer must not mix catalog and passage versions: Task 6 tests interrupted publication and pinned reads.
4. A forged identity, duplicate eval request, or browser closure must not expose admin data or repeat completed paid work: Tasks 2 and 10 test authorization and resumption.
5. Chat failure, narrow retrieval, or empty results must not erase browseable opportunities or imply no scholarships exist: Tasks 7–9 test coverage and service degradation.

---

## Delivery sequence and your involvement

This is one integrated demo, not independent products. Each task below has its own testable result. Build the vertical slice before broad ingestion; do not defer all service integration until the end.

| Milestone | Tasks | Codex can do independently | Your checkpoint |
| --- | --- | --- | --- |
| Foundation and local matching | 1–3 | Contracts, tests, local app, matching, service adapters | Provide access/configuration when ready; no keys needed to begin |
| Real source-to-answer slice | 4–7 | Parsing, extraction, indexing, versioning, cited retrieval | Enable service secrets before live calls |
| Complete student journey | 8–9 | Responsive UX, scenarios, source inspection, print plan | Review one complete junior and senior journey; batch cosmetic feedback |
| Admin evidence | 10–11 | Eval runner, case inspector, baseline/comparison, broader ingestion | Resolve only product tradeoffs if measured targets or coverage fall short |
| Demo release | 12 | Build, release checklist, demo script and submission draft | Authenticate as admin; approve publishing configuration; record or approve demo and submission |

Estimated owner involvement: setup 1–3 hours, UX review 2–3, corpus/eval explanation 2–4, demo/release 3–5, plus 3–5 hours contingency (11–20 total). Keep the previously discussed 15–25-hour availability as a buffer, not a promise of elapsed implementation time. Codex implementation and service waiting are additional elapsed work; reassess after the first live vertical slice. If the deadline becomes tight, propose a specific scope change rather than silently omitting approved requirements.

Independent work may continue through an active session while you are away, using tests. Login, missing keys, and final publication can block dependent steps. This plan does not schedule an overnight automation or guarantee that a session survives interruption. Record completed tasks and blockers in `docs/BUILD_STATUS.md` at handoffs.

### Access and secrets checklist

Enter secrets directly in Replit Secrets or an ignored local `.env`; do not paste keys into chat, Markdown, commits, frontend environment variables, or recordings.

| Dependency | What you supply/do | Needed by | Codex handles |
| --- | --- | --- | --- |
| Replit | Open/create the project, confirm available credits and publishing allowance | Hosted integration in Task 2; release Task 12 | Files, commands, one-port configuration, connection checks |
| PostgreSQL | Provision/authorize project database; expose server `DATABASE_URL` | Task 2 live integration | Migrations, catalog repository, explicit development/production checks |
| App Storage | Enable a bucket and supply non-secret bucket ID | Task 4 live artifacts | SDK adapter and paths; use supported in-Replit authentication |
| OpenAI | Server `OPENAI_API_KEY`, funded API project | Tasks 5–7 live calls | Model adapters, batching, token accounting, cache, retries |
| Pinecone | Server `PINECONE_API_KEY`; approve index name/region  | Task 6 | Create/check compatible index and namespace, verify dimensions, upserts |
| LangSmith | `LANGSMITH_API_KEY`, workspace/project access | Task 10 live traces | Fictional eval-only tracing and experiment links |
| Admin identity | Enable supported Replit identity integration and sign in once; allowlist your immutable subject ID | Task 2 integration, Task 12 release | Backend session verification and authorization |
| GitHub | Repository destination/visibility and authenticated access | Task 12 external publishing | Prepare clean local Git history and handoff assets |

LangChain is a library: no LangChain API key. A ChatGPT subscription is not OpenAI API funding. No optional Tavily account is required initially. Never assume course credits are redeemed or usable; inspect the tracker/account with the owner when configuring paid services.

## Decisions resolved for implementation

- Baseline extraction/answer model: configurable `gpt-4.1-mini`; embedding model `text-embedding-3-small`, explicitly request 1536 dimensions; cosine Pinecone index. Record configured and returned model IDs. These are starting defaults, not claims of best quality; change only with recorded eval evidence and a new configuration version.
- Use structured model output validated by Pydantic. Temperature 0 where supported; maximum extraction output 4,000 tokens per bounded program section, answer output 1,200, judge output 1,200. Evidence cannot be truncated silently: mark extraction incomplete and process another bounded section. Answer requests have a 30-second total timeout and no automatic paid retry after ambiguous timeouts; ingestion retries explicit rate-limit/transient failures at most twice with backoff.
- Semantic retrieval: up to 40 candidates. Hybrid: 20 dense Pinecone + 20 keyword BM25 candidates, fused with reciprocal rank fusion `sum(1/(60 + rank))`; deterministic chunk-ID ties. Use the same metadata filters and corpus for both, final evidence budget 8 passages / 5,000 tokens. BM25 is local in-memory text indexing per active corpus, loaded lazily from persisted chunks; no second search service. Do not call this Pinecone-native hybrid search.
- For comparisons, divide candidate and final passage budgets evenly among selected programs before filling remaining slots. Compare up to four programs per response; ask the student to choose a smaller group for larger requests, preserving their shortlist. Record the limits in the UI and eval config. Catalog matching always scans the catalog, never only vector results.
- Prefer matches with no known unmet mandatory condition, ordered by fewer unresolved mandatory conditions, then documented preference alignment, then normalized name/ID. Do not rank by raw number of rules met (longer rule sets should not win). Separate preparation and incomplete evidence from potential matches. Upcoming deadlines sorts applicable published dates ascending; unknown dates have their own group.
- Request bounds: profile at most 3 colleges; question 2,000 characters, last 6 turns capped at 8,000 total characters, max 4 compared programs. Server-side per-client chat limit 10/minute and project-wide 100/hour initially; keep a bounded PostgreSQL counter using a rotating HMAC of the platform-validated client address, expire after 24 hours, never log raw profiles. Do not trust arbitrary forwarded headers. A shared-network limit may affect classmates; document the behavior.
- One eval case per HTTP execution request, 60-second lease, unique `(run_id, case_id, method)`. Single active eval run enforced in PostgreSQL. The browser drives sequential cases, not a long background request.
- Auth integration is an early feasibility gate: use the actual supported Replit identity configuration, verified issuer/audience/expiry and immutable account subject; never accept a browser-provided user ID or unverified identity header. If that integration cannot support this Python app, record the exact blocker and propose an alternative before exposing admin routes. Local fake identity is test-only and forbidden in production. Independent student/pipeline work continues.

## File map and shared contracts

All paths below are relative to the project root. Create only when the owning task starts. Python package is `backend/nextstep`; use `uv run pytest` from the root, configured via `pyproject.toml`. Frontend commands use `npm --prefix frontend`. Pin resolved dependency versions in `uv.lock` and `frontend/package-lock.json` during setup; do not invent untested version pins in this plan.

| Files | Responsibility |
| --- | --- |
| `pyproject.toml`, `.gitignore`, `.env.example`, `backend/nextstep/app.py`, `config.py`, `models.py` | Boot, configuration and shared typed contracts |
| `backend/nextstep/db.py`, `repository.py`, `auth.py`, `limits.py`, `migrations/` | Persistent catalog/evals, verified admin access, usage controls |
| `backend/nextstep/matching.py`, `api/catalog.py` | Deterministic condition checks and catalog endpoints |
| `backend/nextstep/ingest/{collect,parse,extract,chunk,publish,cli}.py`, `storage.py` | Explicit ingestion stages and artifact adapter |
| `backend/nextstep/rag/{retrieve,answer}.py`, `providers.py`, `api/chat.py` | OpenAI/Pinecone adapters and cited RAG |
| `backend/nextstep/evals/{suite,score,runner}.py`, `api/admin.py` | One evaluation engine and restricted routes |
| `frontend/src/{api,types}.ts`, `App.tsx`, `styles.css` | Shared web contracts, navigation, visual tokens |
| `frontend/src/components/{ProfileForm,Results,ScholarshipDetail,ChatPanel,CitationPanel,ScenarioPanel,PrintPlan}.tsx` | Student journey components |
| `frontend/src/admin/{EvalDashboard,CaseInspector}.tsx` | Admin analysis |
| `data/sources.yaml`, `data/demo_profiles.json`, `evals/cases.jsonl`, `evals/heldout.jsonl` | Source candidates, fictional profiles, checked eval expectations |
| `tests/`, `frontend/src/__tests__/`, `frontend/e2e/` | Focused unit, integration and browser tests |
| `docs/{BUILD_STATUS,ENVIRONMENT,DATA_DICTIONARY,EVAL_REPORT}.md` | Handoff state and measured demo evidence |

Define these Pydantic contracts in Task 1; mirror public fields into generated TypeScript from OpenAPI rather than manually maintaining two schemas:

- `StudentProfile`: optional grade, graduation year, residence, GPA `{value, scale, type, estimated, as_of}`, interests, prospective colleges (max 3), optional contextual conditions. `Scenario` stores overrides separately.
- `EvidenceRef`: source/document version, page/section, exact quote, character offsets, URL and fetch date. A reference is validated against normalized text; it is not a model assertion of truth.
- `Condition`: kind, operator, value, required/preference, evidence refs; recursive AND/OR/NOT groups. Unsupported/ambiguous expressions carry reason and evaluate unknown. `ConditionResult.status` is `met|unmet|unknown`.
- `Scholarship`: stable ID, corpus version, name/sponsor, scope, cycle, conditions, materials, timing/date/timezone precision, evidence refs and information status. Missing values are null, not guessed defaults.
- `NormalizedDocument`: ID/hash/source, ordered `Section` entries (ID, heading, page, text, table headers/rows, program association). `Chunk`: ID, program/source/version, exact evidence text plus separate contextual heading, section refs, token count, neighbor refs.
- `MatchResult`: scholarship ID, condition results, group, fit/timing/evidence labels, follow-up questions and deterministic sort key.
- `RetrievalRequest`: question, program IDs, pinned corpus, method. `RetrievedEvidence`: ordered chunks, ranks and timings. `AnswerResult`: answer blocks with evidence IDs, explicit gaps, pinned version, method/timings and usage; no private reasoning.
- `EvalCase`: ID, fictional profile/question, frozen date, expected conditions/evidence/claims, critical flags, checked source refs. `EvalResult`: run/case/method, answer/evidence, individual scores/reasons, error, timings/usage/config snapshot.

Repository interfaces: `active_version() -> str`, `list_scholarships(version: str) -> list[Scholarship]`, `get_chunks(version: str, ids: list[str] | None) -> list[Chunk]`, `stage_catalog(version: str, records: list[Scholarship]) -> None`, `activate_version(expected_old: str | None, new: str) -> None`. Enforce unique versioned IDs. SQL tables: corpus_versions, active_corpus (singleton), sources, source_versions, scholarships (versioned JSONB), chunk_manifest, ingestion_checkpoints, eval_runs, eval_results, admin_allowlist, rate_counters. No student/chat table.

## Task 1: Bootable app and validated shared contracts

**Files:** Create `pyproject.toml`, `.gitignore`, `.env.example`, `backend/nextstep/{app,config,models}.py`, `frontend/{package.json,index.html,vite.config.ts,tsconfig.json}`, `frontend/src/{App.tsx,types.ts,api.ts}`, `tests/test_contracts.py`, `docs/BUILD_STATUS.md`.
**Interfaces:** `create_app() -> FastAPI`; `Settings` defaults live calls off; shared contracts above; `GET /api/health -> {status: "ok"}` without secrets.

- [ ] Initialize a project-scoped Git repository only after checking there is no parent repository; install/lock dependencies and ignore secrets, downloaded artifacts, local environments and builds.
- [ ] Write `test_profile_limits_and_unknowns`: empty profile valid, 4 colleges invalid, missing GPA not zero, estimated preserved; `test_health_excludes_secrets`: response has only status.
- [ ] Run `uv run pytest tests/test_contracts.py -q`; expect assertion/import failures before implementation, not an unresolved dependency setup failure.
- [ ] Implement contracts, environment validation, health route, exported `app = create_app()`, minimal React shell and OpenAPI type-generation script; configure FastAPI to serve the production UI with `/api` precedence and `$PORT` binding.
- [ ] Run the contract tests and `npm --prefix frontend run build`; expect passes and a built shell. Confirm local paid-call default is disabled.
- [ ] Commit only the named source/config/test files plus lockfiles: `feat: establish app contracts and shell`.

## Task 2: Persistent catalog, secure admin boundary and service setup

**Files:** Create `backend/nextstep/{db,repository,auth,limits}.py`, `migrations/versions/0001_catalog.py`, `alembic.ini`, `migrations/env.py`, `tests/{test_repository,test_auth,test_limits}.py`, `docs/ENVIRONMENT.md`; modify `app.py`, `config.py`.
**Interfaces:** Repository methods above; `require_admin(request: Request) -> AdminIdentity`. `AdminIdentity` is defined in its owning module.

- [ ] Write tests asserting staged rows invisible until activation, unknown/forged identities rejected (401), valid non-owner rejected (403), allowlisted verified owner accepted.
- [ ] Run `uv run pytest tests/test_repository.py tests/test_auth.py tests/test_limits.py -q`; expect failures.
- [ ] Implement migrations/repository with explicit transactions, local test adapters, default-deny auth and rate controls.
- [ ] At the access checkpoint, validate Replit auth support and database connections using the owner's configured environment. Record exact auth mechanism and development/production database/bucket identities without secrets. If blocked, leave production admin disabled; do not fake success.
- [ ] Run the same tests; run PostgreSQL integration tests with an isolated schema (`uv run pytest -m postgres -q`) once access exists. Expect all passes, including concurrent run attempts; clean only test-owned schema.
- [ ] Commit source, migrations and environment instructions: `feat: add catalog persistence and admin authorization`.

## Task 3: Catalog-wide deterministic matching

**Files:** Create `backend/nextstep/matching.py`, `backend/nextstep/api/catalog.py`, `data/demo_profiles.json`, `tests/test_matching.py`; modify `app.py`.
**Interfaces:** `evaluate_condition(condition: Condition, profile: StudentProfile, as_of: date) -> ConditionResult`; `match_catalog(records: list[Scholarship], profile: StudentProfile, as_of: date) -> list[MatchResult]`; `POST /api/matches` accepts profile and optional scenario, returns pinned version, matches and coverage.

- [ ] Write tests asserting unknown GPA/type remains unknown, considering college does not satisfy enrolled/accepted, AND/OR/NOT propagate unknown, unsupported logic remains unknown, expired award cannot be apply-now, junior future rules remain conditional, interest does not remove general awards.
- [ ] Run `uv run pytest tests/test_matching.py -q`; expect failures.
- [ ] Implement bounded rules and ordering defined above; classify incomplete evidence separately and return contextual unanswered questions. Load the entire active catalog, not vector top-k. Use a server date with an injectable eval clock.
- [ ] Run matching tests; add an assertion that an eligible program outside a mocked top-8 retrieval set still appears. Expect passes.
- [ ] Commit: `feat: explain provisional scholarship matches`.

## Task 4: Collect, parse and normalize varied sources

**Files:** Create `backend/nextstep/storage.py`, `backend/nextstep/ingest/{collect,parse,cli}.py`, `data/sources.yaml`, `tests/test_parsing.py`, `tests/fixtures/sources/` with small licensed or synthetic fixtures.
**Interfaces:** `collect_source(source: SourceSpec, store: ArtifactStore) -> CollectedSource`; `parse_source(source: CollectedSource) -> NormalizedDocument`; define `SourceSpec`/`CollectedSource` in `collect.py`, `ArtifactStore.put(key: str, data: bytes) -> str` and `.get(key: str) -> bytes` in `storage.py`.

- [ ] Write tests for HTML boilerplate removal without lost exception, multi-program page separation, PDF page refs/table headers, empty scanned PDF flagged `needs_ocr`, failed download recorded without withdrawal, unchanged hash reused.
- [ ] Run `uv run pytest tests/test_parsing.py -q`; expect failures.
- [ ] Implement HTTP downloads with time/size limits (20 seconds, 20 MB), allowed HTTP(S) sources and blocked private-network targets/redirects; HTML parser, pypdf/pdfplumber dispatch and normalized JSON serialization. Add python-docx only if an actual selected corpus source needs it. Use a local artifact adapter for tests and Replit SDK adapter in its supported environment.
- [ ] Run parsing tests; manually inspect one actual HTML, multi-program HTML, text PDF, table PDF and incomplete/conflicting source output. Log failures and exact artifact paths, not a claim of full verification.
- [ ] Commit parsers, source register and small fixtures: `feat: normalize source documents with provenance`.

## Task 5: Evidence-backed extraction and section chunks

**Files:** Create `backend/nextstep/ingest/{extract,chunk}.py`, `backend/nextstep/providers.py`, `tests/{test_extraction,test_chunking}.py`, `docs/DATA_DICTIONARY.md`.
**Interfaces:** `extract_scholarships(document: NormalizedDocument, model: ExtractionModel) -> list[Scholarship]`; `make_chunks(document: NormalizedDocument, records: list[Scholarship], corpus_version: str) -> list[Chunk]`. `ExtractionModel.extract(section_text: str) -> dict` is defined in `providers.py`; live implementation uses structured OpenAI output via LangChain.

- [ ] Write extraction assertions for exact evidence offsets, no deadline inferred from fetch date, alternatives/exclusions preserved, conflicts retained, unsupported evidence rejected, prompt-injection text ignored as instructions. Test separate programs never share chunks, short FAQ intact, long-section overlap 75 tokens at most and target 500 except explicitly flagged indivisible units.
- [ ] Run `uv run pytest tests/test_extraction.py tests/test_chunking.py -q`; expect failures.
- [ ] Implement schema validation, field provenance, incomplete states and section-aware token splitting using langchain-text-splitters RecursiveCharacterTextSplitter with a tiktoken length function, after structural partitioning; embed input will be contextual title/heading plus passage text, not JSON. Never label all extracted records source-checked.
- [ ] After the key checkpoint, extract the varied real batch. Codex checks representative fields against originals and creates the small checked reference set; owner need not audit the full catalog. Run unit tests; inspect table exceptions and ambiguous GPA/cycle outputs.
- [ ] Commit: `feat: extract sourced conditions and retrieval passages`.

## Task 6: Index and publish consistent corpus versions

**Files:** Create `backend/nextstep/ingest/publish.py`, `tests/test_publication.py`; modify `providers.py`, `repository.py`, `ingest/cli.py`.
**Interfaces:** `EmbeddingProvider.embed(texts: list[str]) -> list[list[float]]`; `VectorStore.upsert(version: str, chunks: list[Chunk], vectors: list[list[float]]) -> None`; `publish_corpus(version: str, expected_old: str | None) -> PublishReport` (`PublishReport` in `publish.py`). CLI `uv run python -m nextstep.ingest.cli run --sources data/sources.yaml --version VERSION` stages; `... publish --version VERSION` validates/promotes; `... rollback --version VERSION` switches only to a ready retained version.

- [ ] Write tests for duplicate rerun stability, dimension mismatch rejection, failed partial upsert leaving old active pointer intact, request pinned to old version through concurrent publication, rollback restores both matching and retrieval.
- [ ] Run `uv run pytest tests/test_publication.py -q`; expect failures.
- [ ] Implement hash/model/dimension-keyed embedding reuse, version namespaces, flat supported Pinecone metadata with nulls omitted, staged manifest counts and query-readiness verification before transactional compare-and-swap activation. Retain prior versions; do not garbage-collect during demo build.
- [ ] With credentials, index varied batch and verify real fetched IDs/counts and searchable passages; rerun unchanged input and confirm no new embeddings. Run tests and save processing report in App Storage.
- [ ] Commit: `feat: publish resumable versioned scholarship corpora`.

## Task 7: Semantic/hybrid retrieval and grounded answers

**Files:** Create `backend/nextstep/rag/{retrieve,answer}.py`, `backend/nextstep/api/chat.py`, `tests/{test_retrieval,test_answers}.py`; modify `providers.py`, `app.py`.
**Interfaces:** `retrieve(request: RetrievalRequest) -> RetrievedEvidence`; `answer_question(profile: StudentProfile, request: RetrievalRequest, history: list[ChatTurn]) -> AnswerResult`; `ChatTurn` in `models.py`; `POST /api/chat` returns `AnswerResult` with server-pinned active version.

- [ ] Write tests asserting semantic/hybrid share filters and budgets, comparison gives each program evidence, stale namespace never enters context, citations must be supplied IDs, missing/conflicting evidence produces gaps, generated prose cannot convert unknown conditions to met, provider failure leaves catalog endpoint functional.
- [ ] Run `uv run pytest tests/test_retrieval.py tests/test_answers.py -q`; expect failures.
- [ ] Implement rank-bm25 corpus cache and Pinecone dense adapter, RRF, deterministic truncation preserving whole evidence units, fixed prompt and structured answer composed with LCEL RunnableLambda/RunnableSequence; loader adapters expose LangChain Document objects while preserving source metadata. Validate citation IDs; return explicit error/gap on invalid output instead of displaying unsupported claims. Apply request limits and redact request logs. Do not enable global LangSmith tracing.
- [ ] Run tests plus real one-program and two-program smoke questions against staged-approved corpus; inspect answer claims against cited passages. Record latency and token use, never claim citation resolution alone proves support.
- [ ] Commit: `feat: add cited semantic and hybrid question answering`.

## Task 8: Responsive profile, results and cited conversation

**Files:** Create `frontend/src/components/{ProfileForm,Results,ScholarshipDetail,ChatPanel,CitationPanel}.tsx`, `frontend/src/styles.css`, `frontend/src/__tests__/student.test.tsx`, `frontend/e2e/student.spec.ts`; modify `App.tsx`, `api.ts`.
**Interfaces:** `ProfileForm({onSubmit}: {onSubmit: (p: StudentProfile) => void})`; results consumes matches/coverage; chat consumes session profile, selected IDs and in-memory history; citations consume `EvidenceRef`/retrieved chunks. Fetch typed API responses generated in Task 1.

- [ ] Write tests for all-skipped profile, fictional-profile labeling, upcoming/prepare/explore groups, precise unknown follow-up, no-match copy without universal claims, citation metadata, absent chat service preserving cards, keyboard-operable phone chat. Assert no profile/history is written to localStorage or backend persistence.
- [ ] Run `npm --prefix frontend test -- --run`; expect failures.
- [ ] Implement approved palette and card hierarchy, responsive desktop side panel/mobile dialog, visual checklist and default-collapsed evidence/timing panel. Use dark text on bright accents; status labels cannot rely on color. Keep profile/history in React memory, clear on refresh.
- [ ] Run unit tests, `npm --prefix frontend run build`, and `npm --prefix frontend run test:e2e -- student.spec.ts` at 390px and 1440px widths; inspect keyboard focus, loading/error states and overflow. Show the owner one junior and senior journey for batched feedback.
- [ ] Commit: `feat: deliver student discovery and evidence experience`.

## Task 9: What-if scenarios and printable action plan

**Files:** Create `frontend/src/scenarios.ts`, `frontend/src/components/{ScenarioPanel,PrintPlan}.tsx`, `frontend/src/__tests__/plan.test.tsx`, `frontend/e2e/print.spec.ts`; modify `App.tsx`, `styles.css`.
**Interfaces:** `applyScenario(profile: StudentProfile, overrides: Partial<StudentProfile>) -> StudentProfile` in `frontend/src/scenarios.ts` returns a copy; `PrintPlan` consumes selected scholarship records, matches, evidence and generated timestamp.

- [ ] Write tests asserting GPA/college scenario never mutates original, reset restores original, selection survives view changes, print includes sources/cycle/unknowns/checklists/generated date and labels hypothetical content.
- [ ] Run `npm --prefix frontend test -- --run`; expect new tests fail.
- [ ] Implement scenario toggle, session shortlist and dedicated print route/view using browser print CSS; handle source updates by refreshing selected records and identifying removed/changed entries rather than mixing versions.
- [ ] Run unit tests and `npm --prefix frontend run test:e2e -- print.spec.ts`; render a PDF in Playwright and visually inspect page breaks, link visibility and no chat controls in the output.
- [ ] Commit: `feat: add conditional scenarios and printable scholarship plans`.

## Task 10: Reproducible eval runner and restricted inspector

**Files:** Create `backend/nextstep/evals/{suite,score,runner}.py`, `backend/nextstep/api/admin.py`, `evals/{cases,heldout}.jsonl`, `tests/test_evals.py`, `frontend/src/admin/{EvalDashboard,CaseInspector}.tsx`, `frontend/e2e/admin.spec.ts`.
**Interfaces:** `start_run(config: EvalConfig) -> str`; `execute_case(run_id: str, case_id: str, method: str) -> EvalResult`; `score_case(case: EvalCase, answer: AnswerResult) -> Scorecard` (define config/scorecard in `evals/suite.py`). Protected API: POST `/api/admin/runs`, POST `/api/admin/runs/{id}/cases/{case_id}?method=...`, GET run/status/results and GET read-only ingestion reports.

- [ ] Create 24 checked cases: 18 tuning, 6 held out. Include mandatory unknowns, GPA types, geography, employer/membership, junior preparation, college status, closed/unknown cycles, conflicting evidence, missing answer, multiple programs, injection and version update. Mark exact critical cases and required evidence units; reference checks must inspect original sources, not generated extraction alone. Keep synthetic update cases labeled separately.
- [ ] Write tests: concurrent start permits one active run; duplicate case call returns stored completed result; expired lease becomes interrupted, not successful; resume runs only incomplete cases; unauthorized GET and POST denied; changed corpus/config cannot join a comparison; judge unavailable produces an error, not a passing score.
- [ ] Run `uv run pytest tests/test_evals.py -q`; expect failures.
- [ ] Implement per-case lease/idempotency and DB results, sequential browser driver and explicit resume. For an interrupted in-flight call, display the uncertain completion status and require explicit retry rather than automatic replay. Send only fictional eval traces to LangSmith via this same runner; persist local result even if trace upload fails.
- [ ] Implement dashboard/inspector displaying expected/actual evidence, condition results, rubric reasons, counts/denominators, error cases, paired regressions, latency and trace links. Show historical run label and immutable configuration. Source review is read-only reports; no full catalog editing UI.
- [ ] Run backend tests and `npm --prefix frontend run test:e2e -- admin.spec.ts`; test browser close/resume and a second browser simultaneous start against the integration DB. Expect completed cases unchanged and anonymous admin access denied.
- [ ] Commit: `feat: make evaluation runs resumable and inspectable`.

### Scoring contract used by Task 10

- Deterministic checks: exact critical condition/timing outcome and citation IDs must match checked expectations. Evidence recall = required evidence units present / required units; alternate supporting chunks can map to the same unit.
- Answer case pass: required facts addressed, no contradiction, unknowns preserved, and answer responsive. Use explicit boolean rubric fields with cited reason; all required fields true. Automated judge model uses the same baseline model initially with a separate prompt, checked references, temperature 0 and no access to expected method label; label this correlated automated assessment, not independent truth. Codex spot-checks all critical failures and a sample of passes against source text.
- Support = supported atomic factual claims / checked factual claims. Report claim counts, unsupported and unscorable claims; unscorable claims cannot count as supported. A factual answer without citations fails. Cases intentionally containing no factual claims are N/A for support, not 100%.
- All critical cases and missing-evidence cases pass; evidence recall at least 90%; answer pass rate at least 90%; factual support at least 95%; citation resolution 100%. All errors/timeouts count as case failures and remain visible; metrics with inapplicable denominators show N/A. Matching, extraction, retrieval and answer scores remain separate.
- Report completed-answer p95 and completion rate, initial target 95% within 15 seconds; report cold starts separately. Store end-to-end timings including retrieval and generation, not judge time. Store corpus, suite, date, prompt, model, chunking, budgets, method versions.

## Task 11: Broaden the real collection and run the comparison

**Files:** Modify `data/sources.yaml`, `evals/cases.jsonl` only before freeze; create `docs/EVAL_REPORT.md`, `tests/test_update_demo.py`, `data/synthetic_update/`; modify ingestion CLI only for demonstrated defects.
**Interfaces:** Use Tasks 4–7 CLI/RAG interfaces and Task 10 runner unchanged. Saved eval results reference immutable corpus and suite versions.

- [ ] Write controlled-update test asserting old GPA/deadline and new GPA/deadline produce matching and cited-answer changes together; failed publication preserves old results. Run `uv run pytest tests/test_update_demo.py -q`; expect failure before creating the staged update workflow fixture.
- [ ] Expand discovery across state, institutional, corporate, employer-family, foundation, credit-union and utility sources; include both GA-specific and national programs open to Georgia students. Deduplicate candidates and record inaccessible/incomplete leads. No fixed program-count stopping rule: report actual breadth, remaining gaps and available time.
- [ ] Run manual staged ingestion, inspect category coverage and flagged exceptions, and publish only after readiness checks. Implement and label synthetic update fixture on a separate demo corpus so invented rules cannot contaminate real sponsor data.
- [ ] Freeze reference suite; run semantic and hybrid on the same version/config with balanced execution order. Investigate failed critical cases, make bounded fixes and rerun affected checks. Run heldout cases once after tuning; further fixes require labeling them no longer held out and creating fresh holdouts if making generalization claims.
- [ ] Run update test and record genuine comparison counts/latencies/errors in `docs/EVAL_REPORT.md`. Select hybrid only if retrieval/answer evidence improves without critical regressions or unacceptable latency; if effectively tied, retain semantic simplicity. If targets fail, document failures and propose a release decision; never change thresholds silently.
- [ ] Commit source inventory, fixtures and report without large downloaded documents/secrets: `test: document corpus coverage and retrieval evaluation`.

## Task 12: Release readiness and course handoff

**Files:** Create `.replit`, `frontend/e2e/release.spec.ts`; modify `README.md`, `docs/{ENVIRONMENT,BUILD_STATUS}.md`.
**Interfaces:** Production command `uv run uvicorn nextstep.app:app --host 0.0.0.0 --port "$PORT"`; build `npm --prefix frontend ci` then `npm --prefix frontend run build`. No dev server or worker required in published runtime.

- [ ] Write release smoke assertions for public profile/results/chat/citations/print journey, denied anonymous admin requests, allowed owner eval, database error state and Pinecone/OpenAI failure with catalog still browseable. Run browser suite against preview; expect any unmet release checks to fail visibly.
- [ ] Finish one-port build configuration and inspect frontend assets/source maps for secrets; verify no profile logging/tracing, request limits, production auth settings and explicit storage/database/index connections. Dependency locks and environment instructions must reproduce the build.
- [ ] Run `uv run pytest -q`, PostgreSQL integration tests, frontend unit/build and browser suites. Record actual commands/results. Run live cold and warm smoke tests, verify historical fallback labeling, and fix critical failures before publication.
- [ ] Prepare a reviewable release packet: preview, coverage/eval report, exact Replit publish settings , unresolved limitations, rollback command and clean Git diff. Obtain owner publication approval before paid deployment or external GitHub publication; credentials alone are not publication approval.
- [ ] After approval, publish using Autoscale and recheck public and admin journeys. Do not claim success from build alone. Preserve prior corpus for rollback.
- [ ] Populate the native Google submission document with actual corpus counts, executed prompts, screenshots, iterations, measured evals and learnings; preserve planned/completed distinctions. Draft a <=5-minute demo script covering profile, cited answer, ingestion flow, one controlled update and case inspector; prepare a Google-Doc-ready submission draft with dataset, prompts, iterations, findings and AI-tool usage. Owner records/approves recording and submits, or explicitly authorizes assistance. Do not invent a completed video or submission.
- [ ] Commit verified docs/config/tests: `docs: prepare verified scholarship demo handoff`. Update build status with remaining actions and measured results.

## Coverage and plan self-review

| Approved PRD requirements | Owning tasks |
| --- | --- |
| P01–P04 profile semantics/follow-ups/starters | 1, 3, 8 |
| P05–P09 fit, unknowns, timing, junior preparation, leads | 3, 5, 8, 11 |
| P10–P13 details, cited conversation, source inspection, gaps | 5, 7, 8 |
| P14 no matches | 3, 8 |
| P15–P16 scenarios and printable shortlist | 9 |
| P17 evidence explanation | 7, 8 |
| P18 admin security | 2, 10, 12 |
| P19–P21 eval execution/comparison/inspector | 10, 11 |
| P22–P23 coverage and ingestion/update evidence | 4–6, 10–11 |

Self-review: all P01–P23 have owners; the five Review Focus risks have explicit tests; every task has a verification and commit boundary. Contract names and corpus-version handling are shared across ingestion, matching, chat and evals. Local fixtures enable independent development but cannot satisfy live integration/release gates. Auth account compatibility, service credentials  are explicit external gates rather than assumed capabilities. No additional production platform or continuous processing service was introduced.

## Reference checks and execution choice

Consult current official documentation at integration time, especially account-specific authentication and publishing behavior:

- [Replit Auth](https://docs.replit.com/features/auth-and-identity/authentication)
- [Replit App Storage](https://docs.replit.com/features/data-and-storage/object-storage)
- [Replit PostgreSQL](https://docs.replit.com/features/data-and-storage/sql-database)
- [Replit publishing](https://docs.replit.com/features/publishing/deployment-types)
- [Pinecone hybrid-search concepts](https://docs.pinecone.io/guides/search/hybrid-search)
- [OpenAI GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [OpenAI embedding model](https://developers.openai.com/api/docs/models/text-embedding-3-small)

Recommended execution: **Native**, with Codex implementing sequentially and a fresh final reviewer. This is a tightly connected course demo; keeping interfaces in one context avoids repeated handoffs, while the test gates and final review address integration risk. **Subagent-driven** is also available: a fresh implementer and reviewer per task, followed by whole-branch review, with additional context overhead. Owner selects the approach after reviewing this plan. Execution used Native; current outcomes are recorded in build status.
