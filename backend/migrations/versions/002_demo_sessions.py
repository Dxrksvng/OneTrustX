"""Isolated deterministic browser demos; legacy audit records remain unchanged."""

from alembic import op
from app.models import DemoSession

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    DemoSession.__table__.create(op.get_bind(), checkfirst=True)


def downgrade():
    DemoSession.__table__.drop(op.get_bind(), checkfirst=True)
