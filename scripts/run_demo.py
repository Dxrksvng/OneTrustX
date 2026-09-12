import json

import httpx

base = "http://localhost:8000/api"
h = {"X-Demo-Role": "AIRPORT_OPERATOR"}
with httpx.Client(timeout=30) as c:

    def post(path, body):
        r = c.post(base + path, json=body, headers=h)
        r.raise_for_status()
        return r.json()

    post("/demo/event", {"event": "reset"})
    post("/demo/event", {"event": "peak"})
    result = c.get(base + "/recommendations").json()
    best = next(x for x in result["options"] if x["name"] == result["recommended"])
    post(
        "/recommendations/" + best["recommendation_id"] + "/accept",
        {"reason": "Demo operator verified available staff"},
    )
    post("/demo/event", {"event": "reset"})
    before = c.get(base + "/passenger/demo-passenger/journey").json()
    post("/demo/event", {"event": "gate-change"})
    after = c.get(base + "/passenger/demo-passenger/journey").json()
    print(
        json.dumps(
            {
                "recommendation": best["name"],
                "passenger_minutes_saved": best["passenger_minutes_saved"],
                "safe_time_before": before["safe_time_min"],
                "safe_time_after": after["safe_time_min"],
                "notice": result["notice"],
            },
            indent=2,
        )
    )
