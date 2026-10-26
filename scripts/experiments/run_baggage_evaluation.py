"""Export the synthetic baggage scenarios and score the assessment over repeated seeds.

Writes:
  backend/app/baggage_evaluation.json          served by /api/trustx/baggage/evaluation
  data/synthetic/baggage_flow/<scenario>.csv   scan records for seed 42 (what the assessment reads)
  data/synthetic/baggage_flow/flights.csv      synthetic schedule for seed 42
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app import baggage_flow as flow  # noqa: E402
from app import baggage_metrics as metrics  # noqa: E402

SEEDS = range(1, 31)


def main():
    out = ROOT / "data/synthetic/baggage_flow"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "flights.csv").open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["scenario_id", "direction", "flight", "scheduled", "actual_or_estimated", "hold_closes", "local_or_terminating_bags", "transfer_bags", "connection", "source_type"])
        for scenario_id in flow.SCENARIOS:
            run = flow.simulate(scenario_id, 42)
            for f in run.outbound:
                writer.writerow([scenario_id, "DEPARTURE", f.flight, flow.clock(f.etd), flow.clock(f.etd), flow.clock(f.load_close), f.local_bags, f.transfer_bags, f.inbound, "SYNTHETIC"])
            for f in run.inbound:
                writer.writerow([scenario_id, "ARRIVAL", f.flight, flow.clock(f.scheduled_on_block), flow.clock(f.on_block), "", f.terminating_bags, f.transfer_bags, f.connects_to, "SYNTHETIC"])
            with (out / f"{scenario_id}.csv").open("w", newline="") as scans:
                rows = csv.DictWriter(scans, fieldnames=list(run.records[0]), lineterminator="\n")
                rows.writeheader()
                rows.writerows(run.records)
    result = flow.evaluate(SEEDS)
    result["scorecard"] = metrics.scorecard(SEEDS)
    result["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (ROOT / "backend/app/baggage_evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    for key, row in result["scenarios"].items():
        print(key, "missed PLAN", row["bags_missed_plan_policy"]["median"], "PRIORITY", row["bags_missed_priority_policy"]["median"],
              "precision", row["flight_precision"], "recall", row["flight_recall"], "alerts", row["alert_share_of_checks"])


if __name__ == "__main__":
    main()
