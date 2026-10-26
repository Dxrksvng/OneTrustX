import pytest

from app import baggage_flow as flow


def test_normal_scenario_reports_normal_at_every_check():
    run = flow.simulate("BAG-NORMAL", 42)
    assert flow.ground_truth(run)["bags_missed"] == 0
    for at in range(60, flow.HORIZON, 15):
        view = flow.assess(run, at)
        assert view["overall_status"] == "NORMAL", at
        assert view["next_action"]["approval"] == "NOT_REQUIRED"


def test_flood_is_located_at_loading_before_the_first_bag_is_missed():
    run = flow.simulate("BAG-FLOOD-STAFF", 42)
    truth = flow.ground_truth(run)
    assert truth["bags_missed"] > 0
    view = flow.assess(run, truth["first_missed_min"] - 30)
    assert view["overall_status"] == "AT_RISK"
    assert view["bottleneck"]["stage_id"] == "loading"
    assert view["next_action"]["approval"] == "HUMAN_REQUIRED"
    assert view["next_action"]["priority_order"]


def test_cause_is_unknown_without_a_resource_feed():
    with_feed = flow.control("BAG-FLOOD-STAFF", 210)
    without = flow.control("BAG-FLOOD-STAFF", 210, use_resource_feed=False)
    assert with_feed["bottleneck"]["cause"]["status"] == "REPORTED"
    assert without["bottleneck"]["cause"]["status"] == "UNKNOWN"
    assert without["bottleneck"]["stage_id"] == "loading"  # location needs scans only


def test_sortation_fault_is_located_at_sorting():
    assert flow.control("BAG-BHS-FAULT", 210)["bottleneck"]["stage_id"] == "sorting"


def test_late_inbound_flags_the_short_connection():
    run = flow.simulate("BAG-LATE-INBOUND", 42)
    missed = set(flow.ground_truth(run)["flights_with_missed_bags"])
    flagged = set()
    for at in range(60, flow.HORIZON, 15):
        flagged |= {f["flight"] for f in flow.assess(run, at)["impact"]["flights"] if f["bags_at_risk"]}
    assert missed and missed <= flagged


def test_stale_loading_feed_asks_for_verification_and_hides_counts():
    view = flow.control("BAG-STALE-FEED", 240)
    assert view["overall_status"] == "VERIFY_DATA"
    assert next(s for s in view["stages"] if s["id"] == "loading")["status"] == "STALE"
    assert view["impact"]["bags_at_risk"] is None


def test_assessment_ignores_scans_not_yet_received():
    run = flow.simulate("BAG-FLOOD-STAFF", 42)
    late = flow.Run(run.scenario_id, run.seed, run.policy, run.outbound, run.inbound,
                    [dict(r, ingest_min=r["ingest_min"] + 10_000) for r in run.records])
    view = flow.assess(late, 210)
    assert all(s["last_scan"] is None for s in view["stages"])


def test_simulation_is_deterministic_and_conserves_bags():
    a, b = flow.simulate("BAG-FLOOD-STAFF", 7), flow.simulate("BAG-FLOOD-STAFF", 7)
    assert a.records == b.records
    for f in a.outbound:
        loaded = sum(r["count"] for r in a.records if r["stage"] == "loading" and r["flight"] == f.flight)
        assert loaded + sum(a.missed[f.flight].values()) == f.local_bags + f.transfer_bags


def test_every_parameter_declares_tier_and_source():
    for name, entry in flow.calibration()["parameters"].items():
        assert entry["tier"] in {"REAL_PUBLIC", "BENCHMARK", "DERIVED", "ASSUMPTION"}, name
        assert entry["source"], name
        if entry["tier"] in {"REAL_PUBLIC", "BENCHMARK", "DERIVED"}:
            assert entry["url"].startswith("https://"), name


@pytest.mark.parametrize("scenario", list(flow.SCENARIOS))
def test_baggage_api(client, scenario):
    response = client.get(f"/api/trustx/baggage/control?scenario={scenario}")
    assert response.status_code == 200
    assert response.json()["source_type"] == "SIMULATED"


def test_baggage_api_rejects_unknown_scenario_and_serves_evaluation(client):
    assert client.get("/api/trustx/baggage/control?scenario=NOPE").status_code == 404
    assert client.get("/api/trustx/baggage/control?at=9999").status_code == 422
    assert len(client.get("/api/trustx/baggage/scenarios").json()["scenarios"]) == 5
    evaluation = client.get("/api/trustx/baggage/evaluation").json()
    assert evaluation["scenarios"]["BAG-NORMAL"]["alert_share_of_checks"] == 0
