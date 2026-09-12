from datetime import UTC, datetime, timedelta

from .engine import EDGES
from .models import MODELS, DemoState

ANCHOR = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)


def seed(db):
    if db.get(DemoState, 1):
        return

    def add(table, id, **kw):
        row = MODELS[table](id=id, source_type="SYNTHETIC", **kw)
        db.add(row)
        db.flush()
        return row

    add(
        "airports",
        "demo-airport",
        iata="TWT",
        icao="ZZTW",
        airport_name="TimeTwin Illustrative Terminal",
        city="Illustrative",
        country="TH",
        latitude=13.69,
        longitude=100.75,
        timezone="Asia/Bangkok",
    )
    for i in range(1, 5):
        add(
            "flights",
            f"flight-{i}",
            flight_number=f"TT{400 + i}",
            airline="Synthetic Airways",
            origin="TWT",
            destination=f"X{i:02}",
            aircraft_type="ASSUMPTION: narrow-body",
            scheduled_departure=ANCHOR + timedelta(minutes=90 + i * 5),
            estimated_departure=ANCHOR + timedelta(minutes=90 + i * 5),
            gate="C8",
            stand=f"S{i}",
            status="SCHEDULED",
            delay_reason="Synthetic departure wave",
        )
        add(
            "aircraft_positions",
            f"position-{i}",
            timestamp=ANCHOR,
            flight_id=f"flight-{i}",
            latitude=13.6 + i * 0.01,
            longitude=100.7,
            altitude=10000,
            ground_speed=200,
            heading=90,
            vertical_rate=0,
        )
        add(
            "baggage_events",
            f"bags-{i}",
            timestamp=ANCHOR,
            flight_id=f"flight-{i}",
            bag_count_expected=110,
            bag_checked=90,
            bag_screened=85,
            bag_sorted=80,
            bag_loaded=60,
            bag_unloaded=0,
            bag_on_belt=0,
        )
        add(
            "gate_events",
            f"gate-{i}",
            timestamp=ANCHOR,
            flight_id=f"flight-{i}",
            gate_id="C8",
            state="PREPARING",
            queue_estimate=30,
            gate_ready=True,
        )
        for a in [
            "cleaning",
            "catering",
            "refuelling",
            "baggage loading",
            "boarding",
            "door closing",
            "pushback",
        ]:
            add(
                "ground_handling",
                f"handling-{i}-{a}",
                flight_id=f"flight-{i}",
                activity=a,
                planned_start=ANCHOR + timedelta(minutes=20),
                planned_end=ANCHOR + timedelta(minutes=35),
                status="PLANNED",
                actor="synthetic-handler",
            )
    add(
        "weather",
        "weather-1",
        timestamp=ANCHOR,
        airport_id="demo-airport",
        temperature=30,
        precipitation=0,
        wind_speed=8,
        wind_gust=12,
        visibility=10000,
        weather_code=1,
        weather_risk_score=0.1,
    )
    for id, typ, zone, lanes in [
        ("security-a", "SECURITY", "A", 5),
        ("security-b", "SECURITY", "B", 3),
        ("checkin-a", "CHECKIN", "A", 4),
        ("bag-drop", "BAG_DROP", "A", 3),
        ("immigration", "IMMIGRATION", "I", 4),
        ("boarding", "BOARDING", "C8", 2),
    ]:
        add(
            "checkpoint",
            id,
            checkpoint_type=typ,
            terminal="Illustrative T1",
            zone=zone,
            maximum_lanes=lanes,
        )
        for lane in range(1, lanes + 1):
            add(
                "lane_status",
                f"{id}-{lane}",
                timestamp=ANCHOR,
                checkpoint_id=id,
                lane_id=f"{zone}{lane}",
                status="UNAVAILABLE" if id == "security-a" and lane == 5 else "OPEN",
                capacity_pax_min=2,
                staff_count=2,
            )
        for t in range(0, 60, 5):
            add(
                "passenger_flow",
                f"flow-{id}-{t}",
                timestamp=ANCHOR - timedelta(minutes=60 - t),
                checkpoint_id=id,
                passenger_arrivals=40,
                passenger_departures=40,
                queue_length=96 if id == "security-a" else 12,
                average_wait_min=12 if id == "security-a" else 2,
                p95_wait_min=15 if id == "security-a" else 4,
            )
    for i in range(580):
        add(
            "passenger_journey",
            "demo-passenger" if i == 0 else f"anon-{i:04}",
            anonymous_passenger_id="demo-passenger" if i == 0 else f"anon-{i:04}",
            flight_id=f"flight-{i % 4 + 1}",
            current_node="Food C",
            journey_state="PRE_SECURITY",
            boarding_deadline=ANCHOR + timedelta(minutes=64),
            safe_time_min=34,
            risk_level="SAFE",
        )
    for i, (a, b, t, access) in enumerate(EDGES):
        add(
            "airport_graph",
            f"edge-{i}",
            from_node=a,
            to_node=b,
            distance_m=t * 65,
            walking_time_min=t,
            accessible=access,
            direction="FORWARD",
            capacity=120,
        )
    db.add(DemoState(id=1))
    db.commit()
