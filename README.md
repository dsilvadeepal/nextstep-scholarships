# NextStep Scholarships

NextStep Scholarships is a cited RAG demo that helps Georgia high-school juniors and seniors find potential scholarships, understand why an opportunity may fit, and identify what they need to prepare next.

The published demo corpus contains **39 award records across 31 award families**, represented by **201 chunks from 63 official documents**. It includes Georgia opportunities, selected neighboring-state universities, and national or company-sponsored awards. This is a course-demo corpus, not a comprehensive directory or a final eligibility determination.

The student app is published at [nextstep-scholarships.replit.app](https://nextstep-scholarships.replit.app/). The release was merged into `main`; hosted admin access is disabled. See [build status](docs/BUILD_STATUS.md) for release evidence and limitations.

Repository: [dsilvadeepal/nextstep-scholarships](https://github.com/dsilvadeepal/nextstep-scholarships) (public).

## Student experience

The main page starts with a short guided intake:

- School year: junior, senior, or unknown
- Georgia residency: yes, no, or unknown
- Optional GPA, marked as estimated or from a school record
- An optional free-text note about interests and college plans

The app suggests editable profile details from supported phrases, including citizenship, residency, college preferences, interests, and some activities. Students review and confirm these before matching. The cards and chat use the same confirmed profile. This is bounded local extraction, not general language understanding; a college preference never establishes admission or enrollment.

Additional fields are under **Add more details**. Results show Strong/Possible matches separately from the collapsed **Explore** section. Students can browse college, company-sponsored, and foundation/community groups, filter by college location or upcoming deadlines, and narrow college-specific awards to their confirmed choices. Portable awards remain available.

Students can save a shortlist, compare awards conversationally, inspect evidence through compact Sources popups, and print a preparation plan. Unknown eligibility conditions remain explicit. Fictional profiles provide starting points for trying the app.

## How the RAG pipeline works

1. Official HTML and PDF sources are collected, cleaned, normalized, and preserved with provenance.
2. Scholarship rules are extracted into structured records. Explicit eligibility checks run deterministically across the catalog, with `met`, `unmet`, and `unknown` outcomes.
3. Source text is split with structure-aware recursive chunking: approximately 500 tokens, with up to 75 tokens of overlap inside long sections.
4. OpenAI `text-embedding-3-small` produces 1,536-dimensional vectors stored in Pinecone. The current app uses equal-weight **50/50 hybrid retrieval**, combining semantic Pinecone results with local BM25 keyword results through reciprocal-rank fusion.
5. The final context is bounded to eight passages and 5,000 tokens. The answer flow uses `gpt-4.1-mini` for structured, cited explanations and a bounded support review. Citation checks do not guarantee that every claim is correct.

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

The project compares semantic retrieval with equal-weight hybrid retrieval on the same reviewed corpus and evidence budget. The historical 26-case source-grounded tuning suite passed for both methods; these are exposed development cases, not an independent accuracy estimate. A separate 60/40 semantic-keyword experiment completed 25 of 26 cases and did not justify replacing the equal-weight hybrid default.

Raw held-out results and saved-output rescoring are reported separately so rescoring is not presented as a fresh model run.

See the [evaluation report](docs/EVAL_REPORT.md) and [RAG comparison](docs/RAG_COMPARISON_2026-10-15.md).

## Live demo

Open [NextStep Scholarships](https://nextstep-scholarships.replit.app/) without an account. Hosted admin is disabled; the evaluation tools remain local.

## Run locally

Python 3.12, Node.js 24, `uv`, and npm are recommended for local development. Docker is not used.

```bash
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
sh scripts/start.sh
```

Open `http://localhost:8000` (or the port set by `PORT`). These commands start the UI and API; a fresh checkout does not automatically load the catalog or enable chat. Follow [environment setup](docs/ENVIRONMENT.md) to connect a prepared database and provider services.

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
