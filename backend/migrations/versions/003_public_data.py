"""Public lineage and normalized airport observations, flights and wait-time benchmarks."""
from alembic import op
from app.public_models import PublicDataset, PublicObservation, PublicFlight, PublicQueue
revision='003'
down_revision='002'
branch_labels=None
depends_on=None
def upgrade():
 for model in [PublicDataset,PublicObservation,PublicFlight,PublicQueue]:model.__table__.create(op.get_bind(),checkfirst=True)
def downgrade():
 for model in [PublicQueue,PublicFlight,PublicObservation,PublicDataset]:model.__table__.drop(op.get_bind(),checkfirst=True)
