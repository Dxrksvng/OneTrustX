"""Frozen initial PostgreSQL schema; SQLite uses metadata for developer convenience."""

from pathlib import Path

from alembic import op

from app import models  # noqa: F401
from app.db import Base

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sql = (Path(__file__).resolve().parents[1] / "001_schema.sql").read_text()
        sql = "\n".join(line for line in sql.splitlines() if not line.lstrip().startswith("--"))
        for statement in sql.split(";"):
            if statement.strip():
                op.execute(statement)
    else:
        Base.metadata.create_all(bind)


def downgrade():
    Base.metadata.drop_all(op.get_bind())
