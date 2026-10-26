"""Baggage flow scenarios and the stage-by-stage assessment built on them.

Two halves that must stay separate:

* ``simulate`` is the SYNTHETIC world. It knows capacities, faults and the truth.
* ``assess`` is One TrustX. It sees only what existing systems could provide:
  aggregate scan counts (BRS/BHS), the flight schedule with expected bag counts
  and on-block times (AODB/DCS) and, optionally, a ground-handler resource feed.
  It never reads capacities or ground truth from the simulation.

Every driving parameter comes from ``baggage_calibration.json`` with its tier and source.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from statistics import median

TICK = 5  # minutes
HORIZON = 540  # minutes simulated
RATE_WINDOW = 30  # minutes of scans used to measure the loading pace
BASE = datetime(2026, 9, 26, 5, 0, tzinfo=timezone(timedelta(hours=7)))
DEFAULT_AT = 210
OUTBOUND_STAGES = ("screening", "sorting", "loading")
MANUAL_STAGES = ("loading", "transfer", "arrival")
STAGES = [
    ("check_in", "Check-in", "DCS / BRS acceptance scan"),
    ("screening", "Screening", "BHS screening scan"),
    ("sorting", "Sorting", "BHS / BRS sortation scan"),
    ("loading", "Loading", "BRS load scan"),
    ("transfer", "Transfer", "BRS transfer-area scan"),
    ("arrival", "Arrival", "BRS arrival-belt scan"),
]
LABEL = {s: label for s, label, _ in STAGES}
OWNERS = {
    "screening": "BHS_OPERATOR",
    "sorting": "BHS_OPERATOR",
    "loading": "GROUND_HANDLER",
    "transfer": "GROUND_HANDLER",
    "arrival": "GROUND_HANDLER",
}
SCENARIOS = {
    "BAG-NORMAL": {
        "name": "Normal operations",
        "summary": "Planned staffing and equipment. Control case.",
        "evidence_tier": "SYNTHETIC",
    },
    "BAG-FLOOD-STAFF": {
        "name": "Flood: ground staff cannot reach the airport",
        "summary": "Manual handling capacity falls for the whole shift and baggage carts fail mid-shift. "
        "Shaped on the Sept 2026 Suvarnabhumi incident; the staffing ratio is an assumption.",
        "evidence_tier": "REAL_PUBLIC context + ASSUMPTION parameters",
    },
    "BAG-BHS-FAULT": {
        "name": "Sortation fault",
        "summary": "Sorting capacity drops to a quarter for 75 minutes.",
        "evidence_tier": "ASSUMPTION",
    },
    "BAG-LATE-INBOUND": {
        "name": "Late inbound connections",
        "summary": "Four inbound flights arrive 55 minutes late, shortening transfer windows.",
        "evidence_tier": "ASSUMPTION",
    },
    "BAG-STALE-FEED": {
        "name": "Loading scans stop arriving",
        "summary": "Operations are normal but the loading feed runs 45 minutes behind. "
        "The view must ask for verification, not report a baggage delay.",
        "evidence_tier": "ASSUMPTION",
    },
}


@lru_cache(maxsize=1)
def calibration() -> dict:
    return json.loads((Path(__file__).with_name("baggage_calibration.json")).read_text())


def param(name: str):
    return calibration()["parameters"][name]["value"]


def clock(minute: int) -> str:
    return (BASE + timedelta(minutes=minute)).strftime("%H:%M")


@dataclass(frozen=True)
class Outbound:
    flight: str
    etd: int
    load_close: int
    local_bags: int
    transfer_bags: int
    inbound: str


@dataclass(frozen=True)
class Inbound:
    flight: str
    scheduled_on_block: int
    on_block: int
    transfer_bags: int
    terminating_bags: int
    connects_to: str


@dataclass
class Cohort:
    flight: str  # flight whose deadline or belt this bag belongs to
    bag_class: str  # LOCAL | TRANSFER | TERMINATING
    count: int
    deadline: int


@dataclass
class Run:
    scenario_id: str
    seed: int
    policy: str
    outbound: list[Outbound]
    inbound: list[Inbound]
    records: list[dict] = field(default_factory=list)
    resource_feed: list[dict] = field(default_factory=list)
    missed: dict[str, dict[str, int]] = field(default_factory=dict)
    first_missed_min: int | None = None


def _spread(total: int, weights: list[float]) -> list[int]:
    """Split ``total`` bags over ticks by weight; largest remainders take the leftovers."""
    scale = sum(weights)
    raw = [total * w / scale for w in weights]
    out = [int(x) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)[
        : total - sum(out)
    ]:
        out[i] += 1
    return out


def build_schedule(scenario_id: str, seed: int) -> tuple[list[Outbound], list[Inbound]]:
    rng = random.Random(seed)
    n = param("departures_in_window")
    outbound, inbound = [], []
    late = set(rng.sample(range(n), 4)) if scenario_id == "BAG-LATE-INBOUND" else set()
    for i in range(n):
        etd = 200 + round(i * 300 / (n - 1) / TICK) * TICK
        pax = max(90, min(300, round(rng.gauss(param("avg_passengers_per_movement"), 40))))
        bags = round(pax * param("bags_per_passenger"))
        transfer = round(bags * param("transfer_bag_share") * rng.uniform(0.5, 1.5))
        flight, feeder = f"TT{401 + i}", f"TT{801 + i}"
        close = etd - param("load_close_before_departure_min")
        outbound.append(Outbound(flight, etd, close, bags - transfer, transfer, feeder))
        scheduled = etd - rng.choice(range(90, 155, TICK))
        inbound.append(
            Inbound(
                feeder,
                scheduled,
                scheduled + (55 if i in late else 0),
                transfer,
                round(rng.uniform(80, 160)),
                flight,
            )
        )
    return outbound, inbound


def _acceptance(flight: Outbound) -> dict[int, int]:
    """Local bags accepted per tick: opens 180 min before departure, peaks at 110, closes at the published cutoff."""
    ticks = list(range(flight.etd - 180, flight.etd - param("bag_drop_cutoff_min"), TICK))
    weights = [1 + min(t - ticks[0], ticks[-1] - t + 50) for t in ticks]
    return dict(zip(ticks, _spread(flight.local_bags, weights), strict=False))


def _capacity_factor(scenario_id: str, stage: str, minute: int) -> float:
    if scenario_id == "BAG-FLOOD-STAFF" and stage in MANUAL_STAGES:
        carts = 0.8 if stage == "loading" and 120 <= minute < 300 else 1.0
        return param("flood_staff_ratio") * carts
    if scenario_id == "BAG-BHS-FAULT" and stage == "sorting" and 150 <= minute < 225:
        return 0.25
    return 1.0


def _serve(queue: list[Cohort], capacity: int, policy: str) -> list[Cohort]:
    """Process up to ``capacity`` bags. PLAN shares capacity equally between flights; PRIORITY serves the earliest deadline first."""
    done: list[Cohort] = []
    if policy == "PRIORITY":
        queue.sort(key=lambda c: c.deadline)
        for cohort in queue:
            take = min(cohort.count, capacity)
            if take:
                done.append(Cohort(cohort.flight, cohort.bag_class, take, cohort.deadline))
                cohort.count -= take
                capacity -= take
    else:
        while capacity > 0 and any(c.count for c in queue):
            flights = sorted({c.flight for c in queue if c.count})
            share = max(1, capacity // len(flights))
            for flight in flights:
                budget = min(share, capacity)
                for cohort in queue:
                    if cohort.flight == flight and cohort.count and budget:
                        take = min(cohort.count, budget)
                        done.append(Cohort(cohort.flight, cohort.bag_class, take, cohort.deadline))
                        cohort.count -= take
                        budget -= take
                        capacity -= take
    queue[:] = [c for c in queue if c.count]
    return done


def _busiest(demand: dict[int, int], window: int) -> float:
    """Largest planned bags per tick, averaged over ``window`` minutes."""
    ticks = window // TICK
    return max(
        sum(demand.get(t + k * TICK, 0) for k in range(ticks)) / ticks
        for t in range(0, HORIZON, TICK)
    )


def simulate(scenario_id: str, seed: int = 42, policy: str = "PLAN") -> Run:
    if scenario_id not in SCENARIOS:
        raise KeyError(scenario_id)
    outbound, inbound = build_schedule(scenario_id, seed)
    run = Run(
        scenario_id,
        seed,
        policy,
        outbound,
        inbound,
        missed={f.flight: {"LOCAL": 0, "TRANSFER": 0} for f in outbound},
    )
    by_flight = {f.flight: f for f in outbound}
    accept = {f.flight: _acceptance(f) for f in outbound}
    # Planned demand per tick (scheduled times, no delays) sizes normal capacity.
    plan: dict[str, dict[int, int]] = {"local": {}, "transfer": {}, "arrival": {}}
    for f in outbound:
        for t, n in accept[f.flight].items():
            plan["local"][t] = plan["local"].get(t, 0) + n
    for f in inbound:
        for key, n in (("transfer", f.transfer_bags), ("arrival", f.terminating_bags)):
            for t, part in zip(
                (f.scheduled_on_block, f.scheduled_on_block + TICK), _spread(n, [1, 1]), strict=False
            ):
                plan[key][t] = plan[key].get(t, 0) + part
    plan["outbound"] = {
        t: plan["local"].get(t, 0) + plan["transfer"].get(t, 0) for t in range(0, HORIZON, TICK)
    }
    head = param("normal_capacity_headroom")
    base_cap = {
        "screening": _busiest(plan["local"], TICK),  # automated: sized for the busiest five minutes
        "sorting": _busiest(plan["outbound"], TICK),
        "loading": _busiest(plan["outbound"], 60),  # manual: staffed for the busiest hour
        "transfer": _busiest(plan["transfer"], 60),
        "arrival": _busiest(plan["arrival"], 60),
    }
    base_cap = {k: max(1, round(v * head)) for k, v in base_cap.items()}
    queues: dict[str, list[Cohort]] = {s: [] for s in base_cap}

    def emit(stage: str, minute: int, cohort: Cohort):
        lag = 45 if scenario_id == "BAG-STALE-FEED" and stage == "loading" and minute >= 195 else 1
        run.records.append(
            {
                "record_id": f"{scenario_id}-{seed}-{len(run.records):05d}",
                "scenario_id": scenario_id,
                "seed": seed,
                "stage": stage,
                "flight": cohort.flight,
                "bag_class": cohort.bag_class,
                "count": cohort.count,
                "event_min": minute,
                "ingest_min": minute + lag,
                "source_type": "SYNTHETIC",
            }
        )

    for minute in range(0, HORIZON, TICK):
        for f in outbound:  # acceptance scans
            n = accept[f.flight].get(minute, 0)
            if n:
                cohort = Cohort(f.flight, "LOCAL", n, f.load_close)
                emit("check_in", minute, cohort)
                queues["screening"].append(cohort)
        for f in inbound:  # bags reach the stand over two ticks after on-block
            parts = zip(
                (0, TICK), _spread(f.transfer_bags, [1, 1]), _spread(f.terminating_bags, [1, 1]), strict=False
            )
            for offset, t_part, a_part in parts:
                if minute == f.on_block + offset:
                    if t_part:
                        queues["transfer"].append(
                            Cohort(
                                f.connects_to,
                                "TRANSFER",
                                t_part,
                                by_flight[f.connects_to].load_close,
                            )
                        )
                    if a_part:
                        queues["arrival"].append(
                            Cohort(f.flight, "TERMINATING", a_part, f.on_block)
                        )
        for stage in queues:  # bags whose flight has closed are left behind
            for cohort in queues[stage]:
                if cohort.bag_class != "TERMINATING" and minute >= cohort.deadline:
                    run.missed[cohort.flight][cohort.bag_class] += cohort.count
                    run.first_missed_min = (
                        run.first_missed_min if run.first_missed_min is not None else minute
                    )
                    cohort.count = 0
            queues[stage][:] = [c for c in queues[stage] if c.count]
        moved = {}
        for stage in (
            "arrival",
            "transfer",
            "loading",
            "sorting",
            "screening",
        ):  # downstream first: one stage per tick
            capacity = round(base_cap[stage] * _capacity_factor(scenario_id, stage, minute))
            use = policy if stage in ("sorting", "loading", "transfer") else "PLAN"
            moved[stage] = _serve(queues[stage], capacity, use)
            for cohort in moved[stage]:
                emit(stage, minute, cohort)
        queues["sorting"].extend(moved["screening"] + moved["transfer"])
        queues["loading"].extend(moved["sorting"])
        if scenario_id == "BAG-FLOOD-STAFF" and minute % 30 == 0:
            run.resource_feed.append(
                {
                    "event_min": minute,
                    "ingest_min": minute + 2,
                    "source_type": "SYNTHETIC",
                    "staff_ratio": param("flood_staff_ratio"),
                    "carts_available": "4 of 5" if 120 <= minute < 300 else "5 of 5",
                }
            )
    return run


# --- One TrustX assessment: scans + schedule only -------------------------------------------


def _sum(records, stage, lo=None, hi=None, flights=None, bag_class=None):
    return sum(
        r["count"]
        for r in records
        if r["stage"] == stage
        and (lo is None or r["event_min"] > lo)
        and (hi is None or r["event_min"] <= hi)
        and (flights is None or r["flight"] in flights)
        and (bag_class is None or r["bag_class"] == bag_class)
    )


def _oldest_waiting(inflow: list[tuple[int, int]], processed: int, at: int) -> int:
    """Minutes the bag now at the head of the queue has waited (first in, first out)."""
    total = 0
    for minute, count in sorted(inflow):
        total += count
        if total > processed:
            return at - minute
    return 0


def assess(run: Run, at: int = DEFAULT_AT, use_resource_feed: bool = True) -> dict:
    """Stage status, bottleneck, flights at risk and a recovery priority, from data received by minute ``at``."""
    seen = [r for r in run.records if r["ingest_min"] <= at]
    stale_after, horizon = param("feed_stale_after_min"), param("risk_horizon_min")
    open_flights = {f.flight for f in run.outbound if f.load_close > at}
    landed = [f for f in run.inbound if f.on_block <= at]  # AODB actual on-block
    scans = {s: [r for r in seen if r["stage"] == s] for s, _, _ in STAGES}
    outbound_scans = {
        s: [(r["event_min"], r["count"]) for r in scans[s] if r["flight"] in open_flights]
        for s in scans
    }
    inflow = {
        "screening": outbound_scans["check_in"],
        "sorting": outbound_scans["screening"] + outbound_scans["transfer"],
        "loading": outbound_scans["sorting"],
        "transfer": [
            (f.on_block, f.transfer_bags) for f in landed if f.connects_to in open_flights
        ],
        "arrival": [(f.on_block, f.terminating_bags) for f in landed],
    }
    stages, waits = [], {}
    for stage, label, source in STAGES:
        row = {
            "id": stage,
            "label": label,
            "source": source,
            "status": "OK",
            "queue_bags": None,
            "oldest_bag_wait_min": None,
            "last_scan": clock(max(r["event_min"] for r in scans[stage])) if scans[stage] else None,
            "note": None,
        }
        if stage != "check_in":
            mine = (
                scans[stage]
                if stage == "arrival"
                else [r for r in scans[stage] if r["flight"] in open_flights]
            )
            processed = sum(r["count"] for r in mine)
            queue = max(0, sum(n for _, n in inflow[stage]) - processed)
            wait = _oldest_waiting(inflow[stage], processed, at) if queue else 0
            newest = max((r["event_min"] for r in scans[stage]), default=None)
            limits = param(
                "inbound_wait_thresholds_min"
                if stage in ("transfer", "arrival")
                else "stage_wait_thresholds_min"
            )
            row.update(queue_bags=queue, oldest_bag_wait_min=wait)
            if queue and wait > stale_after and (newest is None or at - newest > stale_after):
                row.update(
                    status="STALE",
                    queue_bags=None,
                    oldest_bag_wait_min=None,
                    note=f"No {label.lower()} scan newer than {clock(newest) if newest is not None else 'the start of shift'} "
                    "while bags are waiting. The stage has stopped or its feed is down.",
                )
            elif queue:
                waits[stage] = wait
                row["status"] = (
                    "DELAY"
                    if wait > limits["delay"]
                    else "WATCH"
                    if wait > limits["watch"]
                    else "OK"
                )
        stages.append(row)
    by_id = {s["id"]: s for s in stages}
    stale = [s for s in stages if s["status"] == "STALE"]
    slow = {k: v for k, v in waits.items() if by_id[k]["status"] in ("WATCH", "DELAY")}
    bottleneck = max(slow, key=slow.get) if slow else None
    loading_blind = by_id["loading"]["status"] == "STALE"

    # Flights at risk. Two independent checks, both from schedule + scans:
    #  1. congestion: if a stage is constrained, do the bags still to load fit at the pace now observed, earliest close first?
    #  2. short connection: does the inbound flight reach the stand too late for its transfer bags?
    pace = _sum(seen, "loading", lo=at - RATE_WINDOW, hi=at) / RATE_WINDOW
    congested = bottleneck in OUTBOUND_STAGES or bottleneck == "transfer"
    feeder = {f.connects_to: f for f in run.inbound}
    flights, ahead = [], 0
    for f in sorted(run.outbound, key=lambda x: x.load_close):
        if f.flight not in open_flights:
            continue
        expected = f.local_bags + f.transfer_bags
        loaded = _sum(seen, "loading", flights={f.flight})
        transfer_left = f.transfer_bags - _sum(
            seen, "loading", flights={f.flight}, bag_class="TRANSFER"
        )
        remaining = expected - loaded
        row = {
            "flight": f.flight,
            "etd": clock(f.etd),
            "hold_closes": clock(f.load_close),
            "minutes_to_close": f.load_close - at,
            "bags_expected": expected,
            "bags_loaded": None if loading_blind else loaded,
            "bags_at_risk": 0,
            "transfer_bags_at_risk": 0,
            "reason": None,
        }
        inbound = feeder[f.flight]
        short = transfer_left and inbound.on_block + param("min_transfer_minutes") > f.load_close
        if loading_blind:
            row.update(
                bags_at_risk=None, transfer_bags_at_risk=None, reason="Loading scans unavailable"
            )
        elif f.load_close - at <= horizon:
            late = 0
            if congested:
                late = min(remaining, max(0, round(ahead + remaining - pace * (f.load_close - at))))
            if short:
                late = max(late, transfer_left)
            if late:
                row.update(
                    bags_at_risk=late,
                    transfer_bags_at_risk=transfer_left if short else min(late, transfer_left),
                    reason=f"Inbound {inbound.flight} on block {clock(inbound.on_block)}: connection too short"
                    if short and not congested
                    else f"{LABEL[bottleneck]} pace"
                    + (f" and short connection from {inbound.flight}" if short else ""),
                )
        ahead += remaining
        flights.append(row)
    at_risk = [f for f in flights if f["bags_at_risk"]]
    if (
        any("connection" in (f["reason"] or "") for f in at_risk)
        and by_id["transfer"]["status"] == "OK"
    ):
        by_id["transfer"]["status"] = "RISK"
        by_id["transfer"]["note"] = "Inbound arrival leaves less than the minimum transfer time."
    closed = [f for f in run.outbound if f.load_close <= at]
    left_behind = (
        None
        if loading_blind
        else sum(
            f.local_bags + f.transfer_bags - _sum(seen, "loading", flights={f.flight})
            for f in closed
        )
    )

    if stale:
        overall = "VERIFY_DATA"
    elif at_risk or any(s["status"] == "DELAY" for s in stages):
        overall = "AT_RISK"
    elif bottleneck:
        overall = "WATCH"
    else:
        overall = "NORMAL"

    feed = [r for r in run.resource_feed if r["ingest_min"] <= at] if use_resource_feed else []
    cause = {"status": "NOT_APPLICABLE", "source": None, "text": "No stage is constrained."}
    if bottleneck:
        if feed and bottleneck in MANUAL_STAGES:
            cause = {
                "status": "REPORTED",
                "source": "Ground-handler resource feed",
                "text": f"Handler reports staff at {round(feed[-1]['staff_ratio'] * 100)}% of plan and carts {feed[-1]['carts_available']}.",
            }
        else:
            cause = {
                "status": "UNKNOWN",
                "source": None,
                "text": "Scans show where the flow is constrained, not why. A resource or equipment feed is needed to name the cause.",
            }

    action = {
        "action": "No action needed",
        "owner": None,
        "deadline": None,
        "approval": "NOT_REQUIRED",
        "priority_order": [],
        "escalation": None,
    }
    if stale:
        names = ", ".join(s["label"] for s in stale)
        action.update(
            action=f"Confirm {names.lower()} status by radio and restore the scan feed before acting on these numbers",
            owner="DATA_OWNER",
            deadline="Now",
            approval="HUMAN_REQUIRED",
        )
    elif at_risk:
        first, order = at_risk[0], [f["flight"] for f in at_risk]
        if congested:
            text = f"Give {LABEL[bottleneck].lower()} capacity to {first['flight']} first (hold closes {first['hold_closes']})"
            text += f", then {', '.join(order[1:4])}" if order[1:] else ""
        else:
            text = f"Arrange direct aircraft-to-aircraft transfer for {first['flight']} or re-flight its {first['transfer_bags_at_risk']} transfer bags"
        action.update(
            action=text,
            owner=OWNERS.get(bottleneck or "transfer"),
            deadline=first["hold_closes"],
            approval="HUMAN_REQUIRED",
            priority_order=order,
        )
        if congested and sum(f["bags_at_risk"] for f in at_risk) > 0.25 * sum(
            f["bags_expected"] for f in at_risk
        ):
            action["escalation"] = (
                "Reordering alone will not clear this. Ask airline operations to review holding flights or re-flighting bags."
            )
    elif bottleneck:
        action.update(
            action=f"Watch {LABEL[bottleneck].lower()}: bags are waiting longer but no flight is at risk yet",
            owner=OWNERS.get(bottleneck),
        )

    evidence = []
    if bottleneck:
        b = by_id[bottleneck]
        evidence = [
            f"{b['label']}: {b['queue_bags']} bags waiting; the oldest has waited {b['oldest_bag_wait_min']} min",
            f"Loading pace over the last {RATE_WINDOW} min: {pace:.1f} bags/min",
            f"{len(at_risk)} of {sum(1 for f in flights if f['minutes_to_close'] <= horizon)} flights closing within {horizon} min cannot be fully loaded at this pace",
        ]
    elif at_risk:
        evidence = [f["reason"] for f in at_risk]
    return {
        "scenario_id": run.scenario_id,
        "scenario": SCENARIOS[run.scenario_id],
        "seed": run.seed,
        "at_min": at,
        "at": clock(at),
        "overall_status": overall,
        "stages": stages,
        "bottleneck": {
            "stage": LABEL.get(bottleneck),
            "stage_id": bottleneck,
            "evidence": evidence,
            "cause": cause,
        },
        "impact": {
            "flights_open": len(flights),
            "flights_at_risk": None if loading_blind else len(at_risk),
            "bags_at_risk": None if loading_blind else sum(f["bags_at_risk"] for f in flights),
            "transfer_bags_at_risk": None
            if loading_blind
            else sum(f["transfer_bags_at_risk"] for f in flights),
            "bags_left_behind_so_far": left_behind,
            "flights": flights,
            "note": "Bags at risk assume the current pace continues. Flights closing later than the horizon are not judged.",
        },
        "next_action": action,
        "inputs_used": [
            "BRS/BHS aggregate scan counts",
            "AODB schedule and on-block times",
            "DCS expected bag counts",
        ]
        + (["Ground-handler resource feed"] if feed else []),
        "privacy": "Aggregate counts per flight and stage only; no passenger name, passport or bag tag is used.",
        "source_type": "SIMULATED",
        "provenance": "Flights, bags and scans are SYNTHETIC. Parameters and their sources: /api/trustx/baggage/calibration.",
    }


@lru_cache(maxsize=64)
def _cached_run(scenario_id: str, seed: int, policy: str = "PLAN") -> Run:
    return simulate(scenario_id, seed, policy)


def control(
    scenario_id: str = "BAG-NORMAL",
    at: int = DEFAULT_AT,
    seed: int = 42,
    use_resource_feed: bool = True,
) -> dict:
    return assess(_cached_run(scenario_id, seed), at, use_resource_feed)


def ground_truth(run: Run) -> dict:
    local = sum(m["LOCAL"] for m in run.missed.values())
    transfer = sum(m["TRANSFER"] for m in run.missed.values())
    return {
        "bags_missed": local + transfer,
        "transfer_bags_missed": transfer,
        "flights_with_missed_bags": sorted(
            k for k, m in run.missed.items() if m["LOCAL"] + m["TRANSFER"]
        ),
        "first_missed_min": run.first_missed_min,
    }


def evaluate(seeds: range = range(1, 31)) -> dict:
    """Repeated runs per scenario: outcome under each loading policy, detection lead time, flight-level hits and false alerts."""

    def spread(values):
        return {"median": median(values), "min": min(values), "max": max(values)}

    out = {}
    for scenario_id in SCENARIOS:
        plan, priority, lead, alerts, checks, hit, flagged_n, missed_n = [], [], [], 0, 0, 0, 0, 0
        for seed in seeds:
            base = simulate(scenario_id, seed, "PLAN")
            truth = ground_truth(base)
            plan.append(truth)
            priority.append(ground_truth(simulate(scenario_id, seed, "PRIORITY")))
            first_alert, flagged = None, set()
            for at in range(60, HORIZON, 15):
                view = assess(base, at)
                raised = view["overall_status"] in ("AT_RISK", "WATCH")
                checks += 1
                alerts += raised
                first_alert = at if raised and first_alert is None else first_alert
                flagged |= {f["flight"] for f in view["impact"]["flights"] if f["bags_at_risk"]}
            if truth["first_missed_min"] is not None and first_alert is not None:
                lead.append(truth["first_missed_min"] - first_alert)
            missed = set(truth["flights_with_missed_bags"])
            hit, flagged_n, missed_n = (
                hit + len(flagged & missed),
                flagged_n + len(flagged),
                missed_n + len(missed),
            )
        out[scenario_id] = {
            "name": SCENARIOS[scenario_id]["name"],
            "runs": len(seeds),
            "runs_with_missed_bags": sum(1 for p in plan if p["bags_missed"]),
            "bags_missed_plan_policy": spread([p["bags_missed"] for p in plan]),
            "bags_missed_priority_policy": spread([p["bags_missed"] for p in priority]),
            "transfer_bags_missed_plan_policy": spread([p["transfer_bags_missed"] for p in plan]),
            "transfer_bags_missed_priority_policy": spread(
                [p["transfer_bags_missed"] for p in priority]
            ),
            "detection_lead_min": spread(lead) if lead else None,
            "flights_flagged": flagged_n,
            "flights_that_missed_bags": missed_n,
            "flagged_and_missed": hit,
            "flight_precision": round(hit / flagged_n, 2) if flagged_n else None,
            "flight_recall": round(hit / missed_n, 2) if missed_n else None,
            "alert_share_of_checks": round(alerts / checks, 3),
        }
    return {
        "source_type": "SIMULATED",
        "seeds": [seeds.start, seeds.stop - 1],
        "calibration_version": calibration()["version"],
        "policies": {
            "PLAN": "Capacity shared equally between flights with bags waiting (assumed baseline; confirm with a handler).",
            "PRIORITY": "Earliest hold-close first at sorting, transfer and loading (the order One TrustX recommends).",
        },
        "definitions": {
            "detection_lead_min": "Minutes between the first WATCH or AT_RISK status and the first bag missed in the same run.",
            "flight_precision": "Of flights flagged with bags at risk at any 15-minute check, the share that did miss bags when nothing was changed.",
            "flight_recall": "Of flights that missed bags, the share flagged beforehand.",
            "alert_share_of_checks": "Share of 15-minute checks that raised WATCH or AT_RISK. In a scenario where no bag is missed, every one is a false alert.",
        },
        "limitations": [
            "Synthetic flights, bags and capacities; not Suvarnabhumi performance.",
            "The baseline policy is an assumption. A real handler may already prioritise better than PLAN.",
            "The same simulation produces both the alerts and the truth they are scored against.",
        ],
        "scenarios": out,
    }


@lru_cache(maxsize=1)
def stored_evaluation() -> dict | None:
    path = Path(__file__).with_name("baggage_evaluation.json")
    return json.loads(path.read_text()) if path.exists() else None
