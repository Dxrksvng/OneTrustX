"""Export deterministic normalized fixtures without external APIs or personal data."""

import csv
import json
import random
import sys
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.db import Base
from app.engine import Scenario, compare
from app.models import MODELS
from app.seed import seed

root = Path(__file__).resolve().parents[1]
engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
with Session(engine) as db:
    seed(db)
    for name, model in MODELS.items():
        rows = db.scalars(select(model)).all()
        fields = [c.name for c in model.__table__.columns]
        target = root / "data/synthetic" / (name + ".csv")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        c: getattr(row, "details" if c == "metadata" else c)
                        for c in fields
                    }
                )
(root / "data/seeds/peak-scenario.json").write_text(
    json.dumps(
        {
            "source_type": "SYNTHETIC",
            "seed": 42,
            "scenario": {"peak": True, "lanes": 4, "redirect": 0, "gate": "C8"},
            "comparison": compare(Scenario(peak=True)),
        },
        indent=2,
    )
)
# Chronological demand history. No shuffled train/test split.
rng = random.Random(42)
with (root / "data/synthetic/training.csv").open("w") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["minute", "queue", "arrivals", "lanes", "source_type"])
    queue = 40.0
    for t in range(14 * 24 * 60):
        import math

        demand = max(0, 7 + 5 * math.sin(t / 90) + rng.gauss(0, 1.2))
        lanes = 4 if (t // 180) % 4 else 3
        writer.writerow([t, round(queue, 3), round(demand, 3), lanes, "SYNTHETIC"])
        queue = max(0, queue + demand - lanes * 2)
print("Exported SYNTHETIC fixtures and chronological history (seed 42).")
