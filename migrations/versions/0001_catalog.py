"""Initial schema, frozen before first release; never import mutable application metadata."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "active_corpus",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("version", sa.String(), primary_key=False, nullable=True),
    )
    op.create_table(
        "budget_guard",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
    )
    op.create_table(
        "chunk_manifest",
        sa.Column("version", sa.String(), primary_key=True, nullable=False),
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column(
            "data",
            sa.JSON().with_variant(JSONB(), "postgresql"),
            primary_key=False,
            nullable=False,
        ),
    )
    op.create_table(
        "corpus_versions",
        sa.Column("version", sa.String(), primary_key=True, nullable=False),
        sa.Column("status", sa.String(), primary_key=False, nullable=False),
    )
    op.create_table(
        "embedding_cache",
        sa.Column("key", sa.String(), primary_key=True, nullable=False),
        sa.Column(
            "vector",
            sa.JSON().with_variant(JSONB(), "postgresql"),
            primary_key=False,
            nullable=False,
        ),
    )
    op.create_table(
        "eval_results",
        sa.Column("run_id", sa.String(), primary_key=True, nullable=False),
        sa.Column("case_id", sa.String(), primary_key=True, nullable=False),
        sa.Column("method", sa.String(), primary_key=True, nullable=False),
        sa.Column("status", sa.String(), primary_key=False, nullable=False),
        sa.Column("lease_until", sa.Numeric(20, 4), primary_key=False, nullable=True),
        sa.Column("lease_token", sa.String(), primary_key=False, nullable=True),
        sa.Column(
            "attempts",
            sa.JSON().with_variant(JSONB(), "postgresql"),
            primary_key=False,
            nullable=True,
        ),
        sa.Column(
            "result",
            sa.JSON().with_variant(JSONB(), "postgresql"),
            primary_key=False,
            nullable=True,
        ),
    )
    op.create_table(
        "eval_runs",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("status", sa.String(), primary_key=False, nullable=False),
        sa.Column(
            "config",
            sa.JSON().with_variant(JSONB(), "postgresql"),
            primary_key=False,
            nullable=False,
        ),
    )
    op.create_table(
        "rate_counters",
        sa.Column("key", sa.String(), primary_key=True, nullable=False),
        sa.Column("count", sa.Integer(), primary_key=False, nullable=False),
        sa.Column("expires", sa.Integer(), primary_key=False, nullable=False),
    )
    op.create_table(
        "scholarships",
        sa.Column("version", sa.String(), primary_key=True, nullable=False),
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column(
            "data",
            sa.JSON().with_variant(JSONB(), "postgresql"),
            primary_key=False,
            nullable=False,
        ),
    )
    op.create_table(
        "usage_ledger",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("run_id", sa.String(), primary_key=False, nullable=False),
        sa.Column("amount", sa.Numeric(16, 8), primary_key=False, nullable=False),
        sa.Column("status", sa.String(), primary_key=False, nullable=False),
    )


def downgrade():
    op.drop_table("usage_ledger")
    op.drop_table("scholarships")
    op.drop_table("rate_counters")
    op.drop_table("eval_runs")
    op.drop_table("eval_results")
    op.drop_table("embedding_cache")
    op.drop_table("corpus_versions")
    op.drop_table("chunk_manifest")
    op.drop_table("budget_guard")
    op.drop_table("active_corpus")
