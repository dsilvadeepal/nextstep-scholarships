# Environment and setup handoff

## Reproduce locally — no Docker

Python 3.12 and Node 24 are the verified runtimes. Run `uv sync --locked`, `npm --prefix frontend ci`, and `npm --prefix frontend run build`. Start from the repository root with `sh scripts/start.sh`; this serves the production React build and API on `${PORT:-8000}`. For the existing preview, set `PORT=8014`. The Vite dev server is optional and not used in published runtime.

Current sandbox Python lives in `/tmp/nextstep-python`; use `UV_CACHE_DIR=/tmp/nextstep-uv-cache`. Reinstall Python if temporary files are cleared. Playwright browsers are under `/tmp/nextstep-browsers`. No Docker dependency, container command or work-Docker access is required.

Tests: `uv run pytest -q`; `npm --prefix frontend test -- --run`; `npm --prefix frontend run build`; `PLAYWRIGHT_BROWSERS_PATH=/tmp/nextstep-browsers npm --prefix frontend run test:e2e`; `uv run ruff check backend tests migrations scripts`; `git diff --check`.

PostgreSQL integration ran against a separate PostgreSQL 17.7 executable built under `/tmp/nextstep-postgres`, using a private Unix socket `/tmp/nextstep-pgsocket`, port 55434, no TCP listener, UTF8 database `nextstep_test`. Tests create and remove random schemas. Set `TEST_POSTGRES_URL` only to an explicitly authorized development database; run `uv run pytest -m postgres -q`. This verifies actual PostgreSQL JSONB, concurrent budget/run transactions and resume persistence; it does not verify Replit connectivity.

## What the owner needs to configure next

1. **Replit project:** import this private repository/branch after deciding how to transfer local changes. Confirm Python 3.12, Node and uv are available. Keep development and production databases separate. No publish action is authorized by adding keys.
2. **Development PostgreSQL:** provide `DATABASE_URL` in Replit Secrets (SQLAlchemy `postgresql+psycopg://...`). Run `uv run alembic upgrade head` only against that explicitly selected development database. The initial migration is frozen before first release. No prior production database exists in this build; do not apply it blindly to an unrelated schema.
3. **App Storage:** enable a project bucket and set `APP_STORAGE_BUCKET_ID`. The SDK uses Replit runtime identity; no browser/cloud credentials are copied into the app.
4. **Admin identity:** enable Replit Auth, confirm client ID and permitted callback `${PUBLIC_ORIGIN}/api/auth/callback`, sign in and obtain the immutable subject for `ADMIN_SUBJECTS` (JSON array). Set a 32+ character random `SESSION_SECRET`, separate stable `RATE_SECRET`, and HTTPS `PUBLIC_ORIGIN`. Signed sessions are verified server-side; client identity headers are not accepted. Hosted OIDC compatibility remains an integration check.
5. **OpenAI:** set a funded server `OPENAI_API_KEY`. Approve exact per-run and total USD caps and verified model prices/date. Set `INPUT_USD_PER_MILLION`, `OUTPUT_USD_PER_MILLION`, `EMBEDDING_USD_PER_MILLION`, and `PRICING_EFFECTIVE_DATE`. Defaults keep `LIVE_CALLS_ENABLED=false` and both caps at zero. A ChatGPT subscription is not API funding.
6. **Pinecone:** the separate owner-authorized setup created `nextstep-scholarships` (1536 dimensions, cosine, AWS us-east-1). Key and index name are now present in ignored `.env`. Its setup note reports readiness and zero vectors. The application constructor incompatibility found there is fixed: timeout/retry policy belongs on `Pinecone`, not `Index`. No real application embeddings/search have been executed here.
7. **LangSmith:** optional for local result persistence; configure server key/project for fictional evaluation traces when ready. Global tracing stays disabled for real student conversations. Trace-upload failure cannot discard a saved result.

Do not paste secrets into chat. `.env.example` lists variable names; put actual values only in ignored `.env` or Replit Secrets. Account allowances and current pricing must be confirmed before enabling paid calls. Production startup rejects SQLite, missing stable secrets, missing owner identity configuration and non-HTTPS origin.

## Collection, preprocessing, extraction and publication

Collection/preprocessing already ran locally: 16 originals and normalized documents are saved in ignored `artifacts/`. This stage needs no model credentials. `uv run python -m nextstep.ingest.cli collect --sources data/sources.yaml` refreshes that inventory; add `--app-storage` inside the configured Replit runtime.

After OpenAI access/budget approval, `... cli run --sources data/sources.yaml --version VERSION` collects, caches validated extraction, binds program IDs, preserves conflicts and stages catalog/chunks. Multi-award ambiguity fails visibly. Review the saved failure and add hash-pinned section partitions/aliases to the register; reruns reuse extracted output and embedding cache. Never automatically retry an ambiguous failed paid operation.

`... cli publish --version VERSION` freezes the manifest, embeds, upserts, verifies fetched IDs/counts and searchable probes, then atomically activates it. `... cli rollback --version PREVIOUS_READY_VERSION` changes only the retained ready active pointer and needs no OpenAI calls or paid-call enablement.

## Publish preparation only

`.replit` contains one-port build/run commands and `deploymentTarget="cloudrun"`. `scripts/build.sh` installs locked dependencies and builds React; `scripts/start.sh` starts one FastAPI service without access logs. Migrations and ingestion are explicit manual actions, not startup side effects. Use Replit Autoscale only after owner approval and account-specific allowance review. Cold/warm live checks, verified admin login, artifact persistence, budget accounting and a real saved comparison are still release gates.

Configuration reference checked October 14: [Replit application configuration](https://docs.replit.com/features/project-setup/configuration), [Replit Auth](https://docs.replit.com/features/auth-and-identity/authentication). These document the platform; they do not prove this project's hosted configuration.
