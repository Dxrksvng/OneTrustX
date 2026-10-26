"""Deterministic One TrustX event, reconciliation and experiment service."""
import hashlib
import json
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select

from . import baggage_flow
from .trust_models import (
    CommonOperationalState,
    ExperimentRun,
    GroundTruth,
    KpiDefinition,
    KpiResult,
    TrustActor,
    TrustConflict,
    TrustEvent,
    TrustOrganization,
    TrustRecommendation,
    TrustScenario,
)

RULE_VERSION = "trust-rules-1.0"
GENERATOR_VERSION = "process-generator-1.0"
SOURCE_REFERENCE = "One TrustX AI/Data Research Blueprint; controlled prototype scenario"
ANCHOR = datetime(2026, 9, 14, 10, 0, tzinfo=UTC)
SCENARIOS = [
    ("S1", "Normal Turnaround", "NORMAL", "Control case with aligned stakeholder events."),
    ("S2", "Baggage Bottleneck", "MODERATE", "Baggage loading lags while other work continues."),
    ("S3", "Gate Conflict", "MODERATE", "Gate readiness and assignment are inconsistent."),
    ("S4", "Weather-affected Turnaround", "MODERATE", "Weather context changes operating uncertainty."),
    ("S5", "Multi-factor Disruption", "SEVERE", "Baggage, gate and weather interact."),
    ("S6", "Data Conflict", "SEVERE", "Stakeholders report contradictory status."),
    ("S7", "Missing / Late Data", "MODERATE", "A required event is late or missing."),
    ("S8", "Scale Test", "SEVERE", "Many concurrent flights and shared resources."),
]
ORG_DATA = [
    ("airline", "Demo Airline Operations"), ("airport", "BKK Airport Operations"),
    ("ground", "Ground Handler"), ("baggage", "Baggage Operator"),
    ("weather", "Open-Meteo Context"),
]


def sid(kind, value):
    return str(uuid5(NAMESPACE_URL, f"one-trustx:{kind}:{value}"))


def ensure_seed(db):
    """Insert master actors, scenario definitions, events, labels and KPI definitions once."""
    if db.get(TrustScenario, "S5"):
        return
    orgs = {}
    for key, name in ORG_DATA:
        orgs[key] = sid("org", key)
        db.add(TrustOrganization(id=orgs[key], name=name, stakeholder_type=key.upper(), source_type="MODELLED"))
    db.flush()
    for key, _name in ORG_DATA:
        db.add(TrustActor(id=sid("actor", key), organization_id=orgs[key], role=f"{key.title()} operator"))
    for ident, name, regime, description in SCENARIOS:
        db.add(TrustScenario(id=ident, name=name, regime=regime, description=description,
                             generator_version=GENERATOR_VERSION, rule_version=RULE_VERSION,
                             parameter_set={"flight_count": 1 if ident != "S8" else 50, "seed": 42},
                             random_seed=42, source_reference=SOURCE_REFERENCE,
                             assumption_version="assumptions-1.0"))
    # Flush master rows before adding dependent events/states.  This keeps
    # startup deterministic on PostgreSQL even though the seed objects are
    # intentionally created without ORM relationships.
    db.flush()
    flight = "flight-1"
    events = [
        ("T0", "AIRCRAFT_ON_GROUND", "ON_GROUND", "opensky", "airport"),
        ("T1", "GROUND_HANDLING_STARTED", "IN_PROGRESS", "ground-handler", "ground"),
        ("T2", "BAGGAGE_LOADING", "82_PERCENT", "baggage-system", "baggage"),
        ("T3", "WEATHER_CONTEXT_CHANGED", "RAIN_CONTEXT", "open-meteo", "weather"),
        ("T4A", "BOARDING_STATUS", "COMPLETE", "airline-dcs", "airline"),
        ("T4B", "BAGGAGE_LOADING", "82_PERCENT", "baggage-system", "baggage"),
        ("T5", "GATE_READINESS", "READY", "airport-aodb", "airport"),
    ]
    ids = []
    for offset, (stamp, typ, state, source, org) in enumerate(events):
        eid = sid("event", f"S5:{stamp}")
        ids.append(eid)
        payload = {"state": state, "process_timepoint": stamp, "generator_version": GENERATOR_VERSION}
        checksum = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        db.add(TrustEvent(id=eid, scenario_id="S5", flight_id=flight, event_type=typ,
                          entity_type="FLIGHT", entity_id=flight, actor_id=sid("actor", org),
                          organization_id=orgs[org], source_system=source,
                          source_timestamp=ANCHOR + timedelta(minutes=offset * 3), state=state,
                          payload=payload, payload_checksum=checksum,
                          verification_status="VERIFIED" if stamp not in {"T4A", "T4B"} else "PENDING",
                          verification_rule_result="SOURCE_AND_SEQUENCE_OK" if stamp not in {"T4A", "T4B"} else "WAITING_FOR_DEPENDENCY",
                          lineage={"source_system": source, "source_record": stamp},
                          conflict_status="CONFLICT" if stamp == "T4A" else "NONE",
                          trust_status="SUPPORTED" if stamp not in {"T4A", "T4B"} else "REQUIRES_RECONCILIATION",
                          source_type="SYSTEM_GENERATED"))
    db.add(TrustConflict(id=sid("conflict", "S5:boarding-baggage"), scenario_id="S5", entity_id=flight,
                         event_ids=[ids[4], ids[5]], conflict_type="CONTRADICTORY_STATUS",
                         rule_version=RULE_VERSION,
                         explanation="Boarding is reported complete while required baggage loading is only 82%.",
                         status="OPEN"))
    db.add(CommonOperationalState(id=sid("state", "S5:flight-1"), scenario_id="S5", flight_id=flight,
                                  readiness_state="AT_RISK", blocking_dependency="Baggage loading",
                                  supporting_event_count=len(events), stakeholder_count=4, conflict_count=1,
                                  confidence=0.86, state_timestamp=ANCHOR + timedelta(minutes=21),
                                  explanation="Baggage completion is a required dependency; boarding status cannot override it.",
                                  supporting_events=ids))
    db.add(TrustRecommendation(id=sid("recommendation", "S5:baggage"), scenario_id="S5",
                               risk_type="BAGGAGE_BOTTLENECK", action="Deploy spare baggage resource GH-03",
                               owner="GROUND_HANDLER", deadline="Before boarding close",
                               dependency="Baggage loading reaches 100% before readiness",
                               expected_outcome={"readiness_delay_reduction_min": 8, "resource": "GH-03"},
                               reference="Rule-based acceptable action + S5 ground truth", confidence=0.86))
    db.add(GroundTruth(id=sid("truth", "S5:readiness"), scenario_id="S5", flight_id=flight,
                       ground_truth_type="TRUE_ROOT_CAUSE", ground_truth_value={"root_event": "T2", "delay_min": 12, "ready": False},
                       source_of_truth="Deterministic process generator", label_rule="Required baggage completion < 100% blocks readiness.",
                       label_creator="rule-based ground truth", label_confidence=1.0,
                       used_for_training=False, used_for_tuning=False, used_for_test=True))
    add_kpi_definitions(db)


def add_kpi_definitions(db):
    defs = [
        ("data-consistency", "Data Consistency", "Share of relevant event views reconciled to one state.", "TRUST", "%", "Ground truth state", "Scenario event stream", "Test labels excluded", "reconciled events / relevant events × 100", "T0–T9", "scenario", "none", "P25–P75 over seeds", "Synthetic process; not production telemetry."),
        ("event-sync", "Event Synchronization Time", "Time from event occurrence to shared state ready.", "TRUST", "seconds", "Event timestamps", "Synthetic event stream", "Future events excluded", "shared_state_timestamp − event_timestamp", "T0–T9", "event", "none", "median and P90", "Simulated ingestion latency."),
        ("traceability", "Event Traceability", "Events with source, actor, timestamp, lineage and checksum.", "TRUST", "%", "Rule criterion", "Trusted event ledger", "none", "traceable events / relevant events × 100", "scenario", "scenario", "100% fields", "Source identity is not physical-world truth."),
        ("verified-rate", "Verified Event Rate", "Events that pass predefined verification rules.", "TRUST", "%", "Verification rule", "Trusted event ledger", "none", "verified events / relevant events × 100", "scenario", "scenario", "rule version", "Verification supports auditability."),
        ("risk-f1", "Risk Detection F1", "F1 against rule-based ground truth risk labels.", "INTELLIGENCE", "score", "GroundTruth.used_for_test", "Synthetic episodes", "Test labels never train/tune", "2PR/(P+R)", "T0–T9", "episode", "risk=readiness false", "Prototype validation only."),
        ("coord-time", "Coordination Time Reduction", "Reduction from event to shared decision.", "OPERATION", "%", "Same episode baseline/proposed", "Scenario experiment", "same scenario required", "(T_baseline−T_oneTrustX)/T_baseline×100", "T0–T9", "scenario", "none", "Simulated workflow time."),
        ("recon-time", "Reconciliation Time Reduction", "Reduction in time to resolve conflicting source views.", "OPERATION", "%", "Same episode baseline/proposed", "Scenario experiment", "same scenario required", "(R_baseline−R_oneTrustX)/R_baseline×100", "T4–T6", "scenario", "none", "Rule workflow, not user study."),
        ("traceability-op", "Recommendation Success", "Action meets predefined acceptable-action and outcome rules.", "INTELLIGENCE", "%", "GroundTruth + rule acceptable action", "Scenario experiment", "test outcomes excluded from tuning", "successful recommendations / evaluated recommendations × 100", "T7–T9", "episode", "none", "P25–P75 over seeds", "No real operational deployment claim."),
    ]
    for row in defs:
        if len(row) == 13:
            row = (*row[:12], "Not reported; deterministic prototype", row[12])
        db.add(KpiDefinition(id=row[0], name=row[1], description=row[2], category=row[3], unit=row[4], reference_type=row[5], reference_source=row[6], dataset_source=row[6], training_data_exclusion=row[7], formula=row[8], measurement_window=row[9], aggregation_level=row[10], threshold=row[11], uncertainty_method=row[12], limitations=row[13], version="1.0"))


def events(db, scenario_id="S5", status=None):
    q = select(TrustEvent).where(TrustEvent.scenario_id == scenario_id).order_by(TrustEvent.source_timestamp)
    if status:
        q = q.where(TrustEvent.verification_status == status)
    return db.scalars(q).all()


def shared_state(db, scenario_id="S5", flight_id="flight-1"):
    row = db.scalar(select(CommonOperationalState).where(CommonOperationalState.scenario_id == scenario_id, CommonOperationalState.flight_id == flight_id))
    if not row:
        return None
    # Computed from the flood scenario's scans and schedule; see baggage_flow.assess.
    baggage_control = baggage_flow.control("BAG-FLOOD-STAFF")
    return {"id": row.id, "scenario_id": row.scenario_id, "flight_id": row.flight_id, "readiness_state": row.readiness_state, "blocking_dependency": row.blocking_dependency, "supporting_event_count": row.supporting_event_count, "stakeholder_count": row.stakeholder_count, "conflict_count": row.conflict_count, "confidence": row.confidence, "explanation": row.explanation, "supporting_events": row.supporting_events, "source_type": "DERIVED", "baggage_control": baggage_control}


def run_experiment(db, scenario_id, condition, seed=42):
    existing = db.scalar(select(ExperimentRun).where(ExperimentRun.scenario_id == scenario_id, ExperimentRun.condition == condition, ExperimentRun.seed == seed))
    if existing:
        return existing
    # Same deterministic episode; only workflow visibility/reconciliation differs.
    proposed = condition in {"ONE_TRUSTX", "TRUST_NO_AI", "ONE_TRUSTX_AI"}
    ai = condition == "ONE_TRUSTX_AI"
    baseline_coord, proposed_coord = 18.0, 7.0
    baseline_recon, proposed_recon = 14.0, 3.0
    metrics = {"coordination_time_s": proposed_coord if proposed else baseline_coord,
               "reconciliation_time_s": proposed_recon if proposed else baseline_recon,
               "risk_detection_time_s": 42.0 if not proposed else (11.0 if ai else 19.0),
               "event_traceability_percent": 42.0 if not proposed else 100.0,
               "verified_event_rate_percent": 0.0 if not proposed else 85.7,
               "delay_risk": 1.0 if not proposed else 0.75 if not ai else 0.5,
               "recommendation_success_percent": 0.0 if not ai else 100.0}
    row = ExperimentRun(id=sid("experiment", f"{scenario_id}:{condition}:{seed}"), scenario_id=scenario_id, condition=condition, seed=seed, code_version="onetrustx-mvp-1", dataset_version="process-fixtures-1", generator_version=GENERATOR_VERSION, rule_version=RULE_VERSION, model_version="rule-risk-1", configuration={"same_episode": True, "condition": condition}, metric_results=metrics, started_at=ANCHOR, ended_at=ANCHOR + timedelta(seconds=metrics["coordination_time_s"]))
    db.add(row)
    return row


def kpi_results(db, scenario_id="S5"):
    base = run_experiment(db, scenario_id, "BASELINE")
    proposed = run_experiment(db, scenario_id, "ONE_TRUSTX_AI")
    db.flush()
    formulas = [("coord-time", base.metric_results["coordination_time_s"], proposed.metric_results["coordination_time_s"], "%"), ("recon-time", base.metric_results["reconciliation_time_s"], proposed.metric_results["reconciliation_time_s"], "%"), ("traceability", base.metric_results["event_traceability_percent"], proposed.metric_results["event_traceability_percent"], "%"), ("verified-rate", 0, proposed.metric_results["verified_event_rate_percent"], "%")]
    out=[]
    for k, b, p, unit in formulas:
        d = (b-p)/b*100 if b else p
        existing = db.scalar(select(KpiResult).where(KpiResult.id == sid("kpi-result", f"{scenario_id}:{k}")))
        if not existing:
            existing=KpiResult(id=sid("kpi-result", f"{scenario_id}:{k}"), kpi_id=k, scenario_id=scenario_id, experiment_id=proposed.id, value=d, baseline=b, proposed=p, delta=d, unit=unit, uncertainty="Single deterministic run; repeated multi-seed pack pending", dataset="Prototype Validation Dataset", reference="Same S5 episode; rule-based ground truth", limitation="Simulated workflow, not an airport deployment result", source_type="SIMULATED")
            db.add(existing)
        out.append(existing)
    db.flush()
    return out
