import pytest

from app.engine import Scenario, compare, forecast, graph, journey, queue_step, simulate


def test_queue_balance_and_capacity():
    assert queue_step(10, 8, 2, 2, 1) == (14, 4)
    assert queue_step(0, 1, 2) == (0, 1)
    assert queue_step(10, 8, 0) == (18, 0)
    with pytest.raises(ValueError):
        queue_step(-1, 0, 2)


def test_demo_forecast():
    assert forecast(Scenario(peak=True))[0]["forecast"][1]["predicted_wait_min"] == 39
    assert forecast(Scenario())[0]["current_wait"] == 12


def test_simulation_conservation_and_reproducibility():
    for lanes in range(6):
        result = simulate(Scenario(peak=True), lanes=lanes, redirect=0.2)
        assert result["conservation_error"] == 0
        assert result["throughput"] >= 0
        assert result["unserved"] >= 0
    assert simulate(Scenario(peak=True)) == simulate(Scenario(peak=True))


def test_recommendation_network_gain():
    result = compare(Scenario(peak=True))
    best = next(x for x in result["options"] if x["name"] == result["recommended"])
    assert best["name"] == "Open A5 + redirect 12%"
    assert best["passenger_minutes_saved"] > 0
    assert best["p95_wait"] < result["options"][0]["p95_wait"]
    assert best["additional_staff"] == 2


def test_resource_constraint():
    with pytest.raises(ValueError):
        simulate(Scenario(lanes=2), lanes=5)
    with pytest.raises(ValueError):
        simulate(Scenario(), redirect=0.5)


def test_safe_time_gate_change():
    before = journey(Scenario())
    after = journey(Scenario(gate="E7"))
    assert before["safe_time_min"] == 34
    assert after["safe_time_min"] == 11
    assert after["risk_level"] == "LEAVE NOW"
    assert after["walking_time_min"] - before["walking_time_min"] == 23
    assert after["remaining_journey_min"] + after["safe_time_min"] + 10 == 64


def test_accessibility():
    assert graph(True)["Retail"]["E7"]["walking_time_min"] == 25
    assert graph(False)["Retail"]["E7"]["walking_time_min"] == 18
    assert (
        journey(Scenario(gate="E7"), False)["walking_time_min"]
        < journey(Scenario(gate="E7"), True)["walking_time_min"]
    )


def test_stale_blocks_recommendation():
    result = compare(Scenario(stale=True))
    assert result["recommended"] is None
    assert result["options"][0]["confidence"] < 0.5


def test_root_cause_model_attribution_conserves_wait_change():
    from app.engine import root_causes

    result = root_causes(Scenario(peak=True))
    assert (
        sum(d["wait_contribution_min"] for d in result["drivers"])
        == result["attributed_change_min"]
    )
    assert sum(d["contribution_percent"] for d in result["drivers"]) == 100
    assert result["drivers"][0]["rank"] == "PRIMARY"
    assert root_causes(Scenario(lanes=0))["available"] is False
