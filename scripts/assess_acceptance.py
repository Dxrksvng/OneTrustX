"""Report configurable synthetic model targets without silently promoting a model."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
targets = json.loads((root / "data/seeds/acceptance.json").read_text())
evaluation = json.loads((root / "docs/evaluation-results.json").read_text())
checks = []
for row in evaluation["results"]:
    if row["model"] != "fluid":
        continue
    lead = row["median_detected_lead_time_min"]
    checks.append(
        {
            "horizon_min": row["horizon_min"],
            "mae": row["mae"],
            "mae_pass": row["mae"] <= targets["queue_mae_max_min"],
            "recall": row["congestion_recall"],
            "recall_pass": row["congestion_recall"] >= targets["congestion_recall_min"],
            "lead_time_min": lead,
            "lead_time_pass": lead is not None and lead >= targets["warning_lead_min"],
        }
    )
result = {
    "source_type": "SIMULATED",
    "notice": evaluation["notice"],
    "engine": "fluid",
    "targets": targets,
    "checks": checks,
    "all_model_targets_met": all(
        x["mae_pass"] and x["recall_pass"] and x["lead_time_pass"] for x in checks
    ),
    "ml_promoted": False,
    "interpretation": "Synthetic benchmark only; unmet targets remain visible and require further validation/improvement.",
}
(root / "docs/acceptance-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
