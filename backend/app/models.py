"""Normalized operational entities. JSONB is restricted to flexible event metadata."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


def now():
    return datetime.now(UTC)


S = String
F = Float
INT = Integer
B = Boolean
T = DateTime(timezone=True)
# name: fields. Foreign keys are marked with @table; natural fixture IDs are opaque strings.
SCHEMA = {
    "airports": "iata:s icao:s airport_name:s city:s country:s latitude:f longitude:f timezone:s",
    "flights": "flight_number:s airline:s origin:s destination:s aircraft_type:s scheduled_departure:t estimated_departure:t actual_departure:t scheduled_arrival:t estimated_arrival:t gate:s stand:s status:s delay_reason:s",
    "aircraft_positions": "timestamp:t flight_id:@flights latitude:f longitude:f altitude:f ground_speed:f heading:f vertical_rate:f",
    "weather": "timestamp:t airport_id:@airports temperature:f precipitation:f wind_speed:f wind_gust:f visibility:f weather_code:i weather_risk_score:f",
    "checkpoint": "checkpoint_type:s terminal:s zone:s maximum_lanes:i",
    "lane_status": "timestamp:t checkpoint_id:@checkpoint lane_id:s status:s capacity_pax_min:f staff_count:i",
    "passenger_flow": "timestamp:t checkpoint_id:@checkpoint passenger_arrivals:i passenger_departures:i queue_length:i average_wait_min:f p95_wait_min:f",
    "passenger_journey": "anonymous_passenger_id:s flight_id:@flights current_node:s journey_state:s boarding_deadline:t predicted_gate_arrival:t safe_time_min:f risk_level:s",
    "baggage_events": "timestamp:t flight_id:@flights bag_count_expected:i bag_checked:i bag_screened:i bag_sorted:i bag_loaded:i bag_unloaded:i bag_on_belt:i",
    "ground_handling": "flight_id:@flights activity:s planned_start:t planned_end:t actual_start:t actual_end:t status:s actor:s",
    "gate_events": "timestamp:t flight_id:@flights gate_id:s state:s queue_estimate:i gate_ready:b",
    "airport_graph": "from_node:s to_node:s distance_m:f walking_time_min:f accessible:b direction:s capacity:i",
    "operational_events": "timestamp:t event_type:s entity_type:s entity_id:s actor:s status:s",
    "predictions": "timestamp:t target:s forecast_horizon:i predicted_value:f lower_bound:f upper_bound:f confidence:f model_version:s event_id:@operational_events",
    "recommendations": "prediction_id:@predictions action:s expected_impact:f cost:f constraints:s score:f accepted:b decision:s reason:s actor:s timestamp:t",
    "intervention_results": "recommendation_id:@recommendations before:f after_predicted:f after_actual:f passenger_minutes_saved:f prediction_error:f result:s timestamp:t",
}
MODELS = {}
for table, spec in SCHEMA.items():
    fields = {
        "__tablename__": table,
        "id": Column(String(64), primary_key=True),
        "source_type": Column(String(20), nullable=False, default="SYNTHETIC"),
    }
    for entry in spec.split():
        name, kind = entry.split(":")
        args = (
            [String(64), ForeignKey(kind[1:] + ".id")]
            if kind.startswith("@")
            else [{"s": S(200), "f": F, "i": INT, "b": B, "t": T}[kind]]
        )
        fields[name] = Column(
            *args,
            nullable=True,
            index=name in {"timestamp", "flight_id", "checkpoint_id", "event_type", "status"},
        )
    if table == "operational_events":
        fields["details"] = Column(
            "metadata", JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
        )
    MODELS[table] = type("".join(x.title() for x in table.split("_")), (Base,), fields)


class DemoState(Base):
    __tablename__ = "demo_state"
    id = Column(Integer, primary_key=True)
    peak = Column(Boolean, nullable=False, default=False)
    lanes = Column(Integer, nullable=False, default=4)
    redirect = Column(Float, nullable=False, default=0)
    gate = Column(String(10), nullable=False, default="C8")
    updated_at = Column(T, nullable=False, default=now)
    version = Column(Integer, nullable=False, default=1)


class Audit(Base):
    __tablename__ = "audit"
    id = Column(Uuid, primary_key=True, default=uuid4)
    timestamp = Column(T, nullable=False, default=now, index=True)
    prediction_id = Column(String(64), ForeignKey("predictions.id"), nullable=True)
    event_id = Column(String(64), ForeignKey("operational_events.id"), nullable=False)
    human_decision = Column(String(30), nullable=True)
    action_taken = Column(String(200), nullable=True)
    actual_outcome = Column(Float, nullable=True)
    prediction_error = Column(Float, nullable=True)
    result = Column(String(200), nullable=False)
