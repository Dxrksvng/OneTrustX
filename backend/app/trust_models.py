"""One TrustX shared-event and experiment records.

These tables hold collaboration-level facts only. Stakeholders retain detailed
records in their own systems; this layer stores the event, reference, lineage,
verification and decision metadata needed to coordinate safely.
"""
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


def utcnow():
    return datetime.now(UTC)


Json = JSON().with_variant(JSONB, "postgresql")


class TrustOrganization(Base):
    __tablename__ = "trust_organizations"
    id = Column(String(64), primary_key=True)
    name = Column(String(160), nullable=False)
    stakeholder_type = Column(String(40), nullable=False, index=True)
    source_type = Column(String(30), nullable=False, default="MODELLED")


class TrustActor(Base):
    __tablename__ = "trust_actors"
    id = Column(String(64), primary_key=True)
    organization_id = Column(String(64), ForeignKey("trust_organizations.id"), index=True)
    role = Column(String(80), nullable=False)
    source_type = Column(String(30), nullable=False, default="MODELLED")


class TrustScenario(Base):
    __tablename__ = "trust_scenarios"
    id = Column(String(64), primary_key=True)
    name = Column(String(120), nullable=False)
    regime = Column(String(30), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    generator_version = Column(String(40), nullable=False)
    rule_version = Column(String(40), nullable=False)
    parameter_set = Column(Json, nullable=False)
    random_seed = Column(Integer, nullable=False)
    source_reference = Column(String(500), nullable=False)
    assumption_version = Column(String(40), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class TrustEvent(Base):
    __tablename__ = "trust_events"
    id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    flight_id = Column(String(64), index=True)
    event_type = Column(String(80), index=True, nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), index=True, nullable=False)
    actor_id = Column(String(64), ForeignKey("trust_actors.id"), index=True)
    organization_id = Column(String(64), ForeignKey("trust_organizations.id"), index=True)
    source_system = Column(String(120), nullable=False)
    source_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    ingestion_timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    state = Column(String(80), nullable=False)
    related_event_id = Column(String(64), ForeignKey("trust_events.id"), nullable=True)
    related_resource_id = Column(String(64))
    payload = Column(Json, nullable=False, default=dict)
    payload_checksum = Column(String(64), nullable=False)
    verification_status = Column(String(30), nullable=False, default="PENDING", index=True)
    verification_rule_result = Column(String(300), nullable=False, default="NOT_RUN")
    lineage = Column(Json, nullable=False, default=dict)
    conflict_status = Column(String(30), nullable=False, default="NONE", index=True)
    trust_status = Column(String(30), nullable=False, default="UNVERIFIED")
    source_type = Column(String(30), nullable=False, default="SYSTEM_GENERATED")


class TrustConflict(Base):
    __tablename__ = "trust_conflicts"
    id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    entity_id = Column(String(100), index=True, nullable=False)
    event_ids = Column(Json, nullable=False)
    conflict_type = Column(String(40), nullable=False, index=True)
    rule_version = Column(String(40), nullable=False)
    explanation = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False, default="OPEN", index=True)
    resolution = Column(String(500))
    resolved_by = Column(String(80))
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class CommonOperationalState(Base):
    __tablename__ = "common_operational_states"
    id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    flight_id = Column(String(64), index=True, nullable=False)
    readiness_state = Column(String(40), nullable=False)
    blocking_dependency = Column(String(120))
    supporting_event_count = Column(Integer, nullable=False)
    stakeholder_count = Column(Integer, nullable=False)
    conflict_count = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    state_timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    explanation = Column(String(500), nullable=False)
    supporting_events = Column(Json, nullable=False, default=list)


class TrustRecommendation(Base):
    __tablename__ = "trust_recommendations"
    id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    risk_type = Column(String(80), nullable=False)
    action = Column(String(300), nullable=False)
    owner = Column(String(120), nullable=False)
    deadline = Column(String(80), nullable=False)
    dependency = Column(String(200), nullable=False)
    expected_outcome = Column(Json, nullable=False)
    reference = Column(String(300), nullable=False)
    status = Column(String(30), nullable=False, default="PENDING", index=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class TrustDecision(Base):
    __tablename__ = "trust_decisions"
    id = Column(String(64), primary_key=True)
    recommendation_id = Column(String(64), ForeignKey("trust_recommendations.id"), index=True, nullable=False)
    actor_id = Column(String(64), ForeignKey("trust_actors.id"), nullable=False)
    decision = Column(String(30), nullable=False)
    reason = Column(String(500), nullable=False)
    decided_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    audit_reference = Column(String(100), nullable=False)


class GroundTruth(Base):
    __tablename__ = "trust_ground_truth"
    id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    flight_id = Column(String(64), index=True)
    event_id = Column(String(64), index=True)
    ground_truth_type = Column(String(60), nullable=False)
    ground_truth_value = Column(Json, nullable=False)
    source_of_truth = Column(String(200), nullable=False)
    label_rule = Column(String(500), nullable=False)
    label_created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    label_creator = Column(String(100), nullable=False)
    label_confidence = Column(Float, nullable=False)
    used_for_training = Column(Boolean, nullable=False, default=False)
    used_for_tuning = Column(Boolean, nullable=False, default=False)
    used_for_test = Column(Boolean, nullable=False, default=True)


class ExperimentRun(Base):
    __tablename__ = "trust_experiment_runs"
    id = Column(String(64), primary_key=True, default=lambda: str(uuid4()))
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    condition = Column(String(50), nullable=False, index=True)
    seed = Column(Integer, nullable=False)
    code_version = Column(String(60), nullable=False)
    dataset_version = Column(String(60), nullable=False)
    generator_version = Column(String(40), nullable=False)
    rule_version = Column(String(40), nullable=False)
    model_version = Column(String(60), nullable=False)
    configuration = Column(Json, nullable=False)
    metric_results = Column(Json, nullable=False)
    started_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    ended_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class KpiDefinition(Base):
    __tablename__ = "trust_kpi_definitions"
    id = Column(String(64), primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=False)
    category = Column(String(30), nullable=False, index=True)
    unit = Column(String(30), nullable=False)
    reference_type = Column(String(100), nullable=False)
    reference_source = Column(String(300), nullable=False)
    dataset_source = Column(String(300), nullable=False)
    training_data_exclusion = Column(String(300), nullable=False)
    formula = Column(String(600), nullable=False)
    measurement_window = Column(String(120), nullable=False)
    aggregation_level = Column(String(120), nullable=False)
    threshold = Column(String(120), nullable=False)
    uncertainty_method = Column(String(200), nullable=False)
    limitations = Column(String(600), nullable=False)
    version = Column(String(30), nullable=False)


class KpiResult(Base):
    __tablename__ = "trust_kpi_results"
    id = Column(String(64), primary_key=True)
    kpi_id = Column(String(64), ForeignKey("trust_kpi_definitions.id"), index=True, nullable=False)
    scenario_id = Column(String(64), ForeignKey("trust_scenarios.id"), index=True, nullable=False)
    experiment_id = Column(String(64), ForeignKey("trust_experiment_runs.id"), index=True)
    value = Column(Float)
    baseline = Column(Float)
    proposed = Column(Float)
    delta = Column(Float)
    unit = Column(String(30), nullable=False)
    uncertainty = Column(String(200), nullable=False)
    dataset = Column(String(200), nullable=False)
    reference = Column(String(300), nullable=False)
    limitation = Column(String(600), nullable=False)
    source_type = Column(String(30), nullable=False)
