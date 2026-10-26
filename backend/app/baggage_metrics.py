"""Measured scorecard for the baggage use case, in the Trust / Intelligence / Operation pillars.

Every value here is computed by running the simulation; none is a constant.
Trust metrics come from fault injection: known faults are added to the scan feed,
the verification rules run, and the result is scored against what was injected.
"""

from __future__ import annotations

import random
from statistics import median

from . import baggage_flow as flow

FAULT_RATE = 0.02  # share of records given each record-level fault (ASSUMPTION; sets how hard the test is, not the score)
MISSING_BLOCKS = 3  # (flight, stage) scan blocks removed per run
USD_PER_MISHANDLED_BAG = 260  # SITA Baggage IT Insights 2026 (BENCHMARK)
CHECKS = range(60, flow.HORIZON, 15)
# (upstream stage, downstream stage, bag classes that follow this path), most downstream pair first
CHAIN = [
    ("sorting", "loading", ("LOCAL", "TRANSFER")),
    ("screening", "sorting", ("LOCAL",)),
    ("transfer", "sorting", ("TRANSFER",)),
    ("check_in", "screening", ("LOCAL",)),
]


def inject_faults(run: flow.Run, seed: int) -> tuple[list[dict], dict[str, set]]:
    """Return a faulted copy of the scan feed and the ground truth of what was injected."""
    rng = random.Random(seed * 7919)
    records = [dict(r) for r in run.records]
    truth: dict[str, set] = {
        "DUPLICATE": set(),
        "LATE": set(),
        "CORRUPT": set(),
        "UNKNOWN_FLIGHT": set(),
        "MISSING": set(),
        "LOST": set(),
    }
    flights = [f.flight for f in run.outbound]
    for _ in range(MISSING_BLOCKS):  # a stage's scans for one flight never arrive
        key = (rng.choice(flights), rng.choice(["screening", "sorting"]))
        truth["MISSING"].add(key)
        truth["LOST"].add(key)
    records = [r for r in records if (r["flight"], r["stage"]) not in truth["MISSING"]]
    extra = []
    for r in records:
        roll = rng.random()
        if roll < FAULT_RATE:
            extra.append(dict(r))  # same message delivered twice
            truth["DUPLICATE"].add(r["record_id"])
        elif roll < 2 * FAULT_RATE:
            r["ingest_min"] = r["event_min"] + rng.choice([25, 40, 60])
            truth["LATE"].add(r["record_id"])
        elif roll < 3 * FAULT_RATE:
            truth["LOST"].add((r["flight"], r["stage"]))
            r["count"] = rng.choice([0, -r["count"], r["count"] + 5000])
            truth["CORRUPT"].add(r["record_id"])
        elif roll < 4 * FAULT_RATE:
            truth["LOST"].add((r["flight"], r["stage"]))
            r["flight"] = "ZZ" + r["flight"][2:]
            truth["UNKNOWN_FLIGHT"].add(r["record_id"])
    return records + extra, truth


def verify(records: list[dict], run: flow.Run) -> tuple[list[dict], dict[str, set]]:
    """Verification rules of the event layer. Returns accepted records and what each rule flagged."""
    known = {f.flight for f in run.outbound} | {f.flight for f in run.inbound}
    largest = max(f.local_bags + f.transfer_bags for f in run.outbound) + max(
        f.terminating_bags for f in run.inbound
    )
    late_after = flow.param("feed_stale_after_min")
    flags: dict[str, set] = {
        "DUPLICATE": set(),
        "LATE": set(),
        "CORRUPT": set(),
        "UNKNOWN_FLIGHT": set(),
        "MISSING": set(),
    }
    seen, accepted = set(), []
    for r in records:
        rid = r["record_id"]
        if rid in seen:
            flags["DUPLICATE"].add(rid)
            continue
        seen.add(rid)
        if r["flight"] not in known:
            flags["UNKNOWN_FLIGHT"].add(rid)
            continue
        if not 0 < r["count"] <= largest:
            flags["CORRUPT"].add(rid)
            continue
        if r["ingest_min"] - r["event_min"] > late_after:
            flags["LATE"].add(rid)  # kept, but marked: it describes the past
        accepted.append(r)
    # Reconciliation: a bag scanned downstream must have passed the stage before it. Where upstream
    # scans are short, flag the gap and add an inferred upstream record so counts stay consistent.
    outbound = {f.flight for f in run.outbound}
    for upstream, downstream, classes in CHAIN:
        for flight in outbound:
            for bag_class in classes:
                down = sorted(
                    (r["event_min"], r["count"])
                    for r in accepted
                    if r["flight"] == flight
                    and r["stage"] == downstream
                    and r["bag_class"] == bag_class
                )
                up = sorted(
                    (r["event_min"], r["count"])
                    for r in accepted
                    if r["flight"] == flight
                    and r["stage"] == upstream
                    and r["bag_class"] == bag_class
                )
                seen_up = seen_down = i = 0
                for minute, count in down:
                    while i < len(up) and up[i][0] <= minute:
                        seen_up += up[i][1]
                        i += 1
                    seen_down += count
                    if seen_down > seen_up:
                        gap = seen_down - seen_up
                        flags["MISSING"].add((flight, upstream))
                        accepted.append(
                            {
                                "record_id": f"inferred-{flight}-{upstream}-{bag_class}-{minute}",
                                "scenario_id": run.scenario_id,
                                "seed": run.seed,
                                "stage": upstream,
                                "flight": flight,
                                "bag_class": bag_class,
                                "count": gap,
                                "event_min": minute,
                                "ingest_min": minute + 1,
                                "source_type": "DERIVED",
                            }
                        )
                        seen_up += gap
    return accepted, flags


def _with_records(run: flow.Run, records: list[dict]) -> flow.Run:
    return flow.Run(
        run.scenario_id, run.seed, run.policy, run.outbound, run.inbound, records, run.resource_feed
    )


def _spread(values):
    return {"median": median(values), "min": min(values), "max": max(values)} if values else None


def trust_metrics(seeds: range, scenarios=("BAG-NORMAL", "BAG-FLOOD-STAFF")) -> dict:
    caught = {k: 0 for k in ("DUPLICATE", "LATE", "CORRUPT", "UNKNOWN_FLIGHT", "MISSING")}
    injected = dict(caught)
    wrongly = dict(caught)
    clean_total = clean_rejected = checks = 0
    outcome = {
        "raw": {"same": 0, "asks_to_verify": 0, "different": 0},
        "verified": {"same": 0, "asks_to_verify": 0, "different": 0},
    }
    for scenario_id in scenarios:
        for seed in seeds:
            run = flow.simulate(scenario_id, seed)
            faulted, truth = inject_faults(run, seed)
            accepted, flags = verify(faulted, run)
            for kind in caught:
                injected[kind] += len(truth[kind])
                caught[kind] += len(truth[kind] & flags[kind])
                wrongly[kind] += len(
                    flags[kind] - (truth["LOST"] if kind == "MISSING" else truth[kind])
                )
            touched = (
                truth["DUPLICATE"] | truth["LATE"] | truth["CORRUPT"] | truth["UNKNOWN_FLIGHT"]
            )
            clean_ids = {
                r["record_id"]
                for r in run.records
                if (r["flight"], r["stage"]) not in truth["MISSING"]
            } - touched
            accepted_ids = {r["record_id"] for r in accepted}
            clean_total += len(clean_ids)
            clean_rejected += len(clean_ids - accepted_ids)
            raw_run, verified_run = _with_records(run, faulted), _with_records(run, accepted)
            for at in CHECKS:
                reference = flow.assess(run, at)["overall_status"]
                for name, candidate in (("raw", raw_run), ("verified", verified_run)):
                    status = flow.assess(candidate, at)["overall_status"]
                    key = (
                        "same"
                        if status == reference
                        else "asks_to_verify"
                        if status == "VERIFY_DATA"
                        else "different"
                    )
                    outcome[name][key] += 1
                checks += 1
    record_kinds = ("DUPLICATE", "LATE", "CORRUPT", "UNKNOWN_FLIGHT")
    return {
        "runs": len(seeds) * len(scenarios),
        "scenarios": list(scenarios),
        "fault_catch_rate": {
            k: {
                "injected": injected[k],
                "caught": caught[k],
                "rate": round(caught[k] / injected[k], 3) if injected[k] else None,
                "flagged_but_not_injected": wrongly[k],
            }
            for k in caught
        },
        "record_fault_catch_rate": round(
            sum(caught[k] for k in record_kinds) / sum(injected[k] for k in record_kinds), 3
        ),
        "clean_records": clean_total,
        "clean_records_rejected": clean_rejected,
        "false_reject_rate": round(clean_rejected / clean_total, 4),
        "status_checks": checks,
        "status_vs_clean_feed": {
            name: {k: round(v / checks, 3) for k, v in counts.items()}
            for name, counts in outcome.items()
        },
    }


def operation_metrics(
    seeds: range, scenarios=("BAG-FLOOD-STAFF", "BAG-BHS-FAULT", "BAG-LATE-INBOUND")
) -> dict:
    out = {}
    for scenario_id in scenarios:
        windows, plan_bags, prio_bags, plan_tr, prio_tr, better, same, worse = (
            [],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        for seed in seeds:
            base = flow.simulate(scenario_id, seed, "PLAN")
            a, b = (
                flow.ground_truth(base),
                flow.ground_truth(flow.simulate(scenario_id, seed, "PRIORITY")),
            )
            plan_bags, prio_bags = plan_bags + a["bags_missed"], prio_bags + b["bags_missed"]
            plan_tr, prio_tr = (
                plan_tr + a["transfer_bags_missed"],
                prio_tr + b["transfer_bags_missed"],
            )
            better, same, worse = (
                better + (b["bags_missed"] < a["bags_missed"]),
                same + (b["bags_missed"] == a["bags_missed"]),
                worse + (b["bags_missed"] > a["bags_missed"]),
            )
            close = {f.flight: f.load_close for f in base.outbound}
            for at in CHECKS:
                risky = [
                    f["flight"]
                    for f in flow.assess(base, at)["impact"]["flights"]
                    if f["bags_at_risk"]
                ]
                if risky:
                    windows.append(
                        close[risky[0]] - at
                    )  # minutes the operator has before the first named flight closes
                    break
        saved = plan_bags - prio_bags
        out[scenario_id] = {
            "runs": len(seeds),
            "bags_missed_total_plan": plan_bags,
            "bags_missed_total_priority": prio_bags,
            "bags_missed_reduction_pct": round(saved / plan_bags * 100, 1) if plan_bags else None,
            "transfer_bags_missed_total_plan": plan_tr,
            "transfer_bags_missed_total_priority": prio_tr,
            "transfer_bags_missed_reduction_pct": round((plan_tr - prio_tr) / plan_tr * 100, 1)
            if plan_tr
            else None,
            "runs_priority_better": better,
            "runs_priority_same": same,
            "runs_priority_worse": worse,
            "recommendation_not_worse_pct": round((better + same) / len(seeds) * 100, 1),
            "decision_window_min": _spread(windows),
            "bags_saved_per_shift_mean": round(saved / len(seeds), 1),
            "cost_avoided_usd_per_shift_mean": round(saved / len(seeds) * USD_PER_MISHANDLED_BAG),
        }
    return out


def provenance_coverage() -> dict:
    params = flow.calibration()["parameters"]
    complete = sum(
        1
        for p in params.values()
        if p.get("tier") and p.get("source") and (p["tier"] == "ASSUMPTION" or p.get("url"))
    )
    return {
        "parameters": len(params),
        "with_tier_and_source": complete,
        "coverage_pct": round(complete / len(params) * 100, 1),
        "by_tier": {
            t: sum(1 for p in params.values() if p["tier"] == t)
            for t in sorted({p["tier"] for p in params.values()})
        },
    }


def scorecard(seeds: range = range(1, 31)) -> dict:
    return {
        "source_type": "SIMULATED",
        "seeds": [seeds.start, seeds.stop - 1],
        "trust": {"fault_injection": trust_metrics(seeds), "provenance": provenance_coverage()},
        "operation": operation_metrics(seeds),
        "assumptions": {
            "fault_rate_per_record_fault": FAULT_RATE,
            "missing_blocks_per_run": MISSING_BLOCKS,
            "usd_per_mishandled_bag": USD_PER_MISHANDLED_BAG,
            "baseline_policy": "PLAN: capacity shared equally between flights (assumed)",
        },
        "not_measured": {
            "human_coordination_time": "Needs a timed exercise with controllers: same scenario with and without the view, from first alert to an owner accepting the action.",
            "flight_delay_minutes": "The model counts bags left behind; it does not simulate holding or delaying flights.",
        },
    }
