import json
import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Literal
from uuid import NAMESPACE_URL, uuid4, uuid5

import networkx as nx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import Base, Session, engine, get_db
from .engine import LABEL, Scenario, compare, forecast, graph, journey, root_causes, simulate
from .models import MODELS, Audit, DemoSession, DemoState, now
from .public_api import router as public_router
from .seed import seed
from .trust_api import router as trust_router
from .trust_service import ensure_seed as ensure_trust_seed

DEMO = os.getenv("DEMO_MODE", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app):
    # Vercel's demo runtime has no migration process. Create the current
    # SQLAlchemy schema in its ephemeral SQLite volume before seeding it.
    Base.metadata.create_all(bind=engine)
    with Session() as db:
        seed(db)
        ensure_trust_seed(db)
        db.commit()
    yield


app = FastAPI(
    title="One TrustX",
    version="0.1.0",
    lifespan=lifespan,
    description="Synthetic airport decision support. Human decisions affect demo state only.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080").split(
        ","
    ),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Demo-Role", "X-Demo-Session"],
)
app.include_router(trust_router)
limits = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    host = request.client.host if request.client else "unknown"
    q = limits[host]
    t = time.monotonic()
    while q and q[0] < t - 60:
        q.popleft()
    if len(q) >= 300:
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
    q.append(t)
    return await call_next(request)


def operator(x_demo_role: str = Header(default="VIEWER")):
    if not DEMO:
        raise HTTPException(
            503, "Production identity provider must be configured; demo auth disabled"
        )
    if x_demo_role not in {"AIRPORT_OPERATOR", "ADMIN"}:
        raise HTTPException(403, "Airport operator role required")
    return x_demo_role


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Intervention(Strict):
    lanes: int = Field(5, ge=0, le=5)
    redirect: float = Field(0.12, ge=0, le=0.3)
    staff: int = Field(0, ge=0, le=4)
    flight_delay: int = Field(0, ge=0, le=30)


class Decision(Strict):
    decision: Literal["accept", "reject", "override"] = "accept"
    reason: str = Field(min_length=3, max_length=400)
    intervention: Intervention | None = None


class DemoEvent(Strict):
    event: Literal["reset", "peak", "lane-closure", "gate-change", "stale", "refresh", "normal"]


class Query(Strict):
    question: str = Field(min_length=3, max_length=500)


class Measurement(Strict):
    actual_average_wait: float | None = Field(None, ge=0, le=600)
    source_type: Literal["SIMULATED"] = "SIMULATED"


class Weights(Strict):
    wait: float = Field(1, ge=0, le=100)
    minutes: float = Field(0.01, ge=0, le=100)
    risk: float = Field(50, ge=0, le=100)
    staff: float = Field(1, ge=0, le=100)
    walking: float = Field(1, ge=0, le=100)
    cost: float = Field(0.001, ge=0, le=100)


def state(db, lock=False):
    key = db.info.get("demo_session", "legacy")
    row = db.get(DemoSession, key)
    if row is None:
        try:
            with db.begin_nested():
                row = DemoSession(id=key, peak=True)
                db.add(row)
                db.flush()
            db.commit()
        except IntegrityError:
            row = db.get(DemoSession, key)
    # Serialize mutations and deterministic inserts within each demo, not across visitors.
    row = db.scalar(select(DemoSession).where(DemoSession.id == key).with_for_update())
    return row, Scenario(row.peak, row.lanes, float(row.redirect), row.gate, row.version, row.stale)


def stable_id(db, *parts):
    return str(
        uuid5(
            NAMESPACE_URL,
            json.dumps([db.info.get("demo_session", "legacy"), *parts], sort_keys=True),
        )
    )


def session_events(db):
    model = MODELS["operational_events"]
    key = db.info.get("demo_session", "legacy")
    return select(model.id).where(model.details["session_id"].as_string() == key)


def event(db, typ, details, actor="system", entity="demo"):
    id = str(uuid4())
    details = {**details, "session_id": db.info.get("demo_session", "legacy")}
    db.add(
        MODELS["operational_events"](
            id=id,
            timestamp=now(),
            event_type=typ,
            entity_type="demo",
            entity_id=entity,
            actor=actor,
            status="RECORDED",
            details=details,
            source_type="SIMULATED",
        )
    )
    db.flush()
    return id


def record_prediction(db, s, result, kind="FORECAST"):
    id = stable_id(db, s.version, kind, result)
    if db.get(MODELS["predictions"], id):
        return id
    ev = event(
        db,
        kind,
        {
            "input_snapshot": vars(s),
            "predicted_outcome": result,
            "confidence_type": "heuristic, uncalibrated",
        },
    )
    p = forecast(s)[0]["forecast"][1]
    db.add(
        MODELS["predictions"](
            id=id,
            timestamp=now(),
            target="security-a",
            forecast_horizon=30,
            predicted_value=p["predicted_wait_min"],
            lower_bound=p["lower_bound"],
            upper_bound=p["upper_bound"],
            confidence=p["confidence"],
            model_version="fluid-v1",
            event_id=ev,
            source_type="SIMULATED",
        )
    )
    db.flush()
    db.add(Audit(prediction_id=id, event_id=ev, result=kind))
    return id


def serial(row):
    result = {}
    for c in row.__table__.columns:
        value = getattr(row, "details" if c.name == "metadata" else c.name)
        if isinstance(value, datetime) and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        result[c.name] = value
    return result


@app.get("/health")
def health(db=Depends(get_db)):
    db.execute(select(DemoState.id).limit(1))
    return {"status": "ok", "demo_mode": DEMO, "data_mode": os.getenv("DATA_MODE", "synthetic")}


@app.get("/api/overview")
def overview(db=Depends(get_db)):
    row, s = state(db)
    checkpoints = forecast(s)
    causes = root_causes(s)
    record_prediction(db, s, {"checkpoints": checkpoints, "root_causes": causes})
    db.commit()
    return {
        "scenario": vars(s),
        "checkpoints": checkpoints,
        "journey": journey(s),
        "notice": LABEL,
        "source_type": "SIMULATED",
        "data_status": "DATA STALE / LOW CONFIDENCE" if s.stale else "SYNTHETIC DEMO FEED",
        "scenario_time": "17:00 ICT",
        "root_causes": causes,
        "cohort_count": 580,
        "feed_health": {
            "prediction_service": "ONLINE",
            "passenger_flow": "STALE" if s.stale else "FRESH",
            "synthetic_flights": "FRESH",
            "weather": "CONTEXT ONLY — see source cache status",
        },
        "last_reliable_update": row.updated_at,
        "forecast_status": "PAUSED" if s.stale else "AVAILABLE",
        "impact": impact_snapshot(db, s),
        "journey_flow": journey_flow(s),
    }


@app.get("/api/flights")
def flights(db=Depends(get_db)):
    _, s = state(db)
    return [
        flight_view(x, s)
        for x in db.scalars(select(MODELS["flights"]).order_by(MODELS["flights"].id))
    ]


@app.get("/api/flights/{id}")
def flight(id: str, db=Depends(get_db)):
    row = db.get(MODELS["flights"], id)
    if not row:
        raise HTTPException(404, "Flight not found")
    _, s = state(db)
    return flight_view(row, s)


@app.get("/api/checkpoints")
def checkpoints(db=Depends(get_db)):
    _, s = state(db)
    return forecast(s)


@app.get("/api/checkpoints/{id}/status")
@app.get("/api/checkpoints/{id}/forecast")
def checkpoint(id: str, db=Depends(get_db)):
    _, s = state(db)
    item = next((x for x in forecast(s) if x["id"] == id), None)
    if not item:
        raise HTTPException(
            404, "Forecast checkpoint not found; MVP supports security-a and security-b"
        )
    record_prediction(db, s, item)
    db.commit()
    return item


@app.get("/api/passenger-flow")
def flow(db=Depends(get_db)):
    return [
        serial(x)
        for x in db.scalars(
            select(MODELS["passenger_flow"]).order_by(MODELS["passenger_flow"].timestamp).limit(100)
        )
    ]


@app.get("/api/airport/map")
def airport_map(accessible: bool = True):
    g = graph(accessible)
    return {
        "nodes": list(g.nodes),
        "edges": [{"from": a, "to": b, **d} for a, b, d in g.edges(data=True)],
        "source_type": "ASSUMPTION",
        "description": "Illustrative layout; not a real airport floor plan",
    }


@app.get("/api/airport/risk")
def airport_risk(db=Depends(get_db)):
    _, s = state(db)
    return {"checkpoints": forecast(s), "source_type": "SIMULATED", "notice": LABEL}


@app.post("/api/simulation")
@app.post("/api/simulation/intervention")
def simulation(body: Intervention, role=Depends(operator), db=Depends(get_db)):
    _, s = state(db)
    if s.stale:
        raise HTTPException(409, "DATA STALE: refresh before simulation")
    try:
        result = simulate(s, body.lanes, body.redirect, body.staff, body.flight_delay)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    result["passenger_minutes_saved"] = round(
        simulate(s)["passenger_minutes"] - result["passenger_minutes"], 2
    )
    record_prediction(db, s, {"intervention": body.model_dump(), "result": result}, "SIMULATION")
    db.commit()
    return result


@app.get("/api/recommendations")
def recommendations(db=Depends(get_db)):
    _, s = state(db)
    return make_recommendations(db, s)


@app.post("/api/recommendations/score")
def score(body: Weights, role=Depends(operator), db=Depends(get_db)):
    _, s = state(db)
    return make_recommendations(db, s, body.model_dump())


def make_recommendations(db, s, weights=None):
    result = compare(s, weights)
    if s.stale:
        result.update(options=[], forecast_status="PAUSED")
        return result
    pid = record_prediction(db, s, result, "RECOMMENDATION")
    for option in result["options"]:
        rid = stable_id(db, pid, option["name"])
        option["recommendation_id"] = rid
        existing = db.get(MODELS["recommendations"], rid)
        option["decision"] = existing.decision if existing else "pending"
        if existing:
            continue
        db.add(
            MODELS["recommendations"](
                id=rid,
                prediction_id=pid,
                action=option["name"],
                expected_impact=option["passenger_minutes_saved"],
                cost=option["cost_proxy"],
                constraints="5 lanes maximum; 4 reserve staff; <=30% eligible redirect",
                score=option["score"],
                accepted=False,
                decision="pending",
                reason=result["reason"],
                timestamp=now(),
                source_type="SIMULATED",
            )
        )
    db.commit()
    result["prediction_id"] = pid
    return result


@app.post("/api/recommendations/{id}/accept")
@app.post("/api/recommendations/{id}/decision")
def decision(id: str, body: Decision, role=Depends(operator), db=Depends(get_db)):
    row, s = state(db, True)
    rec = db.get(MODELS["recommendations"], id)
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    if rec.decision != "pending":
        raise HTTPException(409, "Recommendation already decided")
    pred = db.get(MODELS["predictions"], rec.prediction_id)
    ev = db.get(MODELS["operational_events"], pred.event_id)
    if ev.details.get("session_id") != db.info.get("demo_session", "legacy"):
        raise HTTPException(404, "Recommendation not found in this session")
    if body.decision != "reject" and (
        s.stale or ev.details["input_snapshot"]["version"] != s.version
    ):
        raise HTTPException(409, "Recommendation is stale; run comparison again")
    options = ev.details["predicted_outcome"]["options"]
    selected = next(x for x in options if x["name"] == rec.action)
    if body.decision == "override" and not body.intervention:
        raise HTTPException(422, "Override requires an intervention")
    if body.decision == "override" and (body.intervention.staff or body.intervention.flight_delay):
        raise HTTPException(
            422,
            "Staff augmentation and flight delay are simulation-only; executable demo overrides support lanes and redirect",
        )
    params = (
        body.intervention
        if body.decision == "override"
        else Intervention(lanes=selected["lanes"], redirect=selected["redirect"])
    )
    applied = None
    if body.decision != "reject":
        try:
            after = simulate(s, params.lanes, params.redirect)
        except ValueError as e:
            raise HTTPException(422, str(e)) from e
        if not after["feasible"]:
            raise HTTPException(422, "Action leaves an unserved queue; choose a feasible option")
        before = simulate(s)
        db.add(
            MODELS["intervention_results"](
                id=stable_id(db, id, "result"),
                recommendation_id=id,
                before=before["average_wait"],
                after_predicted=after["average_wait"],
                passenger_minutes_saved=before["passenger_minutes"] - after["passenger_minutes"],
                result="AWAITING_MEASUREMENT",
                timestamp=now(),
                source_type="SIMULATED",
            )
        )
        applied = {"baseline": before, "proposed": after}
        row.lanes = params.lanes
        row.redirect = params.redirect
        row.version += 1
    rec.decision = body.decision
    rec.accepted = body.decision != "reject"
    rec.actor = role
    rec.reason = body.reason
    eid = event(
        db,
        "HUMAN_DECISION",
        {**body.model_dump(), "impact": applied, "recommendation_id": id},
        role,
        id,
    )
    db.add(
        Audit(
            prediction_id=rec.prediction_id,
            event_id=eid,
            human_decision=body.decision,
            action_taken=rec.action,
            result="DEMO_STATE_UPDATED" if rec.accepted else "REJECTED",
        )
    )
    db.commit()
    return {"decision": rec.decision, "source_type": "SIMULATED", "notice": LABEL}


@app.get("/api/passenger/{id}/journey")
@app.get("/api/passenger/{id}/safe-time")
def passenger(
    id: str,
    accessible: bool = True,
    current: str = "Food C",
    weight: Literal["distance", "travel_time", "congestion"] = "travel_time",
    db=Depends(get_db),
):
    record = db.get(MODELS["passenger_journey"], id)
    if not record:
        raise HTTPException(404, "Synthetic passenger not found")
    _, s = state(db)
    try:
        result = journey(s, accessible, current, weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        raise HTTPException(422, "No eligible route from that location") from None
    result["anonymous_passenger_id"] = id
    result["flight_id"] = record.flight_id
    flight_record = db.get(MODELS["flights"], record.flight_id)
    if record.flight_id != "flight-1":
        s.gate = flight_record.gate
        result = journey(
            s,
            accessible,
            current,
            weight,
            international=flight_record.destination not in {"CNX", "HKT"},
        )
        result.update(anonymous_passenger_id=id, flight_id=record.flight_id)
    result["flight_number"] = flight_record.flight_number
    record_prediction(db, s, result, "JOURNEY")
    db.commit()
    return result


@app.post("/api/demo/event")
def demo_event(body: DemoEvent, role=Depends(operator), db=Depends(get_db)):
    if not DEMO:
        raise HTTPException(403, "Demo disabled")
    row, _ = state(db, True)
    if body.event == "reset":
        row.peak = True
        row.lanes = 4
        row.redirect = 0.0
        row.gate = "C8"
    if body.event == "normal":
        row.peak = False
    if body.event == "peak":
        row.peak = True
    if body.event == "lane-closure":
        row.lanes = max(0, row.lanes - 1)
    if body.event == "gate-change":
        row.gate = "E7"
    row.version += 1
    if body.event == "stale":
        row.stale = True
    else:
        row.stale = False
        row.updated_at = now()
    eid = event(db, "DEMO_" + body.event.upper(), {"version": row.version}, role)
    db.add(Audit(event_id=eid, result="DEMO_EVENT"))
    db.commit()
    return {"event": body.event, "version": row.version}


@app.get("/api/audit")
def audit(db=Depends(get_db)):
    return [
        {**serial(x), "event": serial(db.get(MODELS["operational_events"], x.event_id))}
        for x in db.scalars(
            select(Audit)
            .where(Audit.event_id.in_(session_events(db)))
            .order_by(Audit.timestamp.desc())
            .limit(100)
        )
    ]


def result_rows(db):
    return db.scalars(
        select(MODELS["intervention_results"])
        .join(MODELS["recommendations"])
        .join(MODELS["predictions"])
        .where(MODELS["predictions"].event_id.in_(session_events(db)))
        .order_by(MODELS["intervention_results"].timestamp.desc())
    ).all()


@app.get("/api/results")
def results(db=Depends(get_db)):
    return [serial(x) for x in result_rows(db)]


@app.post("/api/results/{id}/measure")
def measure(id: str, body: Measurement, role=Depends(operator), db=Depends(get_db)):
    state(db, True)
    row = db.get(MODELS["intervention_results"], id)
    if not row or id not in {x.id for x in result_rows(db)}:
        raise HTTPException(404, "Result not found")
    if row.after_actual is not None:
        raise HTTPException(409, "Measurement already recorded")
    if body.actual_average_wait is None:
        rec = db.get(MODELS["recommendations"], row.recommendation_id)
        pred = db.get(MODELS["predictions"], rec.prediction_id)
        snapshot = db.get(MODELS["operational_events"], pred.event_id).details
        review = db.scalar(
            select(MODELS["operational_events"]).where(
                MODELS["operational_events"].entity_id == rec.id,
                MODELS["operational_events"].event_type == "HUMAN_DECISION",
            )
        )
        proposed = review.details["impact"]["proposed"]
        replay = simulate(
            Scenario(**snapshot["input_snapshot"]),
            lanes=proposed["lanes"],
            redirect=proposed["redirect"],
            throughput_factor=0.97,
        )
        body.actual_average_wait = replay["average_wait"]
    row.after_actual = body.actual_average_wait
    row.prediction_error = round(body.actual_average_wait - row.after_predicted, 3)
    row.result = "SIMULATED_MEASUREMENT"
    rec = db.get(MODELS["recommendations"], row.recommendation_id)
    eid = event(db, "MEASUREMENT", body.model_dump(), role, id)
    db.add(
        Audit(
            prediction_id=rec.prediction_id,
            event_id=eid,
            actual_outcome=row.after_actual,
            prediction_error=row.prediction_error,
            result=row.result,
        )
    )
    db.commit()
    return serial(row)


@app.get("/api/kpi")
def kpi(db=Depends(get_db)):
    _, s = state(db)
    sim = simulate(s)
    return {**{k: v for k, v in sim.items() if k != "series"}, "impact": impact_snapshot(db, s)}


@app.post("/api/copilot/query")
def copilot(body: Query, db=Depends(get_db)):
    _, s = state(db)
    result = compare(s)
    q = body.question.lower()
    if s.stale:
        answer = "DATA STALE / LOW CONFIDENCE. Refresh the demo feed before choosing an action."
    elif result["recommended"] is None:
        answer = "No feasible action within the current staffing constraints. Restore lane availability or obtain authorized reserve staff."
    elif any(x in q for x in ["why", "cause", "surge", "flight", "ทำไม", "สาเหตุ", "เที่ยวบิน"]):
        numbers = list(
            db.scalars(
                select(MODELS["flights"].flight_number).order_by(MODELS["flights"].flight_number)
            )
        )
        demand = 19.2 if s.peak else 5.0
        active_demand = round(demand * (1 - s.redirect), 2)
        answer = f"The {'peak' if s.peak else 'normal'} modelled peak-period profile sends {active_demand} passengers/minute to Security A after redirection. {s.lanes} open lanes provide {s.lanes * 2} passengers/minute. These are operational causal assumptions, not causal proof. The stored synthetic fixture flights are {', '.join(numbers)}."
    elif any(
        x in q
        for x in [
            "open",
            "lane",
            "save",
            "recommend",
            "action",
            "what",
            "แนะนำ",
            "เปิด",
            "ลด",
            "จำลอง",
        ]
    ):
        best = next(x for x in result["options"] if x["name"] == result["recommended"])
        answer = f"{result['reason']} Estimated passenger minutes saved: {best['passenger_minutes_saved']}; P95 cohort wait: {best['p95_wait']} minutes; additional staff: {best['additional_staff']}."
    else:
        answer = "I can explain the structured security forecast, compare lane and redirect options, and report estimated passenger minutes saved. This query is outside the supported deterministic topics."
    if s.stale:
        answer_th = "ข้อมูลเก่า / ความเชื่อมั่นต่ำ กรุณารีเฟรชข้อมูลเดโมก่อนเลือกการดำเนินการ"
    elif result["recommended"]:
        best = next(x for x in result["options"] if x["name"] == result["recommended"])
        point = forecast(s)[0]["forecast"][1]
        answer_th = f"แบบจำลองคาดการณ์ Security A อีก 30 นาที: {point['lower_bound']}–{point['upper_bound']} นาที จากปริมาณผู้โดยสารตามสถานการณ์และช่องบริการ {s.lanes} ช่อง ข้อเสนอ: {result['recommended']} ประหยัดเวลาโดยประมาณ {best['passenger_minutes_saved']} คน-นาที ใช้เจ้าหน้าที่เพิ่ม {best['additional_staff']} คน ทั้งหมดเป็นผลจำลอง ไม่ใช่ข้อมูลตรวจวัด BKK หรือข้อพิสูจน์เชิงสาเหตุ"
    else:
        answer_th = "ยังไม่มีทางเลือกที่ทำได้ภายใต้ข้อจำกัดเจ้าหน้าที่ปัจจุบัน กรุณาตรวจความพร้อมช่องบริการและบุคลากร"
    record_prediction(db, s, {"question": body.question, "answer": answer}, "COPILOT")
    db.commit()
    return {
        "answer": answer,
        "answer_th": answer_th,
        "mode": "NO_LLM_STRUCTURED_FALLBACK",
        "source_type": "SIMULATED",
        "notice": LABEL,
    }


@app.get("/api/public/context")
def public_context():
    from .public_context import context

    return context()


@app.get("/api/root-causes")
def causes(db=Depends(get_db)):
    _, s = state(db)
    result = root_causes(s)
    record_prediction(db, s, result, "ROOT_CAUSE")
    db.commit()
    return result


@app.get("/api/flights/{id}/operations")
def flight_operations(id: str, db=Depends(get_db)):
    row = db.get(MODELS["flights"], id)
    if not row:
        raise HTTPException(404, "Flight not found")
    _, s = state(db)
    result = {"flight": flight_view(row, s), "source_type": "SYNTHETIC"}
    for table in ("ground_handling", "baggage_events", "gate_events"):
        model = MODELS[table]
        result[table] = [serial(x) for x in db.scalars(select(model).where(model.flight_id == id))]
        if table == "gate_events" and id == "flight-1":
            for item in result[table]:
                item["gate_id"] = s.gate
    return result


@app.get("/api/evaluation")
def evaluation_report():
    import json
    from pathlib import Path

    report = Path(__file__).with_name("evaluation-results.json")
    if not report.exists():
        raise HTTPException(503, "Offline evaluation report unavailable")
    return json.loads(report.read_text())


def flight_view(row, s):
    return {
        **serial(row),
        "gate": s.gate if row.id == "flight-1" else row.gate,
        "processing_area": "Security A / eligible Security B",
        "label": "MODELLED SCENARIO FLIGHT",
        "source_type": "MODELLED",
        "passenger_cohort": 145,
    }


def impact_snapshot(db, s):
    events = db.scalars(
        select(MODELS["operational_events"])
        .where(
            MODELS["operational_events"].id.in_(session_events(db)),
            MODELS["operational_events"].event_type == "HUMAN_DECISION",
        )
        .order_by(MODELS["operational_events"].timestamp.desc())
    ).all()
    # Preserve accepted scenario outcomes after action; never compare an optimized state to itself.
    reset = db.scalar(
        select(MODELS["operational_events"])
        .where(
            MODELS["operational_events"].id.in_(session_events(db)),
            MODELS["operational_events"].event_type == "DEMO_RESET",
        )
        .order_by(MODELS["operational_events"].timestamp.desc())
    )
    for ev in events:
        if reset and ev.timestamp < reset.timestamp:
            break
        if ev.details.get("impact"):
            return {
                **ev.details["impact"],
                "basis": "ACCEPTED SCENARIO",
                "recommendation_id": ev.details["recommendation_id"],
            }
    comparison = compare(s)
    proposed = next(
        (x for x in comparison["options"] if x["name"] == comparison["recommended"]), None
    )
    return {
        "baseline": comparison["options"][0],
        "proposed": proposed,
        "basis": "PROPOSED SCENARIO",
    }


def journey_flow(s):
    sim = simulate(s)
    plans = []
    for horizon in [15, 30, 60]:
        rows = sim["series"][:horizon]
        a = sum(x["arrivals_a"] for x in rows)
        b = sum(x["arrivals_b"] for x in rows)
        allocation_a = round(580 * a / (a + b))
        plans.append(
            {
                "horizon": horizon,
                "total": 580,
                "security_a": allocation_a,
                "security_b": 580 - allocation_a,
                "international": 290,
                "domestic_bypass": 290,
                "gates": {s.gate: 145, "D4": 145, "E3": 145, "F2": 145},
                "network_demand": sim["affected_passengers"],
                "initial_queue": 108,
                "new_network_arrivals": round(sum(x["arrivals"] for x in sim["series"]), 2),
            }
        )
    return {
        "plans": plans,
        "source_type": "SIMULATED",
        "definition": "580 representative synthetic flight passengers; routing shares follow forecast arrivals. A full-cohort route plan, not simultaneous occupancy. All use check-in/bag drop by assumption. 290 domestic passengers bypass immigration. Queue simulation additionally includes background demand and initial queues; its denominator is reported separately.",
    }


@app.get("/api/decision-history")
def decision_history(db=Depends(get_db)):
    predictions = db.scalars(
        select(MODELS["predictions"])
        .where(MODELS["predictions"].event_id.in_(session_events(db)))
        .order_by(MODELS["predictions"].timestamp.desc())
    ).all()
    history = []
    for pred in predictions:
        ev = db.get(MODELS["operational_events"], pred.event_id)
        if ev.event_type != "RECOMMENDATION":
            continue
        recs = db.scalars(
            select(MODELS["recommendations"]).where(
                MODELS["recommendations"].prediction_id == pred.id
            )
        ).all()
        decisions = [r for r in recs if r.decision != "pending"]
        if not decisions:
            continue
        for rec in decisions:
            result = db.scalar(
                select(MODELS["intervention_results"]).where(
                    MODELS["intervention_results"].recommendation_id == rec.id
                )
            )
            review = db.scalar(
                select(MODELS["operational_events"]).where(
                    MODELS["operational_events"].entity_id == rec.id,
                    MODELS["operational_events"].event_type == "HUMAN_DECISION",
                )
            )
            history.append(
                {
                    "prediction_id": pred.id,
                    "recommendation_id": rec.id,
                    "decision_id": review.id,
                    "operator_action": rec.decision,
                    "operator": "Demo Operator",
                    "action": rec.action,
                    "reason": rec.reason,
                    "prediction_created": pred.timestamp,
                    "forecast_wait": pred.predicted_value,
                    "reviewed_at": review.timestamp,
                    "result": serial(result) if result else None,
                    "source_type": "SIMULATED",
                }
            )
    return history


app.include_router(public_router)
