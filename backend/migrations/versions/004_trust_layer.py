"""One TrustX trusted event layer and KPI experiment records."""
from alembic import op
from app import trust_models  # noqa: F401
from app.db import Base

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    names = {
        "trust_organizations", "trust_actors", "trust_scenarios", "trust_events",
        "trust_conflicts", "common_operational_states", "trust_ground_truth",
        "trust_experiment_runs", "trust_kpi_definitions", "trust_kpi_results",
        "trust_recommendations", "trust_decisions",
    }
    for table in Base.metadata.sorted_tables:
        if table.name in names:
            table.create(bind, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    for name in [
        "trust_kpi_results", "trust_kpi_definitions", "trust_experiment_runs",
        "trust_decisions", "trust_recommendations", "trust_ground_truth", "common_operational_states", "trust_conflicts",
        "trust_events", "trust_scenarios", "trust_actors", "trust_organizations",
    ]:
        Base.metadata.tables[name].drop(bind, checkfirst=True)
