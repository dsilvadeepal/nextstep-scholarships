# Build status — October 14, 2026

**Partial local implementation, not a completed demo.** Native execution on `feat/nextstep-native`. Main remains at planning commit `679c49e`. Nothing pushed, merged, deployed or submitted. No paid calls made.

## Verified in this build pass

- Python 3.12.15; locked Python/Node dependencies; FastAPI serves the production React build.
- **36 backend tests passed**, including profile unknowns, tri-state rules, source offsets/chunk budgets, catalog versioning, publication failure/cache/rollback, budget concurrency and eval idempotency/leases.
- **4 frontend unit tests passed**; TypeScript and Vite production build passed.
- **8 Playwright checks passed** across 390px phone and 1440px desktop: unavailable catalog, synthetic print, failed scenario reset and stale response ordering.
- Phone/desktop screenshots and print screenshot visually inspected. Generated synthetic PDFs: `/tmp/nextstep-plan-phone.pdf` and `/tmp/nextstep-plan-desktop.pdf`. No real-source PDF journey claimed.
- Ruff and Git whitespace checks passed. Chromium needed sandbox escalation for macOS launch permissions; escalation succeeded.
- Independent whole-branch review completed. Three important findings reproduced with failing tests and fixed: dropped direct-container HTML exceptions, mutable corpus manifest during indexing, and scenario result/label races. Full suites passed after fixes. No release-readiness claim.

## Task ledger

| Task | Status | Remaining work |
| --- | --- | --- |
| 1 Contracts/shell | Complete | Extend API response contracts as routes land |
| 2 Persistence/auth | Partial | PostgreSQL integration, supported identity verifier, request limits, live budget wiring |
| 3 Matching | Complete local implementation | Broaden against source-checked references |
| 4 Collection/parsing | Partial | Safe HTTP collector, source register, App Storage, real varied-format inspection |
| 5 Extraction/chunking | Partial | Structured extraction provider, field provenance validation, real batch and reference checks |
| 6 Corpus publication | Partial | Pinecone adapter, CLI, real query-readiness verification; SQL manifest now freezes before indexing |
| 7 RAG | Partial | Providers, fixed LCEL answer chain, chat API, semantic support guards, bounded calls |
| 8 Student UI | Partial | Complete profile fields, relevant follow-ups, cited chat, full junior/senior journeys |
| 9 Scenarios/print | Partial | Source-change messaging and broader print/reset/selection coverage |
| 10 Evals/admin | Partial | Checked cases, scoring/judge, explicit retry/resume, admin API/UI and LangSmith |
| 11 Real comparison | Not started | Broad ingestion, checked suite, controlled update and genuine measured comparison |
| 12 Release | Partial documentation only | Full integration checks, release packet, deployment approval and submission evidence |

**Independent coding remains; credentials are not the only remaining work.** Do not mark partial tasks complete based on fixture tests. The current application intentionally reports an unavailable catalog. Repository wiring and a real published corpus are not yet configured; browser tests use explicitly synthetic responses where needed.

## Exact live setup gates

Enter secrets directly in ignored `.env` or Replit Secrets, never chat or Git:

- `DATABASE_URL`: explicitly identified development PostgreSQL database.
- Replit-supported identity configuration: verified issuer, audience and immutable owner subject; production admin remains disabled.
- App Storage bucket ID and supported runtime authentication.
- `OPENAI_API_KEY`, funded project and explicit numerical per-run/total spending approval.
- `PINECONE_API_KEY`, index name/region and included allowance or approved cost.
- `LANGSMITH_API_KEY`, workspace/project for fictional evaluations only.

`LIVE_CALLS_ENABLED=false`, `OPENAI_RUN_BUDGET_USD=0`, `OPENAI_TOTAL_BUDGET_USD=0` remain defaults. Provider prices and service identities are not confirmed. Credentials alone do not authorize paid deployment.

## Resume and runtime

Progress ledger: `.superpowers/sdd/2026-10-14-nextstep-scholarships/progress.md` (ignored, intentionally retained because plan is unfinished). Read it and Git history before resuming. First close the independent gaps in Tasks 2, 4 and 5; do not redo completed scaffolding.

Runtime is installed in `/tmp/nextstep-python`; `.venv` references it. Use `UV_CACHE_DIR=/tmp/nextstep-uv-cache`. Reinstall Python 3.12 if temporary storage is cleared. Browser cache: `PLAYWRIGHT_BROWSERS_PATH=/tmp/nextstep-browsers`.

Verification commands: `uv run pytest -q`; `npm --prefix frontend test -- --run`; `npm --prefix frontend run build`; `npm --prefix frontend run test:e2e`; `uv run ruff check backend tests migrations scripts`; `git diff --check`.
