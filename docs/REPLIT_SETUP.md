# Replit development setup — October 14, 2026

Setup chat owns environment/transfer checks; build chat owns application source/tests/corpus. Direct coordination is authorized by the owner.

- Project: https://replit.com/@DeepalDSilva/nextstep-scholarships (private; owner signed in)
- Bootstrap snapshot transferred from feature-branch commit `1ef3148d9c905c383a4b86c00788d7b6173f7180`; `SOURCE_COMMIT.txt` records it. This is not the final live-tested handoff.
- 108 tracked source/document files plus source marker transferred; no local `.env`, instructor handouts, corpus artifacts, Git credentials or local runtime database.
- Replit Development Database exists; initial UI confirmed zero tables, runtime exposes DATABASE_URL. Migration to Alembic head and real database connection verified; 11 tables: alembic_version, active_corpus, chunk_manifest, corpus_versions, embedding_cache, eval_results, eval_runs, rate_counters, scholarships.
- App Storage bucket created and visibly verified: `nextstep-artifacts`, ID `replit-objstore-ec87b5ec-c288-4bf5-b7d6-351f0ac02fa7`. SDK upload/download verified with non-sensitive setup/connection-check.txt; contents matched exactly.
- Remote-only .replit runtime modules added: python-3.12 and nodejs-22. System python3 remains 3.14.6; project uv selects its required Python 3.12. Node 22.22.0 is available; frontend dependency installation, TypeScript check and Vite production build passed.
- uv installed through Python package registry. Replit preconfigured UV_PROJECT_ENVIRONMENT=.pythonlibs pointed to an invalid virtual environment; explicit `.venv` override completed locked backend dependency installation.
- Remote-only [env] config sets UV_PROJECT_ENVIRONMENT=.venv, bucket ID, development mode and LIVE_CALLS_ENABLED=false. No provider secrets copied or paid hosted calls enabled.

## Coordination boundaries

Build chat reports a provisional corpus `live-2026-10-14-reviewed-v6` with 10 programs/131 chunks/9 sources. Source audit and live evaluation fixes are ongoing; do not treat those records as release-ready eligibility guidance. Wait for its tested source commit and sanitized corpus export/import instructions.

  No Docker. No production publishing/merge approval inferred from setup.

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

The embedded Preview initially reported "Your app is not running" because startup was Shell-managed. Created and saved a sequential **NextStep development** workflow containing one Execute Shell Command task: `UV_PROJECT_ENVIRONMENT=.venv LIVE_CALLS_ENABLED=false sh scripts/start.sh`. Stopped only the setup-owned Shell server after checking its PID command matches `uvicorn nextstep.app:app`, then started the saved workflow. UI now shows **Stop workflow**, and the embedded Preview visibly renders the student form. Workflow start is verified; assigning it as the default top-level Run action is not yet verified. No corpus imported, no model/provider secrets transferred, no production publication.

Identity presence-only checks: REPL_ID, REPLIT_DOMAINS and SESSION_SECRET exist; OIDC_CLIENT_ID and ADMIN_SUBJECTS do not. No secret values read/displayed. Users & Auth explicitly reports Replit Auth is not configured. Configure panel shows default providers and an existing session secret; no rotation/provider/access changes made.

Current [official Replit Auth documentation](https://docs.replit.com/features/auth-and-identity/authentication) states that implementation through Replit Agent is the only supported method and manual implementation is unsupported. Existing custom Authlib/OIDC code therefore remains an unverified integration, not evidence that configuring environment variables alone will work. Setup notified Native. Invoking Replit Agent may consume separate Replit credits; do not initiate it or change security-sensitive access without the appropriate owner authorization. Owner sign-in, validated subject allowlisting, callback and denied non-owner flow remain release gates. Preserve fail-closed admin behavior in the meantime.

Owner asked to perform the auth setup themselves and requested steps. Provided a scoped Replit Agent prompt to preserve FastAPI/React, public student access, owner-only server-side allowlisting, existing schema/data/workflow; request a proposal first and prohibit publication/model calls/backend replacement. Recommended waiting for the coordinated latest-source transfer before invoking Agent. Setup has not invoked Agent. A genuine owner sign-in and negative authorization checks remain pending.

Subsequent owner decision: **keep admin evaluations local for now**. Hosted admin stays disabled/fail-closed; do not invoke Replit Agent for authentication. Auth integration is deferred for this demo, rather than a blocker to student-hosting work. Revisit only with owner authorization.

## Reviewed handoff installed in development

Received `/tmp/nextstep-verified-handoff/` from ingestion and uploaded its sanitized source archive, corpus JSON and receipt. Remote SHA256 checks matched source `22bf92db31946114be1b18b481edf0b8bd0a137f287fb44fec6b780c30b5cbff` and corpus `7b607ce3ad8e14ef6b3c9ebd292391d88199b317c59188af4f039c6c7a78532a`. Validated all 149 archive entries were regular, relative source files excluding secrets/runtime directories and `.replit`. Backed up overwritten source files to remote `/tmp/nextstep-before-reviewed.tar.gz` before extraction. Remote `SOURCE_HANDOFF.txt` identifies this exact package; the old `SOURCE_COMMIT.txt` identifies only the bootstrap and must not be mistaken for the current complete source identity. The package includes reviewed corpus/coverage guards and SVG UI polish; it is not solely a clean Git commit export.

Locked uv install, npm ci and frontend TypeScript/Vite build passed on Replit. npm reported zero vulnerabilities, but emitted engine-version warnings for some development dependencies against Node 22.22.0 (they request 22.22.2+ or supported newer versions). No hosted frontend unit/browser-suite claim is made from this build. Keep the Node warning visible for future runtime alignment.

Ran Alembic upgrade to head with process-local psycopg URL normalization, validated the corpus checksum and exact source provenance using `load_bundle`, and staged/froze/activated the PostgreSQL manifest using the trusted ingestion readiness receipt for the same `nextstep-scholarships` index and `verified-2026-10-14-v2` namespace. Confirmed **18 award records, 174 chunks**. No Pinecone write, embedding or extraction calls were needed. This imported manifest uses locally verified vector readiness; it is not an independent hosted Pinecone query check.

Stored and read back byte-identical `corpora/verified-2026-10-14-v2/corpus.json` (1,141,272 bytes) and `receipt.json` (989 bytes) through the existing App Storage bucket. Restarted the NextStep development workflow. Fresh remote health returned 200, admin runs returned 401, and the actual development browser rendered the new SVG brand/hero and returned scholarship cards for the **fictional senior** starter. Expanded Georgia Southern checklist showed source links, exact quotations, Fall 2027 cycle, admissions-GPA caveat and application instructions. UI labels the 18 records as programs; actual breadth is **10 award families**, not 18 distinct sponsor programs.

Hosted calls remained disabled at this checkpoint and no provider keys were transferred. Admin evals stay local. No deployment, merge, push, Replit Agent usage or course submission was performed.

## Shorter intake update — October 15, 2026

Installed the Native build chat's 131-file source package from `/tmp/nextstep-short-intake-handoff`, SHA256 `11570d3fc020cf7f760386c41ff7f799fe3dfa2bd5c78751a1025ebe796cd9fe` (manifest source commit `728228d9872d19c020eb4b08121e2fd7175fd988`). Verified remote checksum, regular relative archive paths and exclusion of secrets/runtime directories; backed up overwritten files to remote `/tmp/nextstep-before-short-intake.tar.gz`. Frontend TypeScript/Vite production build passed, 27 modules. Started NextStep development workflow.

Verified actual Replit development preview displays School year, Georgia resident, optional GPA, plans text and collapsed Add more details. Typing engineering/Georgia Tech/Auburn displays detected mentions with an initially unchecked confirmation; fictional senior returns 18 award records. Setup independently reran six intake unit tests successfully. No hosted model calls, secrets transfer, database migration, production publication or Replit Agent usage. Free-text recognition is a limited local hint mechanism, not general model extraction; follow-up model chat remains gated by hosted paid-call configuration.

Final follow-up package supersedes the first intake package: commit `a415649e4b3c2f23aeb4d6aa38dd32d741b75cba`, SHA256 `f113e284cc118ce95231be3ee0bd81077da7ae81154e27e8b27b445225c81257`, same 131 files. Remote checksum/path validation and frontend build passed. A fresh browser confirmed Fictional senior populates Senior / Georgia resident / Estimated GPA 3.5 consistently in form and summary and returns 18 records. Replit development workflow restarted after inactivity during upload. Screenshot: `/tmp/nextstep-short-intake-replit.jpg`.

## Instructor publication preparation — October 17, 2026

Owner authorized preparing publication. No publication performed.

Installed sanitized working-tree archive SHA256 `f6505e361bd6e1854c27a3c18d3dde8b893d01714cb96701b2479fc71ec9571d`, plus hosted-start delta `0e0c51b5b3dfd5fd6cb91c2314234ab591eaaaed71e3ffdd2767fc1c25a343e8`; local `.env`, credentials, and the full local SQLite database excluded. Prior overwritten remote source backed up under `/tmp/nextstep-before-release.tar.gz`. No clean-commit identity is claimed for this package.

Replit dependency installation and frontend build passed. Node 22.22.0 still emits development-dependency engine warnings; build succeeds. Read-only Pinecone fetch verified all 201 expected chunk IDs and required metadata in `candidate-2026-10-16-v4`. Imported/activated 39 award records and 201 chunks in development PostgreSQL, preserving previous namespaces.

Stopped the local paid-demo server (port 8014) before handoff. No new OpenAI calls during setup.

Production startup uses `scripts/start_hosted.sh` / `start_hosted.py`, validates the active corpus, normalizes the PostgreSQL driver, derives a stable rate-limit secret from the existing platform session secret, and explicitly disables hosted admin. Deployment-only startup enables paid calls after those gates; the development workflow remains `LIVE_CALLS_ENABLED=false`.

Replit preflight constructed the app with production settings against the prepared development database: health 200; homepage 200; admin runs 401; auth configured/authenticated false. This is **not** verification of a published production database or live hosted answer. Publishing UI has initial production database copy enabled. After first publication, verify the copied corpus and run a bounded real hosted journey.

Publication remains **Unpublished**. Existing settings: Autoscale, 2 vCPU/4 GiB, maximum 3 machines; no setting change claimed for machine sizing. Consider maximum 1 for instructor traffic. Domain shown available: nextstep-scholarships.replit.app. Provider keys are present and masked in deployment secrets. No Replit Agent invoked, no merge/push, no Google Doc edits.

Latest local backend verification: 141 passed, 2 skipped. See recording script (historical document removed) for the timed two-scenario walkthrough.

### Pre-publication cleanup

Rate limiting, corpus readiness, context bounds and hosted admin denial remain. Installed cleanup archive `cca58a6a42c4e0a350f1cfac36b1743a803e42708ddbf7d31e7306bb7291a048` on Replit.

## Published release verified — October 17, 2026

Owner approved hosting, publication and merging. PR #1 merged into main at `1d404568d37513ea2279669993a103116cb4025d`. Replit successfully published https://nextstep-scholarships.replit.app/ and both exact demo journeys ran against it with real chat and inspected citations. See published verification (historical document removed). The earlier publication-pending entries are historical. Repository remains private.
