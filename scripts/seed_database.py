import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.db import Session
from app.seed import seed

with Session() as db:
    seed(db)
print("Synthetic seed ready. Run Alembic migrations before seeding.")
