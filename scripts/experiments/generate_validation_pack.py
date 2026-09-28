"""Generate a multi-scenario, multi-seed validation pack for One TrustX.

This creates repeatable synthetic episodes for engineering validation. It is
deliberately labelled SYNTHETIC and must not be presented as airport results.
The CSV shape is also the contract for importing de-identified real episodes
when an airport data owner supplies them.
"""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "cache"
SCENARIOS = {
    "S1": ("normal_turnaround", 0.85),
    "S2": ("baggage_bottleneck", 1.00),
    "S3": ("gate_conflict", 1.05),
    "S4": ("weather_affected", 1.12),
    "S5": ("multi_factor_disruption", 1.20),
    "S6": ("data_conflict", 1.10),
    "S7": ("missing_late_data", 1.08),
    "S8": ("scale_test", 1.35),
}
CONDITIONS = ("BASELINE", "SHARED_DATA", "ONE_TRUSTX", "ONE_TRUSTX_AI")


def episode(scenario: str, condition: str, seed: int) -> dict[str, float | str | int]:
    name, severity = SCENARIOS[scenario]
    # Stable variation across episodes, independent of condition.
    digest = hashlib.sha256(f"{scenario}:{seed}".encode()).digest()
    jitter = 0.92 + (digest[0] / 255) * 0.16
    baseline_coord = 18.0 * severity * jitter
    baseline_recon = 14.0 * severity * jitter
    baseline_detect = 42.0 * severity * jitter
    if condition == "BASELINE":
        coord, recon, detect, trace, verified, risk = baseline_coord, baseline_recon, baseline_detect, 42.0, 0.0, 1.0
    elif condition == "SHARED_DATA":
        coord, recon, detect, trace, verified, risk = baseline_coord * .62, baseline_recon * .64, baseline_detect * .70, 76.0, 52.0, .82
    elif condition == "ONE_TRUSTX":
        coord, recon, detect, trace, verified, risk = baseline_coord * .44, baseline_recon * .29, baseline_detect * .45, 100.0, 85.7, .75
    else:
        coord, recon, detect, trace, verified, risk = baseline_coord * .39, baseline_recon * .22, baseline_detect * .26, 100.0, 85.7, .50
    return {
        "scenario_id": scenario,
        "scenario_name": name,
        "seed": seed,
        "condition": condition,
        "dataset_type": "SYNTHETIC",
        "coordination_time_s": round(coord, 3),
        "reconciliation_time_s": round(recon, 3),
        "risk_detection_time_s": round(detect, 3),
        "event_traceability_percent": trace,
        "verified_event_rate_percent": verified,
        "delay_risk_proxy": risk,
    }


def main() -> None:
    rows = [episode(s, c, seed) for s in SCENARIOS for seed in range(100) for c in CONDITIONS]
    fields = list(rows[0])
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "onetrustx-validation-runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    for scenario in SCENARIOS:
        for condition in CONDITIONS:
            selected = [r for r in rows if r["scenario_id"] == scenario and r["condition"] == condition]
            out = {"scenario_id": scenario, "scenario_name": SCENARIOS[scenario][0], "condition": condition, "n": len(selected)}
            for metric in fields[5:]:
                values = [float(r[metric]) for r in selected]
                out[f"{metric}_median"] = round(statistics.median(values), 3)
                out[f"{metric}_p25"] = round(sorted(values)[24], 3)
                out[f"{metric}_p75"] = round(sorted(values)[74], 3)
            summary.append(out)
    with (OUT / "onetrustx-validation-summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    manifest = {
        "dataset_id": "onetrustx-validation-pack-v2",
        "dataset_type": "SYNTHETIC",
        "scenarios": len(SCENARIOS),
        "seeds_per_scenario": 100,
        "conditions": list(CONDITIONS),
        "episodes": len(rows),
        "same_episode_across_conditions": True,
        "generator": "generate_validation_pack.py",
        "limitations": [
            "Synthetic process generator; no airport telemetry.",
            "Metrics validate repeatability and comparison logic only.",
            "Delay risk is a modelled proxy, not observed delay probability.",
        ],
        "real_data_contract": "docs/validation-data-contract.md",
    }
    (OUT / "onetrustx-validation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} episodes, {len(summary)} summary rows to {OUT}")


if __name__ == "__main__":
    main()
