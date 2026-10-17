"""Production startup with private admin and verified corpus configuration."""

import hashlib
import hmac
import os

import uvicorn
from nextstep.app import create_app
from nextstep.config import Settings
from nextstep.repository import Repository
from sqlalchemy import create_engine


def verified_settings():
    url = os.environ["DATABASE_URL"].replace(
        "postgresql://", "postgresql+psycopg://", 1
    )
    engine = create_engine(url)
    if Repository(engine).active_version() != "candidate-2026-10-16-v4":
        raise ValueError("Production corpus is not the verified demo version")
    secret = os.environ["SESSION_SECRET"]
    if len(secret) < 32:
        raise ValueError("Stable platform secret is required")
    return Settings(
        _env_file=None,
        environment="production",
        hosted_admin_enabled=False,
        database_url=url,
        public_origin="https://nextstep-scholarships.replit.app",
        rate_secret=hmac.new(
            secret.encode(), b"nextstep-rate-limit-v1", hashlib.sha256
        ).hexdigest(),
        live_calls_enabled=True,
        pinecone_index="nextstep-scholarships",
    )


if __name__ == "__main__":
    uvicorn.run(
        create_app(verified_settings()),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        access_log=False,
    )
