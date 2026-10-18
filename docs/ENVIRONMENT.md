# Environment and setup

The student demo is already published. These instructions explain local development and the current deployment configuration; they are not a request to recreate the production database.

## Run locally

Use Python 3.12, Node.js 24, `uv`, and npm. Docker is not required.

```bash
uv sync --locked
npm --prefix frontend ci
npm --prefix frontend run build
sh scripts/start.sh
```

Open `http://localhost:8000`, or set `PORT` before starting. The UI and API share one server. The Vite development server is optional.

A fresh checkout starts without a populated catalog. Connect `DATABASE_URL` to a prepared development database to browse real records. Migrations alone create tables, not scholarship records. Do not point local migration, ingestion, or test commands at the published app's database.

## Configuration

Use `.env.example` as the variable-name reference. Save values only in an ignored `.env` or Replit Secrets; never commit keys.

- **Database:** `DATABASE_URL`, preferably `postgresql+psycopg://...`. On a new, explicitly selected development database, `uv run alembic upgrade head` creates the schema.
- **Chat and embeddings:** server-side `OPENAI_API_KEY`, `PINECONE_API_KEY`, and `PINECONE_INDEX=nextstep-scholarships`. Local calls default to disabled; enabling `LIVE_CALLS_ENABLED=true` also requires a ready catalog and matching Pinecone namespace.
- **Models:** defaults are `gpt-4.1-mini` and `text-embedding-3-small` with 1,536 dimensions.
- **Storage:** `APP_STORAGE_BUCKET_ID` identifies the Replit App Storage bucket; the SDK uses Replit runtime identity. Local tests use a local artifact adapter.
- **Admin:** hosted admin is disabled. The student app needs no account. Local evaluation tooling retains authentication boundaries; do not enable hosted admin just to run the public demo.
- **Tracing:** LangSmith is optional for fictional evaluation traces. Real student conversations must not be globally traced.

The frozen release catalog is `data/corpus-candidate-2026-10-16-v4.json`. The live index namespace is `candidate-2026-10-16-v4`. The existing hosted database was prepared separately; legacy one-time setup scripts are not a generic fresh-clone installer. Do not rerun them against production.

## Tests

```bash
uv run pytest -q
npm --prefix frontend test -- --run
npm --prefix frontend run build
uv run ruff check backend tests migrations scripts
git diff --check
```

For browser checks, install Playwright Chromium and use `npm --prefix frontend run test:e2e`. See the Playwright configuration for server setup. Live browser tests are separate and require a configured running app.

PostgreSQL tests require `TEST_POSTGRES_URL` pointing to an explicitly selected test database. Run `uv run pytest -m postgres -q`; tests use isolated schemas. Historical `/tmp/nextstep-*` runtimes and screenshots are local artifacts, not prerequisites provided by this repository.

## Ingestion and updates

The CLI supports `collect`, `run`, `publish`, and `rollback`. Collection preserves source provenance; extraction stages structured records and chunks; publication verifies the namespace before switching the active corpus. Run `uv run python -m nextstep.ingest.cli --help` for arguments. The initial `data/sources.yaml` register is historical; the expanded release also uses reviewed sections and exclusion records. Do not assume collecting the initial register reproduces the final corpus.

Preserve previous query-ready versions for rollback. Avoid automatically replaying provider requests with an uncertain completion status. See [content policy](OPERATIONAL_CONTENT_POLICY.md) and [data contracts](DATA_DICTIONARY.md).

## Published startup

`.replit` builds with `scripts/build.sh` and deploys with `scripts/start_hosted.sh`. The hosted wrapper requires PostgreSQL, the expected active corpus, provider keys, and a stable `SESSION_SECRET` of at least 32 characters. It derives the rate-limit secret, uses the published HTTPS origin, enables student chat, and keeps hosted admin disabled. It does not ingest sources on startup.

The development Run command uses `scripts/start.sh`; its configuration comes from the local environment. Documentation-only changes do not require republishing. See [Replit release history](REPLIT_SETUP.md) for recorded setup and publication checks.
