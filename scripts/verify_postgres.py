"""Apply migrations and check the configured local PostgreSQL without printing secrets."""

import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
env = dict(os.environ)
for line in (root / ".env").read_text().splitlines():
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        env[key] = value
subprocess.run(
    [str(root / "backend/.venv/bin/alembic"), "upgrade", "head"],
    cwd=root / "backend",
    env=env,
    check=True,
)
os.environ["DATABASE_URL"] = env["DATABASE_URL"]
sys.path.insert(0, str(root / "backend"))
from app.db import Session, engine
from app.models import MODELS, DemoState
from app.seed import seed
from sqlalchemy import inspect, select, text

with Session() as db:
    seed(db)
    assert db.scalar(select(DemoState.id)) == 1
    assert db.scalar(text("SELECT count(*) FROM passenger_journey")) == 580
    assert db.scalar(text("SELECT version_num FROM alembic_version")) == "001"
    assert (
        db.scalar(
            text(
                "SELECT data_type FROM information_schema.columns WHERE table_name='operational_events' AND column_name='metadata'"
            )
        )
        == "jsonb"
    )
assert set(MODELS).issubset(set(inspect(engine).get_table_names()))
print(
    "PostgreSQL migration, normalized tables, JSONB event metadata, and 580 synthetic journey fixtures verified."
)
