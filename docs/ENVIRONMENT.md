# Environment and service gates

Use Python 3.12 and `uv sync --locked`. In the current sandbox run with `UV_CACHE_DIR=/tmp/nextstep-uv-cache`. Frontend: `npm --prefix frontend ci`, `npm --prefix frontend run build`. Run one service with `uv run uvicorn nextstep.app:app --host 0.0.0.0 --port "${PORT:-8000}"` from the repository root. Generate contracts with `uv run python scripts/export_openapi.py` then `npm --prefix frontend run types`.

Local tests use isolated SQLite databases. PostgreSQL uses SQLAlchemy JSONB and transaction advisory locks. PostgreSQL integration is not yet executed and SQLite tests are not evidence of hosted compatibility. Migrate an explicitly configured development database with `DATABASE_URL=... uv run alembic upgrade head`; never paste the URL into chat or shell history. Set it through ignored `.env`/environment first.

Admin endpoints fail closed. A supported Replit issuer/audience/expiry verifier and immutable owner allowlist remain required before enabling production admin. Browser identity headers are never accepted. No production fake identity exists.

No service credentials, provider prices or paid budgets have been configured or tested. App Storage bucket, Pinecone index, PostgreSQL database and Replit deployment identities remain unconfirmed. No claims of connected services or release readiness.
