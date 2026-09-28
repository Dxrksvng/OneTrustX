"""Normalized public observations. Source lineage is a foreign key, never inferred geography."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from .db import Base


class PublicDataset(Base):
    __tablename__ = "public_datasets"
    id = Column(String(100), primary_key=True)
    source_name = Column(String(50), nullable=False)
    source_url = Column(String(1000), nullable=False)
    retrieved_at = Column(DateTime(timezone=True), nullable=False)
    source_geography = Column(String(100), nullable=False)
    source_period = Column(String(100))
    source_type = Column(String(30), nullable=False)
    checksum = Column(String(64), nullable=False)
    records = Column(Integer, nullable=False)
    missing_percent = Column(Float)
    duplicate_percent = Column(Float)
    date_from = Column(String(40))
    date_to = Column(String(40))
    granularity = Column(String(40))
    license_or_terms = Column(String(500))


class PublicObservation(Base):
    __tablename__ = "public_observations"
    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(100), ForeignKey("public_datasets.id"), index=True, nullable=False)
    airport = Column(String(100), index=True)
    date = Column(String(30), index=True)
    metric = Column(String(80), index=True)
    category = Column(String(80))
    value = Column(Float)
    unit = Column(String(30))
    source_type = Column(String(30), nullable=False)
    source_row = Column(Integer)


class PublicFlight(Base):
    __tablename__ = "public_flights"
    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(100), ForeignKey("public_datasets.id"), nullable=False)
    flight_date = Column(String(10), index=True)
    airline = Column(String(10))
    flight_number = Column(String(10))
    origin = Column(String(10), index=True)
    destination = Column(String(10))
    scheduled_departure = Column(String(10))
    departure_delay = Column(Float)
    arrival_delay = Column(Float)
    taxi_out = Column(Float)
    taxi_in = Column(Float)
    cancelled = Column(Float)
    diverted = Column(Float)
    distance = Column(Float)
    carrier_delay = Column(Float)
    weather_delay = Column(Float)
    nas_delay = Column(Float)
    security_delay = Column(Float)
    late_aircraft_delay = Column(Float)
    source_type = Column(String(30), nullable=False)
    source_row = Column(Integer)


class PublicQueue(Base):
    __tablename__ = "public_queues"
    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(100), ForeignKey("public_datasets.id"), nullable=False)
    airport = Column(String(10), index=True)
    terminal = Column(String(100))
    date = Column(String(10), index=True)
    hour = Column(String(20))
    average_wait = Column(Float)
    max_wait = Column(Float)
    us_average_wait = Column(Float)
    us_max_wait = Column(Float)
    non_us_average_wait = Column(Float)
    non_us_max_wait = Column(Float)
    passengers = Column(Integer)
    flights = Column(Integer)
    booths = Column(Integer)
    excluded = Column(Integer)
    bucket_0_15 = Column(Integer)
    bucket_16_30 = Column(Integer)
    bucket_31_45 = Column(Integer)
    bucket_46_60 = Column(Integer)
    bucket_61_90 = Column(Integer)
    bucket_91_120 = Column(Integer)
    bucket_121_plus = Column(Integer)
    source_type = Column(String(30), nullable=False)
    source_row = Column(Integer)
