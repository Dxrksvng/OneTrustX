from app import baggage_flow as flow
from app import baggage_metrics as metrics


def test_verification_catches_every_injected_record_fault_and_rejects_no_clean_record():
    run = flow.simulate("BAG-FLOOD-STAFF", 3)
    faulted, truth = metrics.inject_faults(run, 3)
    accepted, flags = metrics.verify(faulted, run)
    for kind in ("DUPLICATE", "LATE", "CORRUPT", "UNKNOWN_FLIGHT"):
        assert truth[kind] and truth[kind] == flags[kind], kind
    assert truth["MISSING"] <= flags["MISSING"] <= truth["LOST"]
    touched = truth["DUPLICATE"] | truth["LATE"] | truth["CORRUPT"] | truth["UNKNOWN_FLIGHT"]
    clean = {
        r["record_id"] for r in run.records if (r["flight"], r["stage"]) not in truth["MISSING"]
    } - touched
    assert clean <= {r["record_id"] for r in accepted}


def test_verification_leaves_a_clean_feed_untouched():
    run = flow.simulate("BAG-NORMAL", 3)
    accepted, flags = metrics.verify([dict(r) for r in run.records], run)
    assert accepted == run.records
    assert not any(flags.values())


def test_reconciliation_never_leaves_more_bags_downstream_than_upstream():
    run = flow.simulate("BAG-FLOOD-STAFF", 5)
    accepted, _ = metrics.verify(metrics.inject_faults(run, 5)[0], run)
    total = {}
    for r in accepted:
        key = (r["flight"], r["stage"], r["bag_class"])
        total[key] = total.get(key, 0) + r["count"]
    for f in run.outbound:
        for bag_class in ("LOCAL", "TRANSFER"):
            assert total.get((f.flight, "sorting", bag_class), 0) >= total.get(
                (f.flight, "loading", bag_class), 0
            )


def test_scorecard_values_are_computed_and_bounded():
    card = metrics.scorecard(range(1, 3))
    trust = card["trust"]["fault_injection"]
    for name in ("raw", "verified"):
        assert abs(sum(trust["status_vs_clean_feed"][name].values()) - 1) < 0.01
    assert card["trust"]["provenance"]["coverage_pct"] == 100
    flood = card["operation"]["BAG-FLOOD-STAFF"]
    assert flood["bags_missed_total_priority"] <= flood["bags_missed_total_plan"]
    assert (
        flood["runs_priority_better"] + flood["runs_priority_same"] + flood["runs_priority_worse"]
        == flood["runs"]
    )
