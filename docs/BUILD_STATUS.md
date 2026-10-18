# Build status — October 16, 2026

## Local activation — October 16, 2026, 9:03 p.m. ET

Following explicit user approval, `candidate-2026-10-16-v4` is now the active local
catalog: **39 records / 31 families / 201 chunks / 63 official documents**.
The version name retains its immutable staging identifier. The previous
`verified-2026-10-14-v2` catalog (18 records / 174 chunks) and Pinecone namespace
remain intact and ready for rollback. Both namespaces passed fresh ID/count/query
readiness checks before the transactional active-pointer switch.

Post-activation checks against the actual app on port 8014 passed: 39-record
matching; cited UAB no-superscore answer; Cooke transcript/income source distinctions
with explicit sponsor-confirmation caveats; HOPE 2027–28 coverage gap without paid
calls; invalid-program rejection; and server-side version pinning despite a stale
client version. Phone and desktop rendered 39 awards without page errors or
horizontal overflow. These are smoke checks, not a new 47-case evaluation run.

Activation cost $0. Testing added **$0.00807484**; cumulative ledger total is
**$2.08153838 / $5**, including four previously recorded ambiguous-call liabilities.
There are zero outstanding reservations. The original live ledger remains authoritative.
No Docker, hosted deployment, namespace deletion, or `.env` edits occurred.

Receipts: `artifacts/reports/local-activation-2026-10-16.json` and
`artifacts/reports/local-activation-smoke-2026-10-16.json`.
The frozen bundle and vector metadata preserve their staging-time
`inactive_candidate` label; runtime activation is determined solely by the SQL
active-corpus pointer and namespace, not that historical metadata field. Evidence,
source hashes, cycle metadata, and all source references were preserved unchanged.

Rollback from the repository root (does not reset or restore the spend ledger):

```sh
PYTHONPATH=backend:scripts .venv/bin/python - <<'PYROLLBACK'
from sqlalchemy import create_engine
from reviewed_runtime import live_settings
from nextstep.repository import Repository
repo = Repository(create_engine(live_settings().database_url))
repo.activate_version('candidate-2026-10-16-v4', 'verified-2026-10-14-v2')
print(repo.active_version())
PYROLLBACK
```

The checkpoints below describe pre-activation work and remain historical evidence.

The expanded candidate has completed local testing: **39 records / 31 families /
201 chunks / 63 official documents**. Its 21 source cases passed, as did the 26
known regressions on the candidate. The final implementation suite passed 131
backend tests, with both native PostgreSQL checks passing separately; 12 frontend
tests, 20 mocked browser checks, TypeScript/build, and real candidate API/browser/
print checks also passed. Cumulative OpenAI spend is **$2.07346354 of $5**.

The active catalog remains `verified-2026-10-14-v2` (18 records / 174 chunks);
`candidate-2026-10-16-v4` is staged and inactive. Activation was excluded from the
ingestion scope. No Docker or secret-file edits occurred. See the
[complete current evidence and limitations](EXPANDED_BUILD_TEST_REPORT_2026-10-16.md).

The checkpoints below are historical; their counts and stop points are superseded
by this dated update.

## Historical October 14 checkpoint

## Current checkpoint: verified local corpus active

The second-pass research, local ingestion, metadata verification and local application tests are complete. Active corpus: **`verified-2026-10-14-v2`**, with **18 award records / 10 award families / 174 chunks / 19 contributing official documents**. Every Pinecone vector's metadata was fetched and compared exactly with its canonical manifest. Older namespaces are retained but no longer queried by the active local application. See second-pass review (historical document removed) for admitted/deferred sources and limitations.

- **84 backend tests passed**; the two PostgreSQL tests skipped in that default invocation **also passed separately** against the dedicated native Unix-socket PostgreSQL instance. No Docker.
- **7 frontend unit tests**, TypeScript and production build passed. **18 mocked browser regressions** passed. **6 real local browser/API checks** passed across phone and desktop, including two live cited answers, unknown requirements, removed-program rejection, server-side version pinning, coverage gaps and compact printing. Printed output was visually inspected after fixing repeated quotes and a blank first page.
- **26 source-grounded fictional regression cases passed for each retrieval method**, semantic and hybrid. Original held-out answers were **5/6 per method under the old automated rubric**: the correct Clemson evidence-gap response was penalized for not supplying unavailable rules. The rubric now explicitly supports predeclared evidence gaps; rescoring those saved outputs yields **6/6 per method**, without new provider calls. Original grades remain unchanged; this is **not a fresh held-out run**. Rubric-only edits cannot reset question exposure.
- Live tests caught and fixed a real error: absent HOPE rules could be substituted with Georgia Southern merit rules. A versioned coverage register and explicit program/cycle scope now prevent that substitution. Metadata distinguishes application cycle, college entry, award academic year and graduation year; unspecified fields remain null/omitted.
- Cumulative recorded OpenAI spend after tests: **$0.72160134 of $5**, with approximately **$4.28 remaining**. `artifacts/nextstep-live.db` remains authoritative and was not reset. The local app is running on port 8014 with process-scoped live settings via `scripts/start_reviewed_local.py`; `.env` was not rewritten. Subsequent live user questions accrue to the same ledger.

This verifies the **local pilot**, not hosted production readiness or comprehensive scholarship coverage. Hosted paid calls remain disabled; setup must preserve one cumulative budget ledger before enabling another instance. Hosted admin/evaluation authentication remains fail-closed and outside this checkpoint.

## Earlier checkpoints (historical)

**Credential-free implementation and local verification are complete; the live demo is not release-ready.** Native execution remains on `feat/nextstep-native`. Main stays at `679c49e`. No merge, push, deployment, recording or submission performed. Live OpenAI access was briefly verified; see the live checkpoint below for spending and the current credential blocker. **Do not use Docker.**

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
| RAG | Dense/BM25/RRF, LCEL prompt/structured-model pipeline, bounded prior-user context, exact quoted support, deterministic unknowns, pinned API, failure fallback | One/two-program live smoke checks, claim inspection, measured quality/latency |
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

## Live checkpoint — October 14, 2026

The owner supplied both keys and approved a $5 total ceiling. Presence was verified without printing secrets, and four OpenAI extraction calls completed. The dedicated local SQLite ledger at ignored `artifacts/nextstep-live.db` records **$0.00711080** across those calls, including failed validation. No corpus was activated and no live model quality score is claimed. This local database does not replace hosted PostgreSQL verification.

Live output exposed nullable-list/schema mistakes and unreliable citation metadata/offsets. The extraction prompt now distinguishes nullable scalars from empty collections and describes supported matching operators. Exact, unique quotes are anchored deterministically to their supplied source section; invented or ambiguous quotes still fail validation. A regression covers that boundary. The updated extraction has not yet produced a fully validated live record.

During this work the local `.env` changed again: both previously present API keys disappeared, as did the appended local database/pricing settings. No key values were displayed or copied into tracked files. The responsible editor/process has not been identified. Paid execution is stopped until the owner saves the keys durably. Preserve this ledger for all resumed work so the $5 total ceiling remains cumulative.

Pricing used: GPT-4.1 mini input $0.40/output $1.60 per million tokens, and text-embedding-3-small $0.02 per million, checked against https://developers.openai.com/api/docs/models/gpt-4.1-mini and https://developers.openai.com/api/docs/models/text-embedding-3-small on October 14, 2026. Live enablement was command-scoped; no hosted deployment occurred.


## October 15: grounded answers and targeted retrieval

The local default is now phase 1 + phase 2: cited explanations with a bounded support review, source-bound ACT comparisons, and targeted selection of existing passages after 50/50 hybrid search. The same five exposed demo cases were compared against phase 1 alone; the combined approach recovers the missing Auburn Heritage threshold. See [the complete comparison](RAG_COMPARISON_2026-10-15.md) for exact outputs, costs, source links, rollback checkpoints and wording limitations. These results supersede the earlier fragment-based demo outputs, but are not a held-out accuracy claim. Hosted transfer of this new revision remains separate.
