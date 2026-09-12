"""Deterministic minute-step fluid queues, network-aware comparisons, and FIFO cohorts.
All service rates, layouts, arrival profiles and uncertainty bands are assumptions.
"""

from dataclasses import dataclass

import networkx as nx
import numpy as np

LABEL = "Simulated MVP Result — Not actual airport performance."
EDGES = [
    ("Entrance", "Check-in A", 3, True),
    ("Entrance", "Check-in B", 4, True),
    ("Check-in A", "Bag Drop", 2, True),
    ("Check-in B", "Bag Drop", 2, True),
    ("Bag Drop", "Food C", 2, True),
    ("Food C", "Security A", 2, True),
    ("Food C", "Security B", 5, True),
    ("Security A", "Immigration", 2, True),
    ("Security B", "Immigration", 3, True),
    ("Immigration", "Retail", 2, True),
    ("Retail", "C8", 2, True),
    ("Retail", "E7", 25, True),
    ("Retail", "E7", 18, False),
    ("C8", "Exit", 5, True),
    ("E7", "Exit", 6, True),
    ("Baggage Reclaim", "Exit", 4, True),
]


def graph(accessible=True):
    g = nx.DiGraph()
    for a, b, t, access in EDGES:
        if accessible and not access:
            continue
        if g.has_edge(a, b) and g[a][b]["walking_time_min"] <= t:
            continue
        g.add_edge(
            a,
            b,
            walking_time_min=t,
            walking_distance_m=t * 65,
            accessible=access,
            direction="FORWARD",
            capacity=120,
        )
    return g


def risk(wait):
    return "RED" if wait >= 30 else "ORANGE" if wait >= 20 else "YELLOW" if wait >= 10 else "GREEN"


@dataclass
class Scenario:
    peak: bool = False
    lanes: int = 4
    redirect: float = 0.0
    gate: str = "C8"
    version: int = 1
    stale: bool = False


def arrivals(peak=True):
    # 17:00–17:30: 15.2 pax/min. Queue 96 + 456 - 240 = 312; wait 312/8 = 39.
    return [15.2 if peak and t < 30 else (9 if peak and t < 45 else 5) for t in range(60)]


def queue_step(queue, demand, lanes, rate=2.0, minutes=1):
    if min(queue, demand, lanes, rate, minutes) < 0:
        raise ValueError("Queue inputs must be non-negative")
    capacity = lanes * rate * minutes
    served = min(queue + demand, capacity)
    return max(0, queue + demand - served), served


def simulate(s: Scenario, lanes=None, redirect=None, staff=0, delay=0, enforce_staff=True):
    lanes = s.lanes if lanes is None else lanes
    redirect = s.redirect if redirect is None else redirect
    if (
        not 0 <= lanes <= 5
        or not 0 <= redirect <= 0.3
        or not 0 <= staff <= 4
        or not 0 <= delay <= 30
    ):
        raise ValueError("Intervention outside safe demo constraints")
    if enforce_staff and max(0, lanes - s.lanes) * 2 + staff > 4:
        raise ValueError("Only four reserve staff available (ASSUMPTION)")
    demands = arrivals(s.peak)
    if delay:
        demands = [5.0] * delay + demands[: 60 - delay]
    # Existing queues and all arriving cohorts are drained, avoiding horizon-censoring.
    queues = [96.0, 12.0]
    cohorts = [[[0.0, 96.0]], [[0.0, 12.0]]]
    waits, weights = [], []
    series = []
    area = 0.0
    served_total = 0.0
    peak_q = sum(queues)
    overflow = 0.0
    added = 0.0
    capacities = [lanes * 2 + staff * 0.25, 6.0]
    initial = sum(queues)
    for t in range(600):
        a = demands[t] if t < 60 else 0.0
        b = 3.0 if t < 60 else 0.0
        incoming = [a * (1 - redirect), b + a * redirect]
        added += sum(incoming)
        for j in range(2):
            if incoming[j]:
                cohorts[j].append([float(t), incoming[j]])
            queues[j] += incoming[j]
            budget = min(queues[j], capacities[j])
            served_total += budget
            queues[j] -= budget
            while budget > 1e-8 and cohorts[j]:
                start, count = cohorts[j][0]
                take = min(count, budget)
                waits.append(max(0, t + 1 - start))
                weights.append(take)
                budget -= take
                count -= take
                if count < 1e-8:
                    cohorts[j].pop(0)
                else:
                    cohorts[j][0][1] = count
        area += sum(queues)
        peak_q = max(peak_q, sum(queues))
        if t < 60:
            series.append(
                {
                    "minute": t + 1,
                    "queue_a": round(queues[0], 2),
                    "queue_b": round(queues[1], 2),
                    "wait_a": round(queues[0] / capacities[0], 2) if capacities[0] else None,
                    "wait_b": round(queues[1] / 6, 2),
                    "arrivals": round(sum(incoming), 2),
                    "served": round(sum(capacities), 2),
                }
            )
        if t >= 59 and sum(queues) < 1e-7:
            break
    overflow = sum(queues)
    order = np.argsort(waits)
    sw = np.array(waits)[order]
    ww = np.array(weights)[order]
    p95 = float(sw[np.searchsorted(np.cumsum(ww), sum(weights) * 0.95)]) if weights else None
    total = initial + added
    walking = sum(demands) * redirect * 4
    avg = float(np.average(waits, weights=weights)) if weights else None
    return {
        "source_type": "SIMULATED",
        "notice": LABEL,
        "lanes": lanes,
        "redirect": redirect,
        "staff": staff,
        "series": series,
        "average_wait": round(avg, 2) if avg is not None else None,
        "p95_wait": p95,
        "peak_queue": round(peak_q),
        "affected_passengers": round(total),
        "passenger_minutes": round(area + walking, 2),
        "walking_penalty": round(walking / total, 2),
        "additional_staff": max(0, lanes - s.lanes) * 2 + staff,
        "cost_proxy": max(0, lanes - s.lanes) * 120 + staff * 60 + redirect * 100,
        "missed_flight_risk": round(
            sum(w for v, w in zip(waits, weights, strict=True) if v > 35) / total, 4
        ),
        "risk_definition": "ASSUMPTION: share of cohort waits exceeding a 35-minute checkpoint budget; not a flight-specific probability",
        "confidence": 0.35 if s.stale else 0.8,
        "confidence_type": "ASSUMPTION — heuristic, uncalibrated",
        "throughput": round(served_total, 2),
        "unserved": round(overflow, 2),
        "conservation_error": round(total - served_total - overflow, 8),
        "resource_utilization": round(served_total / (sum(capacities) * (t + 1)), 3),
        "feasible": overflow < 1e-6,
    }


DEFAULT_WEIGHTS = {
    "wait": 1.0,
    "minutes": 0.01,
    "risk": 50.0,
    "staff": 1.0,
    "walking": 1.0,
    "cost": 0.001,
}


def compare(s, weights=None):
    weights = weights or DEFAULT_WEIGHTS
    base = simulate(s)
    opts = [
        ("No Action", s.lanes, s.redirect),
        ("Open A5", 5, 0.0),
        ("Redirect 20%", s.lanes, 0.20),
        ("Open A5 + redirect 12%", 5, 0.12),
    ]
    results = []
    for name, lanes, redirect in opts:
        r = simulate(s, lanes, redirect, enforce_staff=False)
        if r["additional_staff"] > 4:
            r.update(feasible=False, infeasibility_reason="Requires more than four reserve staff")
        gain = base["passenger_minutes"] - r["passenger_minutes"]
        r.update(name=name, passenger_minutes_saved=round(gain, 2))
        r["score"] = round(
            weights["wait"] * ((base["average_wait"] or 0) - (r["average_wait"] or 0))
            + weights["minutes"] * gain
            + weights["risk"] * (base["missed_flight_risk"] - r["missed_flight_risk"])
            - weights["staff"] * r["additional_staff"]
            - weights["walking"] * r["walking_penalty"]
            - weights["cost"] * r["cost_proxy"],
            3,
        )
        results.append(r)
    best = max((x for x in results if x["feasible"]), key=lambda x: x["score"], default=results[0])
    return {
        "options": results,
        "recommended": None if s.stale or not best["feasible"] else best["name"],
        "weights": weights,
        "reason": "Blocked: DATA STALE / LOW CONFIDENCE"
        if s.stale
        else "No feasible option within reserve staffing and queue-drain constraints."
        if not best["feasible"]
        else f"{best['name']} has the highest feasible weighted score ({best['score']}); includes both security queues, reserve staffing, and extra walking.",
        "source_type": "SIMULATED",
        "notice": LABEL,
    }


def forecast(s):
    sim = simulate(s)
    out = []
    for checkpoint, queue, lanes in [("security-a", 96, s.lanes), ("security-b", 12, 3)]:
        key = "a" if checkpoint.endswith("a") else "b"
        points = []
        for h in [15, 30, 60]:
            row = sim["series"][h - 1]
            val = row[f"wait_{key}"]
            spread = (0.35 if s.stale else 0.15) * (val or 0) + 2
            points.append(
                {
                    "horizon": h,
                    "predicted_wait_min": val,
                    "lower_bound": round(max(0, (val or 0) - spread), 1),
                    "upper_bound": round((val or 0) + spread, 1) if val is not None else None,
                    "queue_length": row[f"queue_{key}"],
                    "passengers_per_5min": round(
                        (
                            arrivals(s.peak)[h - 1] * (1 - s.redirect)
                            if key == "a"
                            else 3 + arrivals(s.peak)[h - 1] * s.redirect
                        )
                        * 5
                    ),
                    "risk_level": risk(val) if val is not None else "RED",
                    "confidence": 0.35 if s.stale else 0.8,
                }
            )
        out.append(
            {
                "id": checkpoint,
                "name": "Security " + key.upper(),
                "current_wait": queue / (lanes * 2) if lanes else None,
                "queue": queue,
                "open_lanes": lanes,
                "maximum_lanes": 5 if key == "a" else 3,
                "forecast": points,
                "source_type": "SIMULATED",
            }
        )
    return out


def journey(s, accessible=True, current="Food C", weight="travel_time", deadline_minutes=64):
    g = graph(accessible)
    waits = {"Security A": 12.0, "Security B": 2.0, "Immigration": 6.0}
    # Use arrival-time forecast when peak is active; choose the fastest eligible security route.
    if s.peak or s.lanes != 4 or s.redirect:
        sim = simulate(s)
        waits.update(
            {"Security A": sim["series"][1]["wait_a"], "Security B": sim["series"][4]["wait_b"]}
        )
    for a, b, d in list(g.edges(data=True)):
        if b in waits and waits[b] is None:
            g.remove_edge(a, b)
            continue
        d["travel_time"] = d["walking_time_min"] + waits.get(b, 0)
        d["congestion"] = d["travel_time"] + d["walking_time_min"] / d["capacity"]
    key = {
        "distance": "walking_distance_m",
        "travel_time": "travel_time",
        "congestion": "congestion",
    }[weight]
    path = nx.shortest_path(g, current, s.gate, weight=key)
    walk = sum(g[a][b]["walking_time_min"] for a, b in zip(path, path[1:], strict=False))
    processing = sum(waits.get(n, 0) for n in path[1:])
    remaining = walk + processing
    safe = round(deadline_minutes - remaining - 10, 1)
    status = (
        "SAFE"
        if safe >= 25
        else "CAUTION"
        if safe >= 15
        else "LEAVE NOW"
        if safe >= 0
        else "HIGH RISK"
    )
    return {
        "anonymous_passenger_id": "demo-passenger",
        "flight_id": "flight-1",
        "flight_number": "TT401",
        "gate": s.gate,
        "current_node": current,
        "boarding_deadline": "18:04",
        "scenario_time": "17:00",
        "path": path,
        "walking_time_min": walk,
        "processing_time_min": round(processing, 1),
        "remaining_journey_min": round(remaining, 1),
        "safety_buffer_min": 10,
        "safe_time_min": safe,
        "risk_level": status,
        "accessible_route": accessible,
        "action": "Proceed now."
        if safe < 15
        else "Follow your recommended route; check for updates before stopping.",
        "source_type": "SIMULATED",
        "notice": LABEL,
        "confidence": 0.35 if s.stale else 0.8,
        "data_stale": s.stale,
    }


def root_causes(s: Scenario):
    """Two-factor Shapley attribution inside this model, never causal proof about an airport."""

    def value(peak, lanes):
        trial = Scenario(peak=peak, lanes=lanes, redirect=s.redirect)
        return simulate(trial)["series"][29]["wait_a"]

    baseline = value(False, 5)
    demand_only = value(s.peak, 5)
    lanes_only = value(False, s.lanes)
    combined = value(s.peak, s.lanes)
    if combined is None or lanes_only is None:
        return {
            "available": False,
            "drivers": [],
            "reason": "Closed checkpoint: finite wait attribution is unavailable",
            "source_type": "DERIVED",
            "notice": LABEL,
        }
    demand = ((demand_only - baseline) + (combined - lanes_only)) / 2
    lanes = ((lanes_only - baseline) + (combined - demand_only)) / 2
    total = combined - baseline
    drivers = sorted(
        [
            {"name": "Departure-wave demand", "wait_contribution_min": round(demand, 3)},
            {"name": "Reduced lane availability", "wait_contribution_min": round(lanes, 3)},
        ],
        key=lambda item: item["wait_contribution_min"],
        reverse=True,
    )
    for index, driver in enumerate(drivers):
        driver.update(
            rank="PRIMARY" if index == 0 else "SECONDARY",
            contribution_percent=round(driver["wait_contribution_min"] / total * 100, 1)
            if total > 1e-8
            else None,
            relationship="OPERATIONAL_CAUSAL_ASSUMPTION",
        )
    return {
        "available": True,
        "drivers": drivers,
        "baseline_wait_min": baseline,
        "combined_wait_min": combined,
        "attributed_change_min": round(total, 3),
        "method": "Two-factor Shapley decomposition of +30 simulated wait versus normal demand and five lanes; redirect held fixed",
        "reason": "Model counterfactual attribution, not empirical causal evidence; weather is contextual only",
        "source_type": "DERIVED",
        "notice": LABEL,
    }
