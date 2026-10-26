"""Generate a multi-scenario, multi-seed validation pack for One TrustX.

This creates repeatable synthetic episodes for engineering validation. It is
deliberately labelled SYNTHETIC and must not be presented as airport results.
The CSV shape is also the contract for importing de-identified real episodes
when an airport data owner supplies them.

v3 adds a disaster/compound-scenario family (S9-S14) calibrated against
``data/scenarios/scenario_library.json`` (flood+baggage backlog, geopolitical
airspace closure, terminal fire, health screening disruption, our own
BHS/trust-pipeline outage, and terminal power disruption), plus deterministic
failure injection (missing/late/duplicate/conflict/stale) per episode. The
original S1-S8 formulas are untouched, so every percentage previously cited
in docs/evaluation.md is scenario-invariant and still holds: each condition's
reduction is a fixed multiplier of that episode's own baseline, so adding
scenarios changes absolute seconds, never the cited percentages.
"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "cache"
LIBRARY_PATH = ROOT / "data" / "scenarios" / "scenario_library.json"

# name, severity multiplier, scenario_family, provenance_tier, failure_injection_types
SCENARIOS: dict[str, tuple[str, float, str, str, tuple[str, ...]]] = {
    "S1": ("normal_turnaround", 0.85, "SINGLE", "SYNTHETIC", ()),
    "S2": ("baggage_bottleneck", 1.00, "SINGLE", "SYNTHETIC", ()),
    "S3": ("gate_conflict", 1.05, "SINGLE", "SYNTHETIC", ()),
    "S4": ("weather_affected", 1.12, "SINGLE", "SYNTHETIC", ()),
    "S5": ("multi_factor_disruption", 1.20, "COMPOUND", "SYNTHETIC", ()),
    "S6": ("data_conflict", 1.10, "SINGLE", "SYNTHETIC", ("CONTRADICTORY_EVENT",)),
    "S7": (
        "missing_late_data",
        1.08,
        "SINGLE",
        "SYNTHETIC",
        ("MISSING_EVENT", "LATE_EVENT"),
    ),
    "S8": ("scale_test", 1.35, "SINGLE", "SYNTHETIC", ()),
    "S9": (
        "flood_baggage_compound",
        1.45,
        "COMPOUND",
        "REAL_PUBLIC+BENCHMARK+ASSUMPTION",
        ("LATE_EVENT", "MISSING_EVENT", "STALE_SOURCE", "CONTRADICTORY_EVENT"),
    ),
    "S10": (
        "geopolitical_airspace_closure",
        1.30,
        "SINGLE",
        "REAL_PUBLIC+ASSUMPTION",
        ("CONTRADICTORY_EVENT", "LATE_EVENT"),
    ),
    "S11": (
        "terminal_utility_fire",
        1.55,
        "SINGLE",
        "ASSUMPTION",
        ("MISSING_EVENT", "DUPLICATE_EVENT", "STALE_SOURCE"),
    ),
    "S12": (
        "health_screening_disruption",
        1.15,
        "SINGLE",
        "REAL_PUBLIC+ASSUMPTION",
        ("LATE_EVENT", "STALE_SOURCE"),
    ),
    "S13": (
        "bhs_and_trust_pipeline_outage",
        1.60,
        "CASCADING",
        "ASSUMPTION",
        ("STALE_SOURCE", "CONTRADICTORY_EVENT", "MISSING_EVENT", "DUPLICATE_EVENT"),
    ),
    "S14": (
        "terminal_power_disruption",
        1.40,
        "SINGLE",
        "ASSUMPTION",
        ("MISSING_EVENT", "LATE_EVENT"),
    ),
}
CONDITIONS = ("BASELINE", "SHARED_DATA", "ONE_TRUSTX", "ONE_TRUSTX_AI")
METRIC_FIELDS = (
    "coordination_time_s",
    "reconciliation_time_s",
    "risk_detection_time_s",
    "event_traceability_percent",
    "verified_event_rate_percent",
    "delay_risk_proxy",
    "ground_truth_state_match",
)


def pick_failure(scenario: str, seed: int) -> tuple[bool, str]:
    """Deterministic failure-mode draw, independent of condition.

    Every condition for a given (scenario, seed) sees the same injected
    failure, so the comparison stays paired: BASELINE and ONE_TRUSTX_AI are
    scored on the identical adverse input, not an easier one.
    """
    _, _, _, _, failure_types = SCENARIOS[scenario]
    if not failure_types:
        return False, "NONE"
    digest = hashlib.sha256(f"failure:{scenario}:{seed}".encode()).digest()
    # ~55% of episodes in a failure-eligible scenario actually inject a failure;
    # the rest are the scenario's disruption without an added data-quality fault.
    if digest[1] / 255 >= 0.55:
        return False, "NONE"
    choice = failure_types[digest[2] % len(failure_types)]
    return True, choice


def episode(
    scenario: str, condition: str, seed: int
) -> dict[str, float | str | int | bool]:
    name, severity, family, provenance_tier, _ = SCENARIOS[scenario]
    # Stable variation across episodes, independent of condition.
    digest = hashlib.sha256(f"{scenario}:{seed}".encode()).digest()
    jitter = 0.92 + (digest[0] / 255) * 0.16
    injected, failure_type = pick_failure(scenario, seed)
    # Injected failures add latency/ambiguity before any workflow effect is applied.
    failure_penalty = 1.18 if injected else 1.0

    baseline_coord = 18.0 * severity * jitter * failure_penalty
    baseline_recon = 14.0 * severity * jitter * failure_penalty
    baseline_detect = 42.0 * severity * jitter * failure_penalty
    if condition == "BASELINE":
        coord, recon, detect, trace, verified, risk = (
            baseline_coord,
            baseline_recon,
            baseline_detect,
            42.0,
            0.0,
            1.0,
        )
        # A stale/contradictory source with no reconciliation layer is read literally:
        # BASELINE has no mechanism to prefer ground truth over a stale report.
        gt_match = 0.0 if injected else 1.0
    elif condition == "SHARED_DATA":
        coord, recon, detect, trace, verified, risk = (
            baseline_coord * 0.62,
            baseline_recon * 0.64,
            baseline_detect * 0.70,
            76.0,
            52.0,
            0.82,
        )
        gt_match = 0.35 if injected else 1.0
    elif condition == "ONE_TRUSTX":
        coord, recon, detect, trace, verified, risk = (
            baseline_coord * 0.44,
            baseline_recon * 0.29,
            baseline_detect * 0.45,
            100.0,
            85.7,
            0.75,
        )
        gt_match = 0.80 if injected else 1.0
    else:
        coord, recon, detect, trace, verified, risk = (
            baseline_coord * 0.39,
            baseline_recon * 0.22,
            baseline_detect * 0.26,
            100.0,
            85.7,
            0.50,
        )
        gt_match = 0.91 if injected else 1.0
    return {
        "scenario_id": scenario,
        "scenario_name": name,
        "scenario_family": family,
        "provenance_tier": provenance_tier,
        "seed": seed,
        "condition": condition,
        "dataset_type": "SYNTHETIC",
        "failure_injected": injected,
        "failure_type": failure_type,
        "coordination_time_s": round(coord, 3),
        "reconciliation_time_s": round(recon, 3),
        "risk_detection_time_s": round(detect, 3),
        "event_traceability_percent": trace,
        "verified_event_rate_percent": verified,
        "delay_risk_proxy": risk,
        "ground_truth_state_match": gt_match,
    }


def main() -> None:
    rows = [
        episode(s, c, seed)
        for s in SCENARIOS
        for seed in range(100)
        for c in CONDITIONS
    ]
    fields = list(rows[0])
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "onetrustx-validation-runs.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    for scenario in SCENARIOS:
        for condition in CONDITIONS:
            selected = [
                r
                for r in rows
                if r["scenario_id"] == scenario and r["condition"] == condition
            ]
            out = {
                "scenario_id": scenario,
                "scenario_name": SCENARIOS[scenario][0],
                "scenario_family": SCENARIOS[scenario][2],
                "condition": condition,
                "n": len(selected),
                "failure_injected_rate": round(
                    sum(1 for r in selected if r["failure_injected"]) / len(selected), 3
                ),
            }
            for metric in METRIC_FIELDS:
                values = [float(r[metric]) for r in selected]
                out[f"{metric}_median"] = round(statistics.median(values), 3)
                out[f"{metric}_p25"] = round(sorted(values)[24], 3)
                out[f"{metric}_p75"] = round(sorted(values)[74], 3)
            summary.append(out)
    with (OUT / "onetrustx-validation-summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    library_scenarios = []
    if LIBRARY_PATH.exists():
        library_scenarios = [
            s["scenario_id"]
            for s in json.loads(LIBRARY_PATH.read_text()).get("scenarios", [])
        ]

    manifest = {
        "dataset_id": "onetrustx-validation-pack-v3",
        "dataset_type": "SYNTHETIC",
        "scenarios": len(SCENARIOS),
        "scenario_families": sorted({v[2] for v in SCENARIOS.values()}),
        "disaster_scenarios_linked_to_scenario_library": library_scenarios,
        "seeds_per_scenario": 100,
        "conditions": list(CONDITIONS),
        "episodes": len(rows),
        "same_episode_across_conditions": True,
        "generator": "generate_validation_pack.py",
        "failure_injection": {
            "types": [
                "MISSING_EVENT",
                "LATE_EVENT",
                "DUPLICATE_EVENT",
                "CONTRADICTORY_EVENT",
                "STALE_SOURCE",
            ],
            "note": "Deterministic per (scenario, seed), identical across all 4 conditions for a paired comparison.",
        },
        "limitations": [
            "Synthetic process generator; no airport telemetry.",
            "Metrics validate repeatability and comparison logic only.",
            "Delay risk is a modelled proxy, not observed delay probability.",
            "ground_truth_state_match is a modelled reconciliation-success proxy, not a measured detection accuracy from production data.",
            "S9-S14 severity/condition multipliers are ASSUMPTION-tier design parameters; only the cited real-world facts in data/scenarios/scenario_library.json are REAL_PUBLIC.",
        ],
        "real_data_contract": "docs/validation-data-contract.md",
        "scenario_library": "data/scenarios/scenario_library.json",
    }
    (OUT / "onetrustx-validation-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(rows)} episodes, {len(summary)} summary rows to {OUT}")


if __name__ == "__main__":
    main()
