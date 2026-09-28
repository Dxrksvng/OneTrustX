"""External immigration benchmark, explicitly not a BKK security calibration."""

import csv, json
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
)
from common import ROOT

rows = []
for p in sorted((ROOT / "data/normalized").glob("cbp_*.csv")):
    for r in csv.DictReader(p.open()):
        try:
            if float(r["BoothsUsed"]) <= 0:
                continue
            rows.append(r)
        except (ValueError, TypeError):
            continue
rows.sort(
    key=lambda r: (r["FlightDate"], r["HourRange"], r["AirportCode"], r["TerminalName"])
)
wait = np.array([float(r["AverageWait"]) for r in rows])
load = np.array(
    [float(r["TotalPassengerCount"]) / float(r["BoothsUsed"]) / 60 for r in rows]
)
features = []
persistence = []
moving = []
history = {}
for r in rows:
    key = (r["AirportCode"], r["TerminalName"])
    prior = history.setdefault(key, [])
    persistence.append(prior[-1] if prior else np.nan)
    moving.append(float(np.mean(prior[-3:])) if prior else np.nan)
    features.append(
        [
            float(r["TotalPassengerCount"]),
            float(r["BoothsUsed"]),
            float(r["FlightCount"]),
            int(r["HourRange"][:2]),
            float(r["TotalPassengerCount"]) / float(r["BoothsUsed"]),
        ]
    )
    prior.append(float(r["AverageWait"]))
x = np.asarray(features)
train = np.array([r["FlightDate"] < "2025-02-01" for r in rows])
valid = np.array(["2025-02-01" <= r["FlightDate"] < "2025-03-01" for r in rows])
test = np.array([r["FlightDate"] >= "2025-03-01" for r in rows])
models = {}
rate = float(np.median(load[train]))
preds = {
    "persistence": np.asarray(persistence),
    "moving_average": np.asarray(moving),
    "queue_load_proxy": np.maximum(0, x[:, 4] - rate * 60) / max(rate, 0.001),
}
for name, model in [
    ("linear", LinearRegression()),
    (
        "random_forest",
        RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42, n_jobs=1),
    ),
]:
    model.fit(x[train], wait[train])
    preds[name] = np.maximum(0, model.predict(x))
results = []
for name, p in preds.items():
    for label, mask in [("validation", valid), ("test", test)]:
        mask = mask & np.isfinite(p)
        truth = wait[mask]
        estimate = p[mask]
        pr, re, f1, _ = precision_recall_fscore_support(
            truth > 30, estimate > 30, average="binary", zero_division=0
        )
        results.append(
            dict(
                model=name,
                split=label,
                records=int(mask.sum()),
                mae=float(mean_absolute_error(truth, estimate)),
                rmse=float(np.sqrt(mean_squared_error(truth, estimate))),
                precision=float(pr),
                recall=float(re),
                f1=float(f1),
                false_alarm_rate=float(
                    np.sum((estimate > 30) & (truth <= 30))
                    / max(1, np.sum(truth <= 30))
                ),
                lead_time_min=None,
            )
        )
output = {
    "source_type": "DERIVED_REAL",
    "source": "CBP Airport Wait Times",
    "geography": "US / JFK, LAX, SFO",
    "records": len(rows),
    "period": "2025-01-01/2025-03-31",
    "wait_quantiles": dict(
        zip(
            ["p10", "p50", "p90", "p95"],
            map(float, np.quantile(wait, [0.1, 0.5, 0.9, 0.95])),
        )
    ),
    "load_per_booth_min_quantiles": dict(
        zip(["p10", "p50", "p90"], map(float, np.quantile(load, [0.1, 0.5, 0.9])))
    ),
    "results": results,
    "split": "January training; February validation; March final test; no random shuffle. Prior-wait baselines use only previously observed rows per airport/terminal.",
    "scope": "Concurrent hourly immigration wait estimation using observed hourly counts; NOT a +15/+30 security forecast. Lead time is not evaluated. Counts cannot be known in advance without a separate demand forecast.",
    "promotion": "No model promoted to BKK. CBP rates are not security service rates. Empirical wait distributions provide external plausibility bounds only; BKK lane capacity remains an assumption.",
    "constraints": "No inferred records for missing airport/terminal hours; no extrapolation to all BKK passengers.",
}
(ROOT / "data/cache/queue-benchmark.json").write_text(json.dumps(output, indent=2))
print(output["records"], output["wait_quantiles"])
