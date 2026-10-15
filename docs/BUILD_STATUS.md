# Build status — October 14, 2026

**Credential-free implementation and local verification are complete; the live demo is not release-ready.** Native execution remains on `feat/nextstep-native`. Main stays at `679c49e`. No merge, push, deployment, recording or submission performed. No OpenAI calls or spending enabled. **Do not use Docker.**

## Verified evidence

- **71 backend tests passed**, with two PostgreSQL tests skipped only in the default unconfigured test invocation.
- **2 PostgreSQL integration tests passed separately** against our dedicated local PostgreSQL 17.7 Unix-socket instance: JSONB, concurrent budget reservations, concurrent run start and persistence/resume across runner instances. No Docker.
- **6 frontend unit tests passed**; TypeScript and Vite production build passed.
- **18 Playwright checks passed** across 390px phone and 1440px desktop: full synthetic student profile/results/chat/citation/print journey, service failures, scenario/reset/source-version races, anonymous admin boundary, saved-case inspection and refresh without replay.
- Phone/desktop chat and source PDF screenshots visually inspected. Synthetic full-journey print PDFs generated at `/tmp/nextstep-complete-plan-phone.pdf` and `/tmp/nextstep-complete-plan-desktop.pdf`; earlier print fixtures also retained. These are not live-model evidence.
- Ruff and Git whitespace checks passed. Initial frozen Alembic migration successfully applied to a fresh local SQLite database. PostgreSQL schema behavior verified separately; hosted migration still requires the selected development database.
- 16 public documents collected/parsed; originals retained under ignored `artifacts/`. 15 excerpts checked against original HTML/PDF to prepare **24 fictional eval cases: 18 tuning, 6 held out**. No model evaluation has consumed the heldout suite.
- Synthetic source update/failed-publication/rollback test passed. Invented rules live only in the separate fixture directory.

## Scope ledger

| Area | Locally implemented and verified | Access-dependent work |
|---|---|---|
| Contracts/matching | Generated types; optional profile/GPA semantics; deterministic tri-state rules; matching independent of retrieval | Inspect real extracted rules and condition coverage |
| Persistence/security | PostgreSQL-compatible schema/migration, session verification/owner allowlist, origin/body/rate/budget guards, production configuration validation | Genuine Replit OIDC login, hosted DB/storage access |
| Collection/extraction | Safe pinned-public-IP collector, source register, HTML/PDF provenance, field evidence validation, explicit hash-pinned program partitions, cross-page aliases/reconciliation/conflicts | Real structured extraction; inspect all flagged partitions/unknowns and refine bindings from actual output |
| Publication | Embedding cache, namespaces, immutable manifests, fetched-count/search-probe readiness, atomic activation/rollback, resumable CLI | Real embeddings/upsert/query-readiness and storage verification |
| RAG | Dense/BM25/RRF, fixed LCEL flow, bounded prior-user context, exact quoted support, deterministic unknowns, pinned API, failure fallback | One/two-program live smoke checks, claim inspection, measured quality/latency |
| Student experience | Complete skippable form, three fictional starters, result groups/details, shortlist, cited dialog, scenarios/reset/source-change notice, print | Review real junior/senior journeys against published corpus |
| Evals/admin | Checked reference files, protected API, sequential browser driver, durable leases/token CAS, explicit retries/cancel, immutable settings, inspector, aggregates/denominators, post-save fictional trace upload | Run actual tuning/heldout comparison; inspect failures; verify real LangSmith links |
| Release packet | One-port `.replit` and scripts, setup instructions, source/eval reports, demo/submission drafts | Owner access/spend configuration, hosted smoke checks, publication approval, video and submission |

## Independent review and fixes

The fresh whole-branch review found six important issues. Each was reproduced and fixed with local regression evidence:

1. Uncited exceptions: retain all sections for a single program, include nested condition evidence in ownership, and block ambiguous multi-program attribution. Reviewed partitions must cover the entire section and match the original hash; offsets remain exact.
2. Lease expiry: a completed result remains saveable when its original token is still current; explicit retry/cancel invalidates the token. Optional trace upload happens after durable persistence.
3. Configuration drift: execution rejects changed model, embedding dimensions/index, prompt/chunk/retrieval version, prices or budget caps.
4. Answer-key leakage: reference sources are used only after retrieval for assertions; explicit case input selects programs, empty by default.
5. Follow-ups: bounded prior user turns inform retrieval; unsupported assistant claims do not become retrieval context.
6. Cross-page rules: stable program bindings and conservative reconciliation retain source evidence and flag incompatible conditions/dates.

The separate Pinecone setup chat reported an SDK constructor incompatibility. It was reproduced and fixed: timeout and zero retries are configured on `Pinecone`, not `Index`. The setup chat verified an empty ready `nextstep-scholarships` index; this build verified key/index presence without displaying secrets. Real application search is still unexecuted.

## Actual stop point

The next meaningful step is **the first live source-to-answer slice**. It needs:

- Funded OpenAI server key, approved numerical run/total budgets, and verified price inputs/date.
- Replit development PostgreSQL and App Storage configuration for hosted persistence.
- Replit owner identity/client/callback configuration and one genuine owner sign-in.
- LangSmith key/project if live traces are required (local eval persistence does not depend on it).

Pinecone setup is already supplied; do not ask for its key again. `LIVE_CALLS_ENABLED=false`, caps remain zero, and no OpenAI key/price configuration is present. Credentials alone do not authorize publication or paid deployment.

Collection and preprocessing have already happened without credentials. The remaining corpus-quality decisions must be based on actual extracted output and measured model behavior; fixture tests cannot substitute for them. See `ENVIRONMENT.md` for exact setup order and commands, `RELEASE_CHECKLIST.md` for approval gates, and `SOURCE_INSPECTION.md` for known coverage limitations.

The execution ledger is retained because live Tasks 11–12 and integration acceptance remain unfinished. Main/worktree are retained; no automatic merge/push/cleanup. Native implementation remains the owner-selected approach. No measured evidence establishes a parallel-execution time saving.
