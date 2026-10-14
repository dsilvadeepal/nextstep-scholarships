"""Initial catalog and budget persistence."""
from alembic import op
from nextstep.db import metadata
revision = '0001'
down_revision = None

def upgrade():
    metadata.create_all(op.get_bind())

def downgrade():
    metadata.drop_all(op.get_bind())
