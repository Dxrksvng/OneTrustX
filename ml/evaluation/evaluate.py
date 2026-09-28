"""Blocked chronological evaluation with an embargo covering the longest horizon.
Synthetic future observations are not independent evidence of real-world accuracy.
"""

import csv
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
)

root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader((root / "data/synthetic/training.csv").open()))
a = np.array([[float(r[k]) for k in ["queue", "arrivals", "lanes"]] for r in rows])
reports = []
for horizon in [15, 30, 60]:
    x = a[:-horizon]
    y = a[horizon:, 0] / (a[horizon:, 2] * 2)
    split = int(len(x) * 0.7)
    train_end = split - 60
    train = x[:train_end]
    test = x[split:]
    truth = y[split:]
    # Known lane status persists; no future actual arrivals are given to the baseline.
    current = test[:, 0] / (test[:, 2] * 2)
    fluid = np.maximum(0, test[:, 0] + horizon * (test[:, 1] - test[:, 2] * 2)) / (
        test[:, 2] * 2
    )
    ma = np.array(
        [
            np.mean(a[max(0, i - 15) : i + 1, 0] / (a[max(0, i - 15) : i + 1, 2] * 2))
            for i in range(split, len(x))
        ]
    )
    preds = {"persistence": current, "moving_average": ma, "fluid": fluid}
    for name, model in [
        ("linear", LinearRegression()),
        (
            "random_forest",
            RandomForestRegressor(
                n_estimators=60, max_depth=10, random_state=42, n_jobs=1
            ),
        ),
    ]:
        model.fit(train, y[:train_end])
        preds[name] = np.maximum(0, model.predict(test))
    for name, p in preds.items():
        errors = np.abs(truth - p)
        precision, recall, f1, _ = precision_recall_fscore_support(
            truth > 30, p > 30, average="binary", zero_division=0
        )
        # Onset-based lead time, not merely the configured forecast horizon.
        actual_onsets = np.where((truth[1:] > 30) & (truth[:-1] <= 30))[0] + 1
        leads = []
        for onset in actual_onsets:
            # The observed onset occurs at issuance index onset+horizon.
            # Only warnings issued in the preceding horizon count as early detections.
            stop = min(len(p), onset + horizon + 1)
            hits = np.where((p[onset:stop] > 30) & (current[onset:stop] <= 30))[0]
            if len(hits):
                leads.append(horizon - int(hits[0]))
        report = {
            "model": name,
            "horizon_min": horizon,
            "mae": float(mean_absolute_error(truth, p)),
            "rmse": float(np.sqrt(mean_squared_error(truth, p))),
            "p90_absolute_error": float(np.quantile(errors, 0.9)),
            "congestion_precision": float(precision),
            "congestion_recall": float(recall),
            "f1": float(f1),
            "false_alarm_rate": float(np.sum((p > 30) & (truth <= 30)) / max(1, np.sum(truth <= 30))),
            "median_detected_lead_time_min": float(np.median(leads)) if leads else None,
            "detected_onsets": len(leads),
            "total_onsets": len(actual_onsets),
            "heuristic_interval_coverage": float(np.mean(errors <= 0.15 * p + 2)),
            "source_type": "SIMULATED",
        }
        reports.append(report)
output = {
    "notice": "Simulated MVP Result — Not actual airport performance.",
    "split": "First 70% training; last 30% testing; 60-minute embargo; no random shuffle",
    "lead_definition": "Actual congestion onset matched to a warning issued in the prior forecast horizon while current wait remained <=30 minutes; undetected onsets reported separately",
    "seed": 42,
    "library_versions": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
    "threshold_wait_min": 30,
    "promotion": "No ML model promoted. Offline candidates must beat persistence and fluid across horizons and pass independent validation.",
    "results": reports,
}
(root / "docs/evaluation-results.json").write_text(json.dumps(output, indent=2))
lines = [
    "# Synthetic evaluation report",
    "",
    output["notice"],
    "",
    output["split"],
    "",
    "| Model | Horizon | MAE | RMSE | P90 error | Precision | Recall | F1 | Interval coverage |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
]
for r in reports:
    lines.append(
        f"| {r['model']} | {r['horizon_min']} | {r['mae']:.2f} | {r['rmse']:.2f} | {r['p90_absolute_error']:.2f} | {r['congestion_precision']:.2f} | {r['congestion_recall']:.2f} | {r['f1']:.2f} | {r['heuristic_interval_coverage']:.2f} |"
    )
lines += [
    "",
    output["promotion"],
    "",
    "Confidence is a heuristic, not a calibrated probability. Coverage is empirical synthetic test coverage of ±(15% of estimate + 2 min). No airport accuracy claims. Lead times in JSON are onset-matched warning measurements; undetected onsets are reported separately.",
    "",
    "Targets: MAE ≤5 min, recall ≥0.80, warning lead ≥15 min. Targets are MVP aspirations, not industry standards. See JSON for measured results; failing targets are not waived.",
]
(root / "docs/evaluation.md").write_text("\n".join(lines) + "\n")
print(json.dumps(output, indent=2))
