def test_trustx_seed_exposes_scenarios_and_shared_state(client):
        scenarios = client.get("/api/trustx/scenarios")
        assert scenarios.status_code == 200
        assert {row["id"] for row in scenarios.json()} == {f"S{i}" for i in range(1, 9)}
        state = client.get("/api/trustx/flights/flight-1/shared-state")
        assert state.status_code == 200
        assert state.json()["readiness_state"] == "AT_RISK"
        assert state.json()["blocking_dependency"] == "Baggage loading"


def test_trustx_recommendation_decision_is_idempotent(client):
        rows = client.get("/api/trustx/recommendations").json()
        recommendation_id = rows[0]["id"]
        first = client.post(f"/api/trustx/recommendations/{recommendation_id}/approve", json={"reason": "demo"})
        second = client.post(f"/api/trustx/recommendations/{recommendation_id}/approve", json={"reason": "demo"})
        assert first.status_code == second.status_code == 200
        assert first.json()["decision"] == second.json()["decision"]


def test_trustx_experiment_uses_same_episode_and_kpi_formula(client):
        run = client.post("/api/trustx/scenarios/S5/run", json={"condition": "ONE_TRUSTX_AI", "seed": 42})
        assert run.status_code == 200
        assert run.json()["configuration"]["same_episode"] is True
        kpis = client.get("/api/trustx/kpis").json()
        coordination = next(row for row in kpis if row["kpi_id"] == "coord-time")
        assert coordination["value"] == coordination["delta"]
        assert coordination["source_type"] == "SIMULATED"
