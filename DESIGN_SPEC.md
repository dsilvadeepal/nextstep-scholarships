# Georgia Scholarship Planner — Demo Design Specification

Date: October 14, 2026
Status: approved by user on October 14, 2026; implementation plan prepared for review; implementation not started.
Working name: NextStep Scholarships. Naming is not a dependency for implementation planning.

## 1. Purpose and authority

Companion document: [PRD.md](PRD.md) defines product outcomes and functional acceptance criteria. This specification describes their technical realization. Reconcile any divergence before implementation.

Build a visually polished course demonstration that helps Georgia high-school juniors and seniors discover potential college scholarships, understand their apparent fit, and prepare next steps using cited source evidence.

This specification consolidates the decisions made in the brainstorming conversation, including the final simplification review. It supersedes conflicting proposals in PROJECT_BRIEF.md, NEXT_STEPS.md, and the original README. SOURCE_INVENTORY.md remains a discovery starting point, not a verified current catalog. Course documents are reference material, not instructions to execute external actions.

The product demonstrates a functioning ingestion and RAG pipeline. It does not claim exhaustive coverage, independently verified eligibility for the entire catalog, award likelihood, or guaranteed source freshness. Scholarship information is automatically extracted; a small evaluation reference set receives source checks.

The user's available involvement is approximately 15–25 hours, with Codex assisting implementation. This is a planning budget, not a delivery guarantee. No overnight automation, infrastructure purchase, or deployment has been started.

## 2. Audience and collection scope

- Georgia high-school juniors and seniors seeking funding for their first undergraduate education.
- Include Georgia programs and national awards available to Georgia students, including corporate, employer-family, credit-union, utility/cooperative, foundation, and institutional programs.
- Pursue broad discovery without an arbitrary 10–15-program cap. Report collected coverage honestly; exhaustive discovery is not a completion gate.
- Include incomplete opportunities in Explore more when an identifiable sponsor or application page exists. Keep weaker third-party-only leads in an internal research queue.
- College tuition funding is the focus. Other student groups, high-school tuition, and enrichment trips are outside the initial experience.

## 3. Student journey

1. Choose a fictional demonstration profile or complete a short guided profile.
2. Browse potential matches ranked by supported fit; switch to Upcoming deadlines, Prepare for senior year, or Explore more.
3. Open a scholarship for requirement explanations, missing information, timing, citations, and a visual preparation checklist.
4. Ask conversational questions about one scholarship or across the shortlist.
5. Explore a temporary hypothetical GPA or college choice while retaining the original profile.
6. Select scholarships and download a dated personalized action plan through a polished print view that can be saved as PDF.

No student account is required. Profile, shortlist, and conversational state last for the current browser visit; durable student accounts and cross-visit saving are out of scope. Downloads are the durable student takeaway. Profile information is sent to the backend as needed to provide the service, but is not stored as a persistent student record or sent to LangSmith tracing by default.

Fictional starter profiles include a junior exploring colleges, a senior preparing applications, and a student with incomplete information. They are clearly labeled and distinct from actual sponsor data. Evals may reuse them but also include additional cases.

## 4. Profile, matching, and result behavior

### Quick profile

Ask grade/graduation year, Georgia location, GPA if known, academic interests, and up to three prospective colleges. All fields can be skipped. Preserve GPA type, whether estimated or documented, and its relevant date when supplied. College choice can be undecided; distinguish considering a school from acceptance or enrollment.

Ask optional follow-ups only when relevant to a scholarship, including county/school, employment, household utility provider, membership, financial need, or citizenship conditions. No supporting-document uploads in the first version. Unknown answers remain unknown.

### Matching implementation

Use automatically extracted structured eligibility conditions with deterministic checks for a bounded set of supported conditions. Start with grade/year, explicit location requirements, compatible GPA thresholds, college restrictions, and explicit employment/membership conditions. Preserve AND/OR alternatives, exclusions, and source references. Complex or ambiguous conditions return unknown rather than being approximated.

This is not a general-purpose rules engine. Matching across the catalog is independent of the limited number of passages retrieved for a conversational answer. A matching GPA alone never establishes complete eligibility. Interest in a major boosts relevance when justified; it does not exclude general awards that accept any major.

Each condition has met, unmet, or unknown status. Summaries describe potential fit and unresolved conditions, not certified eligibility or an invented percentage match. Explain ranking through supported conditions and user preferences; finalize and test a simple transparent ordering during implementation planning. Unknown is not equivalent to unmet.

### Separate result dimensions

| Dimension | Meaning |
| --- | --- |
| Fit | Potential match, missing profile information, explicit condition unmet, or clarification needed |
| Timing | Open, published upcoming window, closed, or next cycle unpublished/unknown |
| Evidence | Automatically extracted, incomplete, historical, conflicting, or source-checked for a specified test/example |

Potential matches lead the default view. A documented program with one unanswered profile condition can remain there with a precise follow-up prompt. Incomplete source evidence belongs in Explore more. Juniors see a separate Prepare for senior year group; historical rules support conditional preparation but cannot establish future-cycle eligibility. Seniors need applicable entry-year conditions and actionable windows.

No-match results explain catalog gaps, offer useful follow-ups, and show relevant leads or future opportunities. They never imply no scholarships exist outside the collection. Closed awards do not appear as Apply now. Multiple college choices must not be treated as accepted admissions.

## 5. Student interface and visual direction

One responsive React/TypeScript application supports phones and laptops. Results lead the screen: scholarship cards occupy the main view, with Ask about your matches beside them on laptops and behind an accessible button on phones.

Use a sleek, energetic visual style with playful touches: electric blue #3454F5, violet #7546E8, aqua #35D6CA, yellow #FFD65A, cool white #F7F9FF, and deep navy #172244. These are design tokens to validate for contrast, not a guarantee that every pairing is readable. Use dark text on bright accent surfaces, visible focus states, keyboard navigation, and text/icons alongside color-coded statuses.

Card reading order: scholarship name, why it appeared, unresolved information, timing, next action. Detail views provide cited conditions and compact checklists. Avoid unsupported numerical match scores and celebratory language implying an award was won.

Answers contain visible citations. Selecting one reveals the supporting passage, source title, official URL, cycle when known, retrieval date, and page/section. Cards and printed plans also cite sources.

An optional collapsed How this answer was built panel shows retrieved passages, retrieval method, and response timing. It does not reveal private chain-of-thought or server secrets. Full eval scores remain restricted to the admin view.

The action plan includes selected scholarships, apparent fit, unresolved requirements, deadlines/cycle status, source links, checklists, and generation date. Hypothetical results are visibly conditional and do not overwrite the original profile.

## 6. Ingestion design

Run ingestion explicitly as a repeatable Python command from the development workspace. Do not require a crawler worker or a public ingestion endpoint. Start with a varied source batch: ordinary HTML, a page describing several scholarships, a text PDF, a table-heavy PDF, and an incomplete/conflicting example. Add DOCX processing only when needed.

### Stages and outputs

| Stage | Behavior and output |
| --- | --- |
| Discover/register | Source register with stable program/source IDs, sponsor, URL, format, and discovery status |
| Collect | Preserve downloaded originals, retrieval timestamps, content hashes, and fetch failures |
| Parse/clean | Extract ordered sections, text, tables, and references; remove boilerplate without losing requirements or exceptions |
| Normalize | JSON representing document sections, tables, source identity, and page/section references |
| Extract | Structured scholarship records with evidence for each field, explicit unknowns, alternatives, and conflict flags |
| Chunk | Section-aware passage records with stable IDs and provenance |
| Embed/index | Embed contextual passage text with OpenAI, then upload vectors, text, and retrieval metadata to Pinecone |
| Check/publish | Validate staged records and indexed passages, then activate the complete corpus version |

Use pypdf for ordinary text PDFs, pdfplumber for important tables/layout, python-docx for DOCX, and an HTML parser/content cleaner for webpages. Detect empty/garbled extraction and scanned documents. OCR is added only if essential sources justify it; otherwise retain an explicit processing failure or incomplete lead. PyMuPDF and docx2txt are not initial dependencies.

Normalized document JSON, scholarship JSON, and chunk JSON are distinct outputs. JSON is an interchange format; PostgreSQL becomes the authoritative catalog. Do not maintain competing editable JSON and SQL catalogs. Raw documents are not embedded directly, and the entire JSON object is not sent for embedding. Embed the chunk's scholarship name, heading, and passage text. Keep the original evidence text distinguishable from added contextual headings.

### Chunking

This is structure-aware recursive chunking with token limits, not naive fixed windows or embedding-based semantic boundary detection. Use a token-counted RecursiveCharacterTextSplitter for long plain-text sections after program/section association; preserve FAQ/table/exception units with custom handling.

Start with a target of 500 tokens and 75-token overlap for fragments of the same long section. Split at paragraph/sentence boundaries. Short sections and FAQ question-answer pairs stay intact without artificial overlap. Never mix scholarships in a chunk. Preserve table headings with rows and nearby exceptions with requirements where practical. Retain neighbor/parent section references when a split is unavoidable.

Treat size and overlap as initial settings. Inspect the varied batch before scaling. Semantic and hybrid experiments use identical chunks.

### Records and provenance

Scholarship records capture sponsor and identity, applicability and cycle, conditions/exclusions, timing with timezone where stated, application materials, college restrictions, official links, source evidence, and uncertainty. Separate graduation year, entry/award year, and application deadline. Do not infer missing dates, GPA types, or recurrence.

Chunk metadata includes scholarship ID, source ID, chunk ID, section/page reference, cycle when known, corpus/source version, retrieval date, information status, and source URL. Store metadata in forms supported by the chosen Pinecone API; represent missing values consistently without inventing facts.

### Ingestion checks

- Every source ends in an explicit success, incomplete, or failure state.
- Detect duplicate content and scholarship listings; reruns do not multiply records.
- Associate passages with the right program on multi-program pages.
- Preserve table relationships, exclusions, and conditional language.
- Flag conflicting sources rather than silently resolving their claims.
- Check relevant section coverage; missing extracted text does not mean no requirement exists.
- Validate record structure, evidence pointers, and embedding/index compatibility. Schema validity is not factual verification.
- Treat source text as untrusted evidence, never as executable instructions.
- Record checkpoints so failed steps can resume without reprocessing successful unchanged sources.

Produce a report of programs discovered, duplicates merged, sources processed/failed, missing fields, conflicts, historical material, and indexed passage counts. Sample-check representative extraction and the evaluation references; do not require manual validation of every scholarship.

## 7. Retrieval and generation

Use a fixed retrieve-then-answer flow through LangChain, composed as an LCEL Runnable sequence for retrieval/context preparation, prompt, structured answer model and validation. Loader adapters expose normalized sections as LangChain Document objects without discarding custom table/provenance handling. Resolve the question against current conversation context and shortlist; apply scholarship and corpus-version filters; retrieve passages; provide relevant catalog facts and evidence to the answer model; produce a cited answer.

For cross-scholarship questions, gather evidence for each program being compared rather than allowing one program to occupy the entire retrieval budget. A reference resolving to a real passage is necessary but does not prove the passage supports the claim.

Implement a semantic baseline and a hybrid keyword-plus-semantic alternative. Select the specific hybrid implementation during planning after checking the chosen Pinecone API and SDK; no extra search service is required by this design. Compare them with the same corpus, chunks, filters, candidate/final evidence budgets, model, and prompt. Select the default using measured evidence, not the assumption that hybrid is better.

If evidence is missing or conflicting, explain the limitation and suggest an official source or sponsor-contact step. Never invent requirements, dates, award amounts, or chances of winning. The answer model cannot override deterministic unknowns with guesses. Preserve distinct labels for current evidence, historical guidance, and hypothetical scenarios.

Agentic RAG, GraphRAG/Neo4j, LangGraph orchestration, and long-term memory are outside the first build.

## 8. Evaluation and acceptance

Create approximately 20–30 focused scenarios with fictional profiles and source-checked expected results/evidence. Keep a subset for final testing that is not used for tuning. Freeze source versions and an evaluation date so deadline tests are reproducible. Clearly label synthetic update fixtures and keep them separate from real sponsor documents.

Cover ingestion, extracted fields, condition logic, junior/senior differences, GPA types, employer/membership conditions, prospective versus accepted colleges, closed windows, unpublished cycles, contradictory evidence, multi-program retrieval, citation support, no-answer behavior, and source replacement.

Use code checks for exact dates, IDs, statuses, and rule outcomes. Use automated judge assessments for prose support/correctness where appropriate, label them as automated, and spot-check against references. Do not evaluate extraction solely against answers produced by the same extraction process.

### Initial targets

| Metric | Proposed target |
| --- | --- |
| Critical eligibility/freshness cases | All designated cases pass; unknown never becomes met and superseded rules never become current |
| Expected evidence recall | At least 90% of required evidence units retrieved within a fixed, recorded retrieval budget |
| Answer correctness | At least 90% of scored cases pass the specified rubric |
| Citation support | At least 95% of checked factual claims supported; no unsupported eligibility/deadline claim in critical cases |
| Citation resolution | All references resolve to supplied evidence |
| Missing-evidence tests | All designated cases explain the gap appropriately |
| Answer latency | Initial goal: 95% complete within 15 seconds; report cold starts separately |

These are provisional targets to assess after the baseline, not existing results. Record counts and denominators, include errors/timeouts, and avoid claiming population-level reliability from a small suite. Set concrete retrieval budgets, scoring rubrics, and model settings in the implementation plan before the comparison. Matching correctness, retrieval quality, and answer quality remain separate metrics.

### Admin evaluation screen

- Restricted run controls: choose suite and semantic/hybrid/comparison mode.
- Progress and per-case saved results; only one active eval run initially.
- Summary: counts, correctness, evidence recall, citation support, unknown handling, latency, and available usage/cost estimates.
- Comparison: improvements, regressions, unchanged results, and failures for the same cases.
- Case inspector: profile, question, expected outcome/evidence, actual answer, retrieved passages, citations, and reason for the score.
- Reproducibility metadata: corpus/test-set version, evaluation date, chunk settings, retrieval settings, prompt/model identifiers, run ID, and timestamps.
- LangSmith experiment/trace links, generated by the same evaluation runner rather than an independent duplicate scoring pipeline.

Run bounded cases or batches through requests and save progress to PostgreSQL. The admin UI explicitly resumes incomplete runs. Browser closure does not guarantee continued execution. Retries must not duplicate completed cases or charge for an entire suite unnecessarily. A saved prior real run can be used during a service outage, clearly labeled as historical, never presented as a live result.

## 9. Application architecture and deployment

Use one Replit project with React/TypeScript frontend and a Python FastAPI backend. FastAPI serves the API and the built frontend through one public service. LangChain is used narrowly; ordinary Python handles matching, ingestion control, and data validation.

| Service | Responsibility |
| --- | --- |
| Replit PostgreSQL | Scholarship catalog, source/version register, active corpus pointer, eval progress/results, and minimal admin authorization data |
| Replit App Storage | Downloaded originals, normalized content, chunk files, and processing reports |
| Pinecone | Passage vectors, evidence text, and retrieval metadata |
| OpenAI | Embeddings, structured extraction, and cited answer generation; optional judge calls |
| LangSmith | Evaluation experiments/traces and diagnostics linked to app results |

Develop and test using Replit preview or the local workspace. Publish using Autoscale when ready for public access, after checking account credits and costs. No Reserved VM, process supervisor, always-running worker, or general job queue is included. Autoscale startup delay is measured separately in demo readiness checks.

Ingestion runs explicitly from the development workspace against configured services. Credentials and production storage access must be verified through supported connections; do not assume local and published environments share credentials or data automatically. A scheduled deployment is a later option, not a first-version requirement.

Students access the public app without login. Admin routes require authenticated identity and a backend allowlist for the user's account. Prefer Replit Auth if compatible with the selected project setup; validate that integration during planning. Hiding a link is not authorization.

Keep provider keys and database credentials in server-side secrets. Apply bounded request lengths, public rate limits, model-output limits, and restricted eval concurrency. Do not persist real student profiles or trace their conversations by default. Fictional test traces are permitted. Browser explanations expose evidence and timings, not credentials, internal prompts, or private reasoning.

If OpenAI/Pinecone fails, browsing and matching can remain available from PostgreSQL; the chat panel reports its limitation. Database outages produce an explicit error rather than fabricated results.

## 10. Updates and demo freshness

Preserve source versions and compare content hashes. Produce before/after reports for meaningful eligibility/date changes. Stage catalog records and Pinecone passages under a new corpus version; check completeness and retrieval readiness before changing the active version pointer. Pin each answer and eval run to one version. Retain the prior version for rollback.

Initial broad ingestion remains automatically extracted, not human-certified. For changed important conditions, demonstrate the manual review/promotion workflow on selected examples; pending disputed details are marked as needing verification. We are not requiring whole-catalog human approval.

A failed fetch indicates access failure, not program withdrawal. A recent fetch date does not prove applicability to the current cycle. Historical versions are excluded from current matching unless explicitly shown as conditional preparation material. Never roll deadlines forward automatically.

The demo proves one controlled source update affecting structured matching and retrieved answers. Continuous crawling, freshness guarantees, notifications, and a full source editing/approval UI are deferred.

## 11. Tools, cost, and boundaries

Use the user's OpenAI API credentials and Pinecone account. LangChain is a library; LangSmith is the tracing/evaluation service. Course credits may help with Replit, LangSmith, and optional Tavily discovery, but balances and expiration must be checked rather than assumed. ChatGPT subscription access is not an OpenAI API budget.

Do not add Nebius, Toloka, Tandem, Mem0, LlamaIndex, Neo4j, or another backend solely because credits exist. Exact model IDs, machine configuration, numerical spend ceilings, and SDK versions are implementation-plan decisions based on account availability and measurements, not reasons to expand product scope.

Reuse unchanged embeddings. Keep corpus summaries visible: actual program/source counts, information status, collection date, and known gaps. Do not advertise comprehensive statewide coverage or fabricated evaluation results.

## 12. Completion and handoff

The demo is complete when a visitor can use fictional or guided profiles, inspect potential matches and sources, ask cited questions, explore supported scenarios, and export an action plan; the authorized admin can run/resume evals and inspect comparisons; ingestion reports and a controlled update demonstrate the data pipeline; and required checks have run with failures documented and critical cases resolved.

Course assets: project documentation with corpus, prompts, iterations, and findings; a live demonstration video of five minutes or less; and GitHub project assets. The handout's Builder of the Week cutoff is October 18, 2026 at 11:59 p.m. Pacific (October 19 at 2:59 a.m. Eastern). Later certification submission is described as allowed in the handout. These are recorded course requirements, not a promise of submission or publication.

Next step: review the [implementation plan](docs/superpowers/plans/2026-10-14-nextstep-scholarships.md) and select an execution approach. The user approved this specification and the PRD on October 14, 2026. Implementation has not started.

## Reference documentation consulted during design

- [Pinecone hybrid search](https://docs.pinecone.io/guides/search/hybrid-search)
- [LangChain retrieval architectures](https://docs.langchain.com/oss/python/deepagents/retrieval)
- [LangSmith evaluation types](https://docs.langchain.com/langsmith/evaluation-types)
- [Replit deployment types](https://docs.replit.com/features/publishing/deployment-types)
- [Replit PostgreSQL](https://docs.replit.com/features/data-and-storage/sql-database)
- [Replit App Storage](https://docs.replit.com/features/data-and-storage/object-storage)
- [Replit Auth](https://docs.replit.com/features/auth-and-identity/authentication)
- [pypdf extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [pdfplumber](https://github.com/jsvine/pdfplumber/blob/stable/README.md)
- [python-docx](https://python-docx.readthedocs.io/en/latest/api/document.html)
