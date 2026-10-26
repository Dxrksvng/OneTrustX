-- One TrustX initial schema; execute on an empty database. Alembic is preferred.


CREATE TABLE airport_graph (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	from_node VARCHAR(200),
	to_node VARCHAR(200),
	distance_m FLOAT,
	walking_time_min FLOAT,
	accessible BOOLEAN,
	direction VARCHAR(200),
	capacity INTEGER,
	PRIMARY KEY (id)
)

;


CREATE TABLE airports (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	iata VARCHAR(200),
	icao VARCHAR(200),
	airport_name VARCHAR(200),
	city VARCHAR(200),
	country VARCHAR(200),
	latitude FLOAT,
	longitude FLOAT,
	timezone VARCHAR(200),
	PRIMARY KEY (id)
)

;


CREATE TABLE checkpoint (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	checkpoint_type VARCHAR(200),
	terminal VARCHAR(200),
	zone VARCHAR(200),
	maximum_lanes INTEGER,
	PRIMARY KEY (id)
)

;


CREATE TABLE demo_state (
	id SERIAL NOT NULL,
	peak BOOLEAN NOT NULL,
	lanes INTEGER NOT NULL,
	redirect FLOAT NOT NULL,
	gate VARCHAR(10) NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
	version INTEGER NOT NULL,
	PRIMARY KEY (id)
)

;


CREATE TABLE flights (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	flight_number VARCHAR(200),
	airline VARCHAR(200),
	origin VARCHAR(200),
	destination VARCHAR(200),
	aircraft_type VARCHAR(200),
	scheduled_departure TIMESTAMP WITH TIME ZONE,
	estimated_departure TIMESTAMP WITH TIME ZONE,
	actual_departure TIMESTAMP WITH TIME ZONE,
	scheduled_arrival TIMESTAMP WITH TIME ZONE,
	estimated_arrival TIMESTAMP WITH TIME ZONE,
	gate VARCHAR(200),
	stand VARCHAR(200),
	status VARCHAR(200),
	delay_reason VARCHAR(200),
	PRIMARY KEY (id)
)

;

CREATE INDEX ix_flights_status ON flights (status);


CREATE TABLE operational_events (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	event_type VARCHAR(200),
	entity_type VARCHAR(200),
	entity_id VARCHAR(200),
	actor VARCHAR(200),
	status VARCHAR(200),
	metadata JSONB NOT NULL,
	PRIMARY KEY (id)
)

;

CREATE INDEX ix_operational_events_status ON operational_events (status);

CREATE INDEX ix_operational_events_timestamp ON operational_events (timestamp);

CREATE INDEX ix_operational_events_event_type ON operational_events (event_type);


CREATE TABLE aircraft_positions (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	flight_id VARCHAR(64),
	latitude FLOAT,
	longitude FLOAT,
	altitude FLOAT,
	ground_speed FLOAT,
	heading FLOAT,
	vertical_rate FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY(flight_id) REFERENCES flights (id)
)

;

CREATE INDEX ix_aircraft_positions_timestamp ON aircraft_positions (timestamp);

CREATE INDEX ix_aircraft_positions_flight_id ON aircraft_positions (flight_id);


CREATE TABLE baggage_events (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	flight_id VARCHAR(64),
	bag_count_expected INTEGER,
	bag_checked INTEGER,
	bag_screened INTEGER,
	bag_sorted INTEGER,
	bag_loaded INTEGER,
	bag_unloaded INTEGER,
	bag_on_belt INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(flight_id) REFERENCES flights (id)
)

;

CREATE INDEX ix_baggage_events_timestamp ON baggage_events (timestamp);

CREATE INDEX ix_baggage_events_flight_id ON baggage_events (flight_id);


CREATE TABLE gate_events (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	flight_id VARCHAR(64),
	gate_id VARCHAR(200),
	state VARCHAR(200),
	queue_estimate INTEGER,
	gate_ready BOOLEAN,
	PRIMARY KEY (id),
	FOREIGN KEY(flight_id) REFERENCES flights (id)
)

;

CREATE INDEX ix_gate_events_flight_id ON gate_events (flight_id);

CREATE INDEX ix_gate_events_timestamp ON gate_events (timestamp);


CREATE TABLE ground_handling (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	flight_id VARCHAR(64),
	activity VARCHAR(200),
	planned_start TIMESTAMP WITH TIME ZONE,
	planned_end TIMESTAMP WITH TIME ZONE,
	actual_start TIMESTAMP WITH TIME ZONE,
	actual_end TIMESTAMP WITH TIME ZONE,
	status VARCHAR(200),
	actor VARCHAR(200),
	PRIMARY KEY (id),
	FOREIGN KEY(flight_id) REFERENCES flights (id)
)

;

CREATE INDEX ix_ground_handling_status ON ground_handling (status);

CREATE INDEX ix_ground_handling_flight_id ON ground_handling (flight_id);


CREATE TABLE lane_status (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	checkpoint_id VARCHAR(64),
	lane_id VARCHAR(200),
	status VARCHAR(200),
	capacity_pax_min FLOAT,
	staff_count INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(checkpoint_id) REFERENCES checkpoint (id)
)

;

CREATE INDEX ix_lane_status_checkpoint_id ON lane_status (checkpoint_id);

CREATE INDEX ix_lane_status_status ON lane_status (status);

CREATE INDEX ix_lane_status_timestamp ON lane_status (timestamp);


CREATE TABLE passenger_flow (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	checkpoint_id VARCHAR(64),
	passenger_arrivals INTEGER,
	passenger_departures INTEGER,
	queue_length INTEGER,
	average_wait_min FLOAT,
	p95_wait_min FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY(checkpoint_id) REFERENCES checkpoint (id)
)

;

CREATE INDEX ix_passenger_flow_timestamp ON passenger_flow (timestamp);

CREATE INDEX ix_passenger_flow_checkpoint_id ON passenger_flow (checkpoint_id);


CREATE TABLE passenger_journey (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	anonymous_passenger_id VARCHAR(200),
	flight_id VARCHAR(64),
	current_node VARCHAR(200),
	journey_state VARCHAR(200),
	boarding_deadline TIMESTAMP WITH TIME ZONE,
	predicted_gate_arrival TIMESTAMP WITH TIME ZONE,
	safe_time_min FLOAT,
	risk_level VARCHAR(200),
	PRIMARY KEY (id),
	FOREIGN KEY(flight_id) REFERENCES flights (id)
)

;

CREATE INDEX ix_passenger_journey_flight_id ON passenger_journey (flight_id);


CREATE TABLE predictions (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	target VARCHAR(200),
	forecast_horizon INTEGER,
	predicted_value FLOAT,
	lower_bound FLOAT,
	upper_bound FLOAT,
	confidence FLOAT,
	model_version VARCHAR(200),
	event_id VARCHAR(64),
	PRIMARY KEY (id),
	FOREIGN KEY(event_id) REFERENCES operational_events (id)
)

;

CREATE INDEX ix_predictions_timestamp ON predictions (timestamp);


CREATE TABLE weather (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE,
	airport_id VARCHAR(64),
	temperature FLOAT,
	precipitation FLOAT,
	wind_speed FLOAT,
	wind_gust FLOAT,
	visibility FLOAT,
	weather_code INTEGER,
	weather_risk_score FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY(airport_id) REFERENCES airports (id)
)

;

CREATE INDEX ix_weather_timestamp ON weather (timestamp);


CREATE TABLE audit (
	id UUID NOT NULL,
	timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
	prediction_id VARCHAR(64),
	event_id VARCHAR(64) NOT NULL,
	human_decision VARCHAR(30),
	action_taken VARCHAR(200),
	actual_outcome FLOAT,
	prediction_error FLOAT,
	result VARCHAR(200) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(prediction_id) REFERENCES predictions (id),
	FOREIGN KEY(event_id) REFERENCES operational_events (id)
)

;

CREATE INDEX ix_audit_timestamp ON audit (timestamp);


CREATE TABLE recommendations (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	prediction_id VARCHAR(64),
	action VARCHAR(200),
	expected_impact FLOAT,
	cost FLOAT,
	constraints VARCHAR(200),
	score FLOAT,
	accepted BOOLEAN,
	decision VARCHAR(200),
	reason VARCHAR(200),
	actor VARCHAR(200),
	timestamp TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(prediction_id) REFERENCES predictions (id)
)

;

CREATE INDEX ix_recommendations_timestamp ON recommendations (timestamp);


CREATE TABLE intervention_results (
	id VARCHAR(64) NOT NULL,
	source_type VARCHAR(20) NOT NULL,
	recommendation_id VARCHAR(64),
	before FLOAT,
	after_predicted FLOAT,
	after_actual FLOAT,
	passenger_minutes_saved FLOAT,
	prediction_error FLOAT,
	result VARCHAR(200),
	timestamp TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(recommendation_id) REFERENCES recommendations (id)
)

;

CREATE INDEX ix_intervention_results_timestamp ON intervention_results (timestamp);
