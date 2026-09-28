H = {"X-Demo-Role": "AIRPORT_OPERATOR"}


def test_demo_loop(client):
    assert client.post("/api/demo/event", json={"event": "reset"}, headers=H).status_code == 200
    assert client.get("/api/passenger/demo-passenger/safe-time").json()["safe_time_min"] == 34
    assert client.post("/api/demo/event", json={"event": "peak"}, headers=H).status_code == 200
    assert (
        client.get("/api/checkpoints/security-a/forecast").json()["forecast"][1][
            "predicted_wait_min"
        ]
        == 39
    )
    comp = client.get("/api/recommendations").json()
    best = next(x for x in comp["options"] if x["name"] == comp["recommended"])
    sim = client.post("/api/simulation", json={"lanes": 5, "redirect": 0.12}, headers=H)
    assert sim.status_code == 200
    assert sim.json()["passenger_minutes_saved"] > 0
    url = f"/api/recommendations/{best['recommendation_id']}/decision"
    assert (
        client.post(
            url, json={"decision": "accept", "reason": "Reserve staff confirmed"}, headers=H
        ).status_code
        == 200
    )
    assert (
        client.post(url, json={"decision": "accept", "reason": "Duplicate"}, headers=H).status_code
        == 409
    )
    assert (
        client.post("/api/demo/event", json={"event": "gate-change"}, headers=H).status_code == 200
    )
    assert client.get("/api/passenger/demo-passenger/journey").json()["gate"] == "E7"
    assert any(x["human_decision"] == "accept" for x in client.get("/api/audit").json())
    result = client.get("/api/results").json()[0]
    measured = client.post(
        f"/api/results/{result['id']}/measure",
        json={"actual_average_wait": result["after_predicted"] + 2},
        headers=H,
    )
    assert measured.status_code == 200
    assert measured.json()["prediction_error"] == 2


def test_validation_rbac_and_stale(client):
    assert client.post("/api/simulation", json={"lanes": 5}).status_code == 403
    assert client.post("/api/simulation", json={"lanes": 99}, headers=H).status_code == 422
    assert (
        client.post("/api/simulation", json={"lanes": 5, "redirect": -0.1}, headers=H).status_code
        == 422
    )
    assert client.get("/api/flights/unknown").status_code == 404
    assert client.get("/api/passenger/unknown/journey").status_code == 404
    assert client.get("/api/passenger/demo-passenger/journey?current=Nowhere").status_code == 422
    comp = client.get("/api/recommendations").json()
    client.post("/api/demo/event", json={"event": "stale"}, headers=H)
    assert client.get("/api/recommendations").json()["recommended"] is None
    assert client.post("/api/simulation", json={"lanes": 5}, headers=H).status_code == 409
    assert (
        client.post(
            f"/api/recommendations/{comp['options'][0]['recommendation_id']}/accept",
            json={"reason": "Reviewed action"},
            headers=H,
        ).status_code
        == 409
    )
    assert (
        "DATA STALE"
        in client.post("/api/copilot/query", json={"question": "What action?"}).json()["answer"]
    )


def test_override_reject_and_version(client):
    comp = client.get("/api/recommendations").json()
    options = comp["options"]
    rid = options[0]["recommendation_id"]
    assert (
        client.post(
            f"/api/recommendations/{rid}/decision",
            json={"decision": "reject", "reason": "Keep observing"},
            headers=H,
        ).status_code
        == 200
    )
    rid = options[1]["recommendation_id"]
    assert (
        client.post(
            f"/api/recommendations/{rid}/decision",
            json={"decision": "override", "reason": "Updated staff constraints"},
            headers=H,
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/api/recommendations/{rid}/decision",
            json={
                "decision": "override",
                "reason": "Updated staff constraints",
                "intervention": {"lanes": 4, "redirect": 0.1},
            },
            headers=H,
        ).status_code
        == 200
    )
    rid = options[2]["recommendation_id"]
    assert (
        client.post(
            f"/api/recommendations/{rid}/decision",
            json={"decision": "accept", "reason": "Outdated option"},
            headers=H,
        ).status_code
        == 409
    )


def test_copilot_fallback_and_api_catalog(client):
    assert (
        client.post("/api/copilot/query", json={"question": "Why the surge?"}).json()["mode"]
        == "NO_LLM_STRUCTURED_FALLBACK"
    )
    for path in [
        "/health",
        "/openapi.json",
        "/api/flights",
        "/api/checkpoints",
        "/api/passenger-flow",
        "/api/airport/map",
        "/api/airport/risk",
        "/api/kpi",
    ]:
        assert client.get(path).status_code == 200


def test_public_context_and_timezone(client):
    result = client.get("/api/public/context")
    assert result.status_code == 200
    assert "operational predictions remain" in result.json()["scope"]
    flight = client.get("/api/flights/flight-1").json()
    assert flight["scheduled_departure"].endswith("Z") or flight["scheduled_departure"].endswith(
        "+00:00"
    )
    passenger = client.get("/api/passenger/anon-0001/journey").json()
    assert passenger["flight_number"] == "DEMO402"


def test_repeated_closures_fail_safely(client):
    for _ in range(4):
        client.post("/api/demo/event", json={"event": "lane-closure"}, headers=H)
        assert client.get("/api/overview").status_code == 200
    comparison = client.get("/api/recommendations").json()
    assert comparison["recommended"] is None
    assert (
        "No feasible"
        in client.post("/api/copilot/query", json={"question": "What action?"}).json()["answer"]
    )


def test_copilot_uses_active_lanes_and_demand(client):
    client.post("/api/demo/event", json={"event": "reset"}, headers=H)
    answer = client.post("/api/copilot/query", json={"question": "Why the queue?"}).json()["answer"]
    assert "peak" in answer and "passengers" in answer
    client.post("/api/demo/event", json={"event": "lane-closure"}, headers=H)
    answer = client.post("/api/copilot/query", json={"question": "Why the queue?"}).json()["answer"]
    assert "3 open lanes provide 6" in answer


def test_flight_operations_and_evaluation(client):
    flight = client.get("/api/flights").json()[0]
    data = client.get(f"/api/flights/{flight['id']}/operations").json()
    assert data["source_type"] == "SYNTHETIC"
    assert len(data["ground_handling"]) == 7
    assert all(x["flight_id"] == flight["id"] for x in data["ground_handling"])
    assert client.get("/api/flights/missing/operations").status_code == 404
    report = client.get("/api/evaluation").json()
    assert len(report["results"]) >= 9
    assert all(x["source_type"] == "SIMULATED" for x in report["results"])
