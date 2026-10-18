# NextStep Scholarships

NextStep Scholarships is a cited RAG demo that helps Georgia high-school juniors and seniors find potential scholarships, understand why an opportunity may fit, and identify what they need to prepare next.

The active local reviewed corpus contains **39 award records across 31 award families**, represented by **201 chunks from 63 official documents**. It includes Georgia opportunities, selected neighboring-state universities, and national or company-sponsored awards. This is a course-demo corpus, not a comprehensive directory or a final eligibility determination.

The expanded catalog was activated locally on October 16 after user approval.
Its 21 source cases and 26 known regressions passed earlier live testing; post-activation
API and phone/desktop smoke checks also passed. The previous 18-record / 174-chunk
catalog and Pinecone namespace remain available for rollback. See the
[build and activation report](docs/EXPANDED_BUILD_TEST_REPORT_2026-10-16.md).

Repository: [dsilvadeepal/nextstep-scholarships](https://github.com/dsilvadeepal/nextstep-scholarships) (private).

## Student experience

The main page now starts with a shorter guided intake:

- School year: junior, senior, or unknown
- Georgia residency: yes, no, or unknown
- Optional GPA, marked as estimated or from a school record
- An optional free-text note about interests and college plans

The app recognizes a small reviewed set of college and interest mentions locally. It shows those as suggestions and requires the student to confirm them before they affect matching. A college under consideration is never treated as an acceptance or enrollment. Unrecognized text remains available as conversational context, and missing information produces a potential match with follow-up questions rather than a fabricated eligibility decision.

Additional profile fields remain under **Add more details**. Students can review matches, filter by scholarship group or upcoming deadlines, expand Explore for options needing more checks, inspect compact Sources popups, ask follow-up questions, build a shortlist, and print a plan. Fictional junior, senior, and undecided profiles are included for demonstrations.

## How the RAG pipeline works

1. Official HTML and PDF sources are collected, cleaned, normalized, and preserved with provenance.
2. Scholarship rules are extracted into structured records. Explicit eligibility checks run deterministically across the catalog, with `met`, `unmet`, and `unknown` outcomes.
3. Source text is split with structure-aware recursive chunking: approximately 500 tokens, with up to 75 tokens of overlap inside long sections.
4. Chunks are embedded in Pinecone. The current app uses equal-weight **50/50 hybrid retrieval**, combining semantic Pinecone results with local BM25 keyword results through reciprocal-rank fusion.
5. The final context is bounded to eight passages and 5,000 tokens. The answer step selects exact evidence units, and the application renders the supported text with citations.

LangChain is used narrowly for document splitting, OpenAI integration, structured output, and LCEL runnable composition. The application does not use an agent loop or LangGraph state machine.

## Application architecture

- React and TypeScript responsive frontend
- FastAPI backend serving the API and production frontend
- PostgreSQL for the structured catalog, evaluation records, and evaluation state
- Pinecone for vector retrieval
- Replit App Storage for corpus and receipt artifacts
- OpenAI for extraction, embeddings, and grounded answer selection
- Local admin evaluation dashboard and case inspector

The Replit development environment contains the reviewed catalog and renders the shorter intake and scholarship cards. The student app is published with chat enabled. Admin evaluations remain local and hosted admin access stays fail-closed.

## Evaluation

The project compares semantic retrieval with equal-weight hybrid retrieval on the same reviewed corpus and evidence budget. The 26-case source-grounded regression suite passed for both methods. A separate 60/40 semantic-keyword experiment completed 25 of 26 cases and did not justify replacing the equal-weight hybrid default.

Raw held-out results and saved-output rescoring are reported separately so rescoring is not presented as a fresh model run.

See [evaluation report](docs/EVAL_REPORT.md), and [RAG comparison](docs/RAG_COMPARISON_2026-10-15.md).

## Live demo

Open [NextStep Scholarships](https://nextstep-scholarships.replit.app/) without an account. Hosted admin is disabled; the evaluation tools remain local.

## Run locally

Python 3.12, Node.js, `uv`, and npm are required. Docker is not used.

```bash
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
sh scripts/start.sh
```

The application is then available on `${PORT:-8000}`.

Keep secrets only in the ignored local `.env` file or Replit Secrets. Do not commit or paste API keys into prompts. Live calls are disabled by default and require configured provider keys.

## Verify the build

```bash
uv run pytest -q
npm --prefix frontend test -- --run
npm --prefix frontend run build
uv run ruff check backend tests migrations scripts
git diff --check
```

PostgreSQL integration and browser-test instructions are documented in [environment setup](docs/ENVIRONMENT.md).

## Project documents

- [Product requirements](PRD.md)
- [Design specification](DESIGN_SPEC.md)
- [Implementation plan](docs/superpowers/plans/2026-10-14-nextstep-scholarships.md)
- [Build status](docs/BUILD_STATUS.md)
- [Replit setup and verified handoffs](docs/REPLIT_SETUP.md)
- [Source inventory](SOURCE_INVENTORY.md)

Current local work is on `feat/rag-answer-comparison`. Merging to `main`, publishing the Replit deployment, recording the demonstration, and submitting the course project remain separate owner decisions.

### Browsing scholarship results

Results show the filtered Strong/Possible match count separately from Explore opportunities. Explore starts collapsed. Expand the college, company-sponsored, or foundation/community groups to browse cards; filter by scholarship type or college location. Confirmed college choices narrow college-specific awards (common aliases are supported); portable company and foundation awards remain available. Uncheck the college-choice filter to browse other colleges. College location filters show only college-specific awards. Routine source-checked badges are hidden, while source conflicts and verification gaps remain visible. This is relevance filtering, not an admission or eligibility determination. The current catalog's grouping metadata is maintained in `frontend/src/scholarshipGroups.ts`; new unclassified programs appear under Other scholarships.

The intake now suggests editable citizenship, Georgia residency, college choices (including Kennesaw State), interests, explicit absence of volunteer experience, and Science Olympiad participation from supported phrases. Review the suggestions and select **Use these reviewed details in my matches** before submitting. Editing the note or a suggestion clears confirmation; explicit profile fields take precedence. Matching and chat share the same submitted profile. Extraction uses bounded local rules, incurs no model calls, and does not interpret every possible wording or infer admission, leadership, or eligibility from an activity.
