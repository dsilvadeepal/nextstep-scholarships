from contextlib import contextmanager

from sqlalchemy import JSON, Column, Integer, MetaData, Numeric, String, Table
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()
json_type = JSON().with_variant(JSONB(), "postgresql")
corpus_versions = Table(
    "corpus_versions",
    metadata,
    Column("version", String, primary_key=True),
    Column("status", String, nullable=False),
)
active_corpus = Table(
    "active_corpus",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("version", String),
)
scholarships = Table(
    "scholarships",
    metadata,
    Column("version", String, primary_key=True),
    Column("id", String, primary_key=True),
    Column("data", json_type, nullable=False),
)
chunk_manifest = Table(
    "chunk_manifest",
    metadata,
    Column("version", String, primary_key=True),
    Column("id", String, primary_key=True),
    Column("data", json_type, nullable=False),
)
usage_ledger = Table(
    "usage_ledger",
    metadata,
    Column("id", String, primary_key=True),
    Column("run_id", String, nullable=False),
    Column("amount", Numeric(16, 8), nullable=False),
    Column("status", String, nullable=False),
)
# A singleton serializes reservations across processes, not just threads.
budget_guard = Table("budget_guard", metadata, Column("id", Integer, primary_key=True))


@contextmanager
def serialized(engine):
    with engine.connect() as conn:
        if engine.dialect.name == "sqlite":
            conn.exec_driver_sql("BEGIN IMMEDIATE")
        else:
            conn.begin()
            conn.exec_driver_sql("SELECT pg_advisory_xact_lock(702614)")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


embedding_cache = Table(
    "embedding_cache",
    metadata,
    Column("key", String, primary_key=True),
    Column("vector", json_type, nullable=False),
)
eval_runs = Table(
    "eval_runs",
    metadata,
    Column("id", String, primary_key=True),
    Column("status", String, nullable=False),
    Column("config", json_type, nullable=False),
)
eval_results = Table(
    "eval_results",
    metadata,
    Column("run_id", String, primary_key=True),
    Column("case_id", String, primary_key=True),
    Column("method", String, primary_key=True),
    Column("status", String, nullable=False),
    Column("lease_until", Numeric(20, 4)),
    Column("lease_token", String),
    Column("attempts", json_type),
    Column("result", json_type),
)
rate_counters = Table(
    "rate_counters",
    metadata,
    Column("key", String, primary_key=True),
    Column("count", Integer, nullable=False),
    Column("expires", Integer, nullable=False),
)
