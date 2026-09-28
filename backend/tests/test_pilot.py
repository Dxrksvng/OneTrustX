from uuid import uuid4

H = {"X-Demo-Role": "AIRPORT_OPERATOR"}


def test_fresh_isolated_sessions(client):
    a = {**H, "X-Demo-Session": str(uuid4())}
    b = {**H, "X-Demo-Session": str(uuid4())}
    o = client.get("/api/overview", headers=a).json()
    assert not o["scenario"]["stale"]
    assert [p["predicted_wait_min"] for p in o["checkpoints"][0]["forecast"]] == [18, 39, 28.88]
    client.post("/api/demo/event", json={"event": "stale"}, headers=a)
    assert client.get("/api/recommendations", headers=a).json()["options"] == []
    assert client.get("/api/overview", headers=a).json()["forecast_status"] == "PAUSED"
    assert not client.get("/api/overview", headers=b).json()["scenario"]["stale"]
    client.post("/api/demo/event", json={"event": "refresh"}, headers=a)
    assert client.get("/api/recommendations", headers=a).json()["recommended"]
    client.post("/api/demo/event", json={"event": "stale"}, headers=a)
    client.post("/api/demo/event", json={"event": "reset"}, headers=a)
    assert not client.get("/api/overview", headers=a).json()["scenario"]["stale"]


def test_idempotent_lifecycle_and_consistent_impact(client):
    first = client.get("/api/recommendations").json()
    for _ in range(3):
        again = client.get("/api/recommendations").json()
        assert first["prediction_id"] == again["prediction_id"]
        assert [o["recommendation_id"] for o in first["options"]] == [
            o["recommendation_id"] for o in again["options"]
        ]
        client.get("/api/overview")
    count = len(client.get("/api/audit").json())
    client.get("/api/overview")
    client.get("/api/recommendations")
    assert len(client.get("/api/audit").json()) == count
    best = next(x for x in first["options"] if x["name"] == first["recommended"])
    assert (
        client.post(
            "/api/recommendations/" + best["recommendation_id"] + "/decision",
            json={"decision": "accept", "reason": "Staff checked"},
            headers=H,
        ).status_code
        == 200
    )
    history = client.get("/api/decision-history").json()
    assert len(history) == 1 and history[0]["operator_action"] == "accept"
    assert client.get("/api/decision-history").json() == history
    impact = client.get("/api/kpi").json()["impact"]
    assert impact["proposed"]["passenger_minutes"] == best["passenger_minutes"]
    assert impact == client.get("/api/overview").json()["impact"]
    result = history[0]["result"]
    assert (
        client.post(
            "/api/results/" + result["id"] + "/measure",
            json={"actual_average_wait": result["after_predicted"] + 1.3},
            headers=H,
        ).status_code
        == 200
    )
    assert len(client.get("/api/decision-history").json()) == 1


def test_flights_and_conserved_journey_cohort(client):
    flights = client.get("/api/flights").json()
    assert [f["destination"] for f in flights] == ["SIN", "CNX", "HKT", "HKG"]
    assert len({f["gate"] for f in flights}) == 4
    o = client.get("/api/overview").json()
    for plan in o["journey_flow"]["plans"]:
        assert plan["security_a"] + plan["security_b"] == plan["total"] == 580
        assert plan["international"] + plan["domestic_bypass"] == sum(plan["gates"].values()) == 580
        assert (
            abs(plan["network_demand"] - plan["initial_queue"] - plan["new_network_arrivals"]) < 1
        )
    before = client.get("/api/passenger/demo-passenger/journey").json()
    client.post("/api/demo/event", json={"event": "gate-change"}, headers=H)
    after = client.get("/api/passenger/demo-passenger/journey").json()
    assert after["safe_time_min"] == before["safe_time_min"] - 23
    assert after["path"] != before["path"]
    assert after["walking_time_min"] == before["walking_time_min"] + 23
    assert client.get("/api/flights").json()[1]["gate"] == "D4"


def test_public_cache_endpoints_use_verified_snapshot_when_db_is_empty(client):
    context = client.get("/api/data/context")
    assert context.status_code == 200
    payload = context.json()
    assert len(payload["bts_daily"]) == 28
    assert [row["passengers"] for row in payload["bkk_daily"]] == [189479, 184178, 165765]
    assert len(payload["thailand_monthly"]) == 19
    assert len(payload["weather_monthly"]) == 12
    assert payload["benchmark"]["records"] == 12178
    catalog = client.get("/api/data/catalog").json()
    assert catalog["datasets"] == []
    assert all(row["source_type"] is None for row in catalog["unavailable"])


def test_rejected_decision_persists_and_cannot_cross_sessions(client):
    a = {**H, "X-Demo-Session": str(uuid4())}
    b = {**H, "X-Demo-Session": str(uuid4())}
    recommendation = client.get("/api/recommendations", headers=a).json()["options"][1]
    url = "/api/recommendations/" + recommendation["recommendation_id"] + "/decision"
    assert (
        client.post(
            url, headers=b, json={"decision": "accept", "reason": "Wrong session"}
        ).status_code
        >= 400
    )
    assert (
        client.post(
            url, headers=a, json={"decision": "reject", "reason": "Staff unavailable"}
        ).status_code
        == 200
    )
    history = client.get("/api/decision-history", headers=a).json()
    assert history[0]["operator_action"] == "reject"
    assert client.get("/api/decision-history", headers=b).json() == []
