"""Verify concurrent human decisions and demo behavior against the running API."""

from concurrent.futures import ThreadPoolExecutor

import httpx

BASE = "http://localhost:8000/api"
HEADERS = {"X-Demo-Role": "AIRPORT_OPERATOR"}
with httpx.Client(timeout=30) as client:

    def event(value):
        r = client.post(BASE + "/demo/event", json={"event": value}, headers=HEADERS)
        r.raise_for_status()

    event("reset")
    event("peak")
    result = client.get(BASE + "/recommendations")
    result.raise_for_status()
    result = result.json()
    best = next(x for x in result["options"] if x["name"] == result["recommended"])
    assert best["passenger_minutes_saved"] > 0
    assert best["p95_wait"] < result["options"][0]["p95_wait"]

    def accept(_):
        with httpx.Client(timeout=30) as c:
            return c.post(
                BASE + "/recommendations/" + best["recommendation_id"] + "/decision",
                json={
                    "decision": "accept",
                    "reason": "Concurrent submission verification",
                },
                headers=HEADERS,
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = sorted(pool.map(accept, range(2)))
    assert codes == [200, 409], codes
    observed = next(
        r
        for r in client.get(BASE + "/results").json()
        if r["recommendation_id"] == best["recommendation_id"]
    )
    measured = client.post(
        BASE + "/results/" + observed["id"] + "/measure",
        json={
            "actual_average_wait": observed["after_predicted"] + 2,
            "source_type": "SIMULATED",
        },
        headers=HEADERS,
    )
    measured.raise_for_status()
    assert abs(measured.json()["prediction_error"] - 2) < 1e-8
    event("reset")
    before = client.get(BASE + "/passenger/demo-passenger/journey").json()
    event("gate-change")
    after = client.get(BASE + "/passenger/demo-passenger/journey").json()
    assert (before["safe_time_min"], after["safe_time_min"]) == (34, 11)
    event("stale")
    assert client.get(BASE + "/recommendations").json()["recommended"] is None
    assert (
        client.post(
            BASE + "/simulation", json={"lanes": 5}, headers=HEADERS
        ).status_code
        == 409
    )
    event("reset")
    print(
        "Live integration passed: network benefit, duplicate-decision serialization (200/409), synthetic outcome measurement, gate replan 34→11, stale blocking, reset."
    )
