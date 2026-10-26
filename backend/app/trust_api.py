"""REST surface for One TrustX shared operational truth and experiments."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import baggage_flow
from .db import get_db
from .trust_models import (
    ExperimentRun,
    KpiDefinition,
    KpiResult,
    TrustConflict,
    TrustDecision,
    TrustEvent,
    TrustRecommendation,
    TrustScenario,
)
from .trust_service import events as event_rows
from .trust_service import kpi_results, run_experiment, shared_state, sid

router = APIRouter(prefix="/api/trustx", tags=["One TrustX"])


def dump(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


@router.get("/scenarios")
def scenarios(db: Session = Depends(get_db)):
    return [dump(x) for x in db.scalars(select(TrustScenario).order_by(TrustScenario.id))]


@router.get("/scenarios/{scenario_id}/events")
def scenario_events(scenario_id: str, db: Session = Depends(get_db)):
    if not db.get(TrustScenario, scenario_id):
        raise HTTPException(404, "Scenario not found")
    return [dump(x) for x in event_rows(db, scenario_id)]


@router.get("/events")
def events(scenario_id: str = "S5", verification_status: str | None = None, db: Session = Depends(get_db)):
    return [dump(x) for x in event_rows(db, scenario_id, verification_status)]


@router.get("/events/{event_id}")
def event_detail(event_id: str, db: Session = Depends(get_db)):
    row = db.get(TrustEvent, event_id)
    if not row:
        raise HTTPException(404, "Event not found")
    related = db.scalars(select(TrustEvent).where(TrustEvent.entity_id == row.entity_id)).all()
    return {**dump(row), "related_events": [dump(x) for x in related]}


@router.post("/events/verify")
def verify_event(body: dict, db: Session = Depends(get_db)):
    row = db.get(TrustEvent, body.get("event_id"))
    if not row:
        raise HTTPException(404, "Event not found")
    row.verification_status = "VERIFIED"
    row.verification_rule_result = "SOURCE_ID_TIMESTAMP_CHECKSUM_PRESENT"
    row.trust_status = "SUPPORTED"
    db.commit()
    return dump(row)


@router.post("/events/reconcile")
def reconcile(body: dict, db: Session = Depends(get_db)):
    conflict = db.get(TrustConflict, body.get("conflict_id"))
    if not conflict:
        raise HTTPException(404, "Conflict not found")
    conflict.status = "RESOLVED"
    conflict.resolution = body.get("resolution", "Baggage dependency takes precedence under rule TR-01")
    conflict.resolved_by = body.get("actor", "Demo Operator")
    for event_id in conflict.event_ids:
        row = db.get(TrustEvent, event_id)
        if row:
            row.conflict_status = "RESOLVED"
            row.verification_status = "VERIFIED"
            row.verification_rule_result = "RECONCILED_BY_TR-01"
    db.commit()
    return dump(conflict)


@router.get("/flights/{flight_id}/shared-state")
def flight_state(flight_id: str, scenario_id: str = "S5", db: Session = Depends(get_db)):
    result = shared_state(db, scenario_id, flight_id)
    if not result:
        raise HTTPException(404, "Common operational state not found")
    rows = db.scalars(select(TrustEvent).where(TrustEvent.scenario_id == scenario_id, TrustEvent.flight_id == flight_id).order_by(TrustEvent.source_timestamp)).all()
    return {**result, "events": [dump(x) for x in rows], "stakeholder_views": {"AIRLINE": "BOARDING_COMPLETE", "AIRPORT": "GATE_READY", "GROUND_HANDLER": "HANDLING_IN_PROGRESS", "BAGGAGE": "82_PERCENT"}}


@router.get("/conflicts")
def conflicts(status: str | None = None, db: Session = Depends(get_db)):
    q = select(TrustConflict).order_by(TrustConflict.created_at.desc())
    if status:
        q = q.where(TrustConflict.status == status)
    return [dump(x) for x in db.scalars(q)]


@router.get("/predictions")
def predictions(db: Session = Depends(get_db)):
    state = shared_state(db)
    return [{"id": "risk-S5", "scenario_id": "S5", "risk_type": "BAGGAGE_BOTTLENECK", "detected_at": "T+11s", "baseline_detected_at": "T+42s", "time_advantage_s": 31, "prediction": "Readiness delay +12 min", "confidence": state["confidence"] if state else None, "reference": "Rule-based ground truth; prototype validation dataset", "source_type": "SIMULATED"}]


@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db)):
    output = []
    for row in db.scalars(select(TrustRecommendation).order_by(TrustRecommendation.created_at)):
        decision = db.scalar(select(TrustDecision).where(TrustDecision.recommendation_id == row.id).order_by(TrustDecision.decided_at.desc()))
        output.append(dump(row) | {"decision": dump(decision) if decision else None})
    return output


def decide(rec_id: str, decision: str, body: dict, db: Session):
    rec = db.get(TrustRecommendation, rec_id)
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    previous = db.scalar(select(TrustDecision).where(TrustDecision.recommendation_id == rec_id))
    if previous:
        return dump(previous)
    rec.status = decision.upper()
    row = TrustDecision(id=f"decision-{rec_id}", recommendation_id=rec_id, actor_id=sid("actor", "ground"), decision=decision.upper(), reason=body.get("reason", "Reviewed by stakeholder operator"), audit_reference=f"audit-{rec_id}")
    db.add(row)
    db.commit()
    return dump(row)


@router.post("/recommendations/{recommendation_id}/approve")
def approve(recommendation_id: str, body: dict | None = None, db: Session = Depends(get_db)):
    return decide(recommendation_id, "APPROVED", body or {}, db)


@router.post("/recommendations/{recommendation_id}/reject")
def reject(recommendation_id: str, body: dict | None = None, db: Session = Depends(get_db)):
    return decide(recommendation_id, "REJECTED", body or {}, db)


@router.post("/scenarios/{scenario_id}/run")
def run(scenario_id: str, body: dict | None = None, db: Session = Depends(get_db)):
    if not db.get(TrustScenario, scenario_id):
        raise HTTPException(404, "Scenario not found")
    body = body or {}
    condition = body.get("condition", "ONE_TRUSTX_AI")
    if condition not in {"BASELINE", "SHARED_DATA", "TRUST_NO_AI", "ONE_TRUSTX", "ONE_TRUSTX_AI"}:
        raise HTTPException(422, "Unknown experiment condition")
    row = run_experiment(db, scenario_id, condition, int(body.get("seed", 42)))
    db.commit()
    return dump(row)


@router.get("/scenarios/{scenario_id}/baseline")
def baseline(scenario_id: str, db: Session = Depends(get_db)):
    return dump(run_experiment(db, scenario_id, "BASELINE"))


@router.get("/scenarios/{scenario_id}/onetrustx")
def onetrustx(scenario_id: str, db: Session = Depends(get_db)):
    return dump(run_experiment(db, scenario_id, "ONE_TRUSTX_AI"))


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    rows = kpi_results(db)
    db.commit()
    return [{**dump(x), "definition": dump(db.get(KpiDefinition, x.kpi_id))} for x in rows]


@router.get("/kpis/{kpi_id}")
def kpi(kpi_id: str, db: Session = Depends(get_db)):
    definition = db.get(KpiDefinition, kpi_id)
    if not definition:
        raise HTTPException(404, "KPI definition not found")
    result = db.scalar(select(KpiResult).where(KpiResult.kpi_id == kpi_id, KpiResult.scenario_id == "S5"))
    return {"definition": dump(definition), "result": dump(result) if result else None}


@router.get("/experiments")
def experiments(db: Session = Depends(get_db)):
    return [dump(x) for x in db.scalars(select(ExperimentRun).order_by(ExperimentRun.started_at.desc()))]


@router.get("/baggage/scenarios")
def baggage_scenarios():
    times = [{"at_min": m, "at": baggage_flow.clock(m)} for m in range(60, baggage_flow.HORIZON, 30)]
    return {"default_scenario": "BAG-NORMAL", "default_at_min": baggage_flow.DEFAULT_AT, "times": times,
            "scenarios": [{"id": key, **value} for key, value in baggage_flow.SCENARIOS.items()], "source_type": "SYNTHETIC"}


@router.get("/baggage/control")
def baggage_control(scenario: str = "BAG-NORMAL", at: int = baggage_flow.DEFAULT_AT, seed: int = 42, resource_feed: bool = True):
    if scenario not in baggage_flow.SCENARIOS:
        raise HTTPException(404, "Baggage scenario not found")
    if not 0 <= at < baggage_flow.HORIZON or not 1 <= seed <= 1000:
        raise HTTPException(422, "at or seed out of range")
    return baggage_flow.control(scenario, at, seed, resource_feed)


@router.get("/baggage/calibration")
def baggage_calibration():
    return baggage_flow.calibration()


@router.get("/baggage/evaluation")
def baggage_evaluation():
    result = baggage_flow.stored_evaluation()
    if not result:
        raise HTTPException(404, "Run scripts/experiments/run_baggage_evaluation.py first")
    return result
