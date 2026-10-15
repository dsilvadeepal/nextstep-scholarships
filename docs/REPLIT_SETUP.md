# Replit development setup — October 14, 2026

Setup chat owns environment/transfer checks; build chat owns application source/tests/corpus. Direct coordination is authorized by the owner.

- Project: https://replit.com/@DeepalDSilva/nextstep-scholarships (private; owner signed in)
- Bootstrap snapshot transferred from feature-branch commit `1ef3148d9c905c383a4b86c00788d7b6173f7180`; `SOURCE_COMMIT.txt` records it. This is not the final live-tested handoff.
- 108 tracked source/document files plus source marker transferred; no local `.env`, instructor handouts, corpus artifacts, Git credentials or live spending database.
- Replit Development Database exists; initial UI confirmed zero tables, runtime exposes DATABASE_URL. Migration to Alembic head and real database connection verified; 11 tables: alembic_version, active_corpus, budget_guard, chunk_manifest, corpus_versions, embedding_cache, eval_results, eval_runs, rate_counters, scholarships, usage_ledger.
- App Storage bucket created and visibly verified: `nextstep-artifacts`, ID `replit-objstore-ec87b5ec-c288-4bf5-b7d6-351f0ac02fa7`. SDK upload/download verified with non-sensitive setup/connection-check.txt; contents matched exactly.
- Remote-only .replit runtime modules added: python-3.12 and nodejs-22. System python3 remains 3.14.6; project uv selects its required Python 3.12. Node 22.22.0 is available; frontend dependency installation, TypeScript check and Vite production build passed.
- uv installed through Python package registry. Replit preconfigured UV_PROJECT_ENVIRONMENT=.pythonlibs pointed to an invalid virtual environment; explicit `.venv` override completed locked backend dependency installation.
- Remote-only [env] config sets UV_PROJECT_ENVIRONMENT=.venv, bucket ID, development mode and LIVE_CALLS_ENABLED=false. No provider secrets copied or paid hosted calls enabled.

## Coordination boundaries

Build chat reports a provisional corpus `live-2026-10-14-reviewed-v6` with 10 programs/131 chunks/9 sources. Source audit and live evaluation fixes are ongoing; do not treat those records as release-ready eligibility guidance. Wait for its tested source commit and sanitized corpus export/import instructions.

Preserve the authoritative cumulative $5 ledger at local ignored `artifacts/nextstep-live.db`. Do not initialize a fresh hosted paid ledger or rerun paid extraction/embedding as part of setup. No Docker. No production publishing/merge approval inferred from setup.

Verification runtime: project Python 3.12.12 (terminal verification result). Database URL normalized to postgresql+psycopg only within the setup process; no password was displayed or written to tracked config. Build chat owns the permanent normalization fix.

## Earlier paused handoff checkpoint (superseded by resumption below)

Build chat reports the owner requested a build pause pending eligibility-source research. Setup stopped after the in-flight frontend build completed successfully. No Replit app server started, no provisional corpus imported, no provider keys copied and no hosted paid calls enabled. Wait for reviewed eligibility-source handoff and explicit resumption of dependent build work.

Verified setup commands: `UV_PROJECT_ENVIRONMENT=.venv python3 -m uv sync --locked --no-dev`; process-local psycopg URL normalization + `alembic upgrade head`; SDK upload/read of setup/connection-check.txt; `npm --prefix frontend ci`; `npm --prefix frontend run build`. Startup/health/auth and latest source handoff remain pending.

## Resumed development setup — October 14, 2026

Owner authorized continuing Replit setup while ingestion finishes, then approved free frontend polish. Native build owns the SVG logo/icons/illustrated hero/CSS and frontend tests; setup owns remote configuration and this record. Do not copy the actively changing working tree before a coordinated checkpoint.

Bootstrap source remains `1ef3148`. `create_app()` successfully imports with the development database configured and live calls disabled (14 routes). Started `UV_PROJECT_ENVIRONMENT=.venv sh scripts/start.sh` in a Replit Shell; Uvicorn reports application startup complete on port 8000. Verified with remote HTTP requests:

- `/api/health`: 200, `{"status":"ok"}`.
- `/`: 200; actual student form rendered in a separate browser tab at the development hostname below.
- `/api/auth/status`: configured false, authenticated false.
- `/api/admin/runs`: 401. An earlier probe at nonexistent `/api/evals/runs` returned 404 and is not authorization evidence.

Development URL: https://19762b75-40b3-412a-b575-64e4f42578fc-00-e2mtjrhqoluu.picard.replit.dev/

The embedded Preview initially reported "Your app is not running" because startup was Shell-managed. Created and saved a sequential **NextStep development** workflow containing one Execute Shell Command task: `UV_PROJECT_ENVIRONMENT=.venv LIVE_CALLS_ENABLED=false sh scripts/start.sh`. Stopped only the setup-owned Shell server after checking its PID command matches `uvicorn nextstep.app:app`, then started the saved workflow. UI now shows **Stop workflow**, and the embedded Preview visibly renders the student form. Workflow start is verified; assigning it as the default top-level Run action is not yet verified. No corpus imported, no model/provider secrets transferred, no hosted paid ledger enabled, no production publication.

Identity presence-only checks: REPL_ID, REPLIT_DOMAINS and SESSION_SECRET exist; OIDC_CLIENT_ID and ADMIN_SUBJECTS do not. No secret values read/displayed. Users & Auth explicitly reports Replit Auth is not configured. Configure panel shows default providers and an existing session secret; no rotation/provider/access changes made.

Current [official Replit Auth documentation](https://docs.replit.com/features/auth-and-identity/authentication) states that implementation through Replit Agent is the only supported method and manual implementation is unsupported. Existing custom Authlib/OIDC code therefore remains an unverified integration, not evidence that configuring environment variables alone will work. Setup notified Native. Invoking Replit Agent may consume separate Replit credits; do not initiate it or change security-sensitive access without the appropriate owner authorization. Owner sign-in, validated subject allowlisting, callback and denied non-owner flow remain release gates. Preserve fail-closed admin behavior in the meantime.

Owner asked to perform the auth setup themselves and requested steps. Provided a scoped Replit Agent prompt to preserve FastAPI/React, public student access, owner-only server-side allowlisting, existing schema/data/workflow and spending controls; request a proposal/cost first and prohibit publication/model calls/backend replacement. Recommended waiting for the coordinated latest-source transfer before invoking Agent. Setup has not invoked Agent or received authorization to spend Replit credits. A genuine owner sign-in and negative authorization checks remain pending.

Subsequent owner decision: **keep admin evaluations local for now**. Hosted admin stays disabled/fail-closed; do not invoke Replit Agent for authentication. Auth integration is deferred for this demo, rather than a blocker to student-hosting work. Revisit only with owner authorization. Current official AI billing documentation offers Free Mode within allowance and effort-based paid work, not a fixed authentication implementation quote; no verified dollar estimate for this integration is available.

## Reviewed handoff installed in development

Received `/tmp/nextstep-verified-handoff/` from ingestion and uploaded its sanitized source archive, corpus JSON and receipt. Remote SHA256 checks matched source `22bf92db31946114be1b18b481edf0b8bd0a137f287fb44fec6b780c30b5cbff` and corpus `7b607ce3ad8e14ef6b3c9ebd292391d88199b317c59188af4f039c6c7a78532a`. Validated all 149 archive entries were regular, relative source files excluding secrets/runtime directories and `.replit`. Backed up overwritten source files to remote `/tmp/nextstep-before-reviewed.tar.gz` before extraction. Remote `SOURCE_HANDOFF.txt` identifies this exact package; the old `SOURCE_COMMIT.txt` identifies only the bootstrap and must not be mistaken for the current complete source identity. The package includes reviewed corpus/coverage guards and SVG UI polish; it is not solely a clean Git commit export.

Locked uv install, npm ci and frontend TypeScript/Vite build passed on Replit. npm reported zero vulnerabilities, but emitted engine-version warnings for some development dependencies against Node 22.22.0 (they request 22.22.2+ or supported newer versions). No hosted frontend unit/browser-suite claim is made from this build. Keep the Node warning visible for future runtime alignment.

Ran Alembic upgrade to head with process-local psycopg URL normalization, validated the corpus checksum and exact source provenance using `load_bundle`, and staged/froze/activated the PostgreSQL manifest using the trusted ingestion readiness receipt for the same `nextstep-scholarships` index and `verified-2026-10-14-v2` namespace. Confirmed **18 award records, 174 chunks**. No Pinecone write, embedding or extraction calls were needed. This imported manifest uses locally verified vector readiness; it is not an independent hosted Pinecone query check.

Stored and read back byte-identical `corpora/verified-2026-10-14-v2/corpus.json` (1,141,272 bytes) and `receipt.json` (989 bytes) through the existing App Storage bucket. Restarted the NextStep development workflow. Fresh remote health returned 200, admin runs returned 401, and the actual development browser rendered the new SVG brand/hero and returned scholarship cards for the **fictional senior** starter. Expanded Georgia Southern checklist showed source links, exact quotations, Fall 2027 cycle, admissions-GPA caveat and application instructions. UI labels the 18 records as programs; actual breadth is **10 award families**, not 18 distinct sponsor programs.

Hosted paid calls remain disabled and no provider keys or local spending database were transferred. The ingestion receipt records $0.72160134 at its checkpoint but is informational, not an imported opening balance. Local demo remains available and can accrue later charges. There is currently no tested hosted ledger importer; future hosted chat requires quiescing local paid calls and an idempotent, reconciled transfer of liability (or one shared authoritative database), followed by explicit activation. Admin evals stay local. No deployment, merge, push, Replit Agent usage or course submission was performed.
