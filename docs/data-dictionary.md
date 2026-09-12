# Dataset specification and data dictionary

All entity records contain `id` and `source_type`. Timestamps are UTC, walking/queue durations are minutes, distances/altitude are metres, weather units follow source metadata. Fixture source_type=SYNTHETIC; engine records=SIMULATED. Null actual timestamps/measurements mean not observed, never zero. UUID-formatted strings identify generated analytics/events; stable opaque strings identify fixtures.

JSONB is limited to operational_events.metadata: versioned input/output snapshots and flexible event payloads. Other operational and result metrics have typed columns. Audit links to event snapshots rather than duplicating JSON.

## airport_graph

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| from_node | VARCHAR(200) | True | from node |
| to_node | VARCHAR(200) | True | to node |
| distance_m | FLOAT | True | distance m |
| walking_time_min | FLOAT | True | walking time min |
| accessible | BOOLEAN | True | accessible |
| direction | VARCHAR(200) | True | direction |
| capacity | INTEGER | True | capacity |

## airports

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| iata | VARCHAR(200) | True | iata |
| icao | VARCHAR(200) | True | icao |
| airport_name | VARCHAR(200) | True | airport name |
| city | VARCHAR(200) | True | city |
| country | VARCHAR(200) | True | country |
| latitude | FLOAT | True | latitude |
| longitude | FLOAT | True | longitude |
| timezone | VARCHAR(200) | True | timezone |

## checkpoint

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| checkpoint_type | VARCHAR(200) | True | checkpoint type |
| terminal | VARCHAR(200) | True | terminal |
| zone | VARCHAR(200) | True | zone |
| maximum_lanes | INTEGER | True | maximum lanes |

## demo_state

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | INTEGER | False | Primary key |
| peak | BOOLEAN | False | peak |
| lanes | INTEGER | False | lanes |
| redirect | FLOAT | False | redirect |
| gate | VARCHAR(10) | False | gate |
| updated_at | DATETIME | False | updated at |
| version | INTEGER | False | version |

## flights

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| flight_number | VARCHAR(200) | True | flight number |
| airline | VARCHAR(200) | True | airline |
| origin | VARCHAR(200) | True | origin |
| destination | VARCHAR(200) | True | destination |
| aircraft_type | VARCHAR(200) | True | aircraft type |
| scheduled_departure | DATETIME | True | scheduled departure |
| estimated_departure | DATETIME | True | estimated departure |
| actual_departure | DATETIME | True | actual departure |
| scheduled_arrival | DATETIME | True | scheduled arrival |
| estimated_arrival | DATETIME | True | estimated arrival |
| gate | VARCHAR(200) | True | gate |
| stand | VARCHAR(200) | True | stand |
| status | VARCHAR(200) | True | status |
| delay_reason | VARCHAR(200) | True | delay reason |

## operational_events

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| event_type | VARCHAR(200) | True | event type |
| entity_type | VARCHAR(200) | True | entity type |
| entity_id | VARCHAR(200) | True | entity id |
| actor | VARCHAR(200) | True | actor |
| status | VARCHAR(200) | True | status |
| metadata | JSON | False | Flexible event payload with input/output snapshot and provenance |

## aircraft_positions

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| flight_id | VARCHAR(64) | True | flights.id |
| latitude | FLOAT | True | latitude |
| longitude | FLOAT | True | longitude |
| altitude | FLOAT | True | altitude |
| ground_speed | FLOAT | True | ground speed |
| heading | FLOAT | True | heading |
| vertical_rate | FLOAT | True | vertical rate |

## baggage_events

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| flight_id | VARCHAR(64) | True | flights.id |
| bag_count_expected | INTEGER | True | bag count expected |
| bag_checked | INTEGER | True | bag checked |
| bag_screened | INTEGER | True | bag screened |
| bag_sorted | INTEGER | True | bag sorted |
| bag_loaded | INTEGER | True | bag loaded |
| bag_unloaded | INTEGER | True | bag unloaded |
| bag_on_belt | INTEGER | True | bag on belt |

## gate_events

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| flight_id | VARCHAR(64) | True | flights.id |
| gate_id | VARCHAR(200) | True | gate id |
| state | VARCHAR(200) | True | state |
| queue_estimate | INTEGER | True | queue estimate |
| gate_ready | BOOLEAN | True | gate ready |

## ground_handling

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| flight_id | VARCHAR(64) | True | flights.id |
| activity | VARCHAR(200) | True | activity |
| planned_start | DATETIME | True | planned start |
| planned_end | DATETIME | True | planned end |
| actual_start | DATETIME | True | actual start |
| actual_end | DATETIME | True | actual end |
| status | VARCHAR(200) | True | status |
| actor | VARCHAR(200) | True | actor |

## lane_status

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| checkpoint_id | VARCHAR(64) | True | checkpoint.id |
| lane_id | VARCHAR(200) | True | lane id |
| status | VARCHAR(200) | True | status |
| capacity_pax_min | FLOAT | True | capacity pax min |
| staff_count | INTEGER | True | staff count |

## passenger_flow

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| checkpoint_id | VARCHAR(64) | True | checkpoint.id |
| passenger_arrivals | INTEGER | True | passenger arrivals |
| passenger_departures | INTEGER | True | passenger departures |
| queue_length | INTEGER | True | queue length |
| average_wait_min | FLOAT | True | average wait min |
| p95_wait_min | FLOAT | True | p95 wait min |

## passenger_journey

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| anonymous_passenger_id | VARCHAR(200) | True | anonymous passenger id |
| flight_id | VARCHAR(64) | True | flights.id |
| current_node | VARCHAR(200) | True | current node |
| journey_state | VARCHAR(200) | True | journey state |
| boarding_deadline | DATETIME | True | boarding deadline |
| predicted_gate_arrival | DATETIME | True | predicted gate arrival |
| safe_time_min | FLOAT | True | Deadline minus remaining journey and buffer |
| risk_level | VARCHAR(200) | True | risk level |

## predictions

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| target | VARCHAR(200) | True | target |
| forecast_horizon | INTEGER | True | forecast horizon |
| predicted_value | FLOAT | True | predicted value |
| lower_bound | FLOAT | True | lower bound |
| upper_bound | FLOAT | True | upper bound |
| confidence | FLOAT | True | 0..1 heuristic, not calibrated |
| model_version | VARCHAR(200) | True | model version |
| event_id | VARCHAR(64) | True | operational_events.id |

## weather

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| timestamp | DATETIME | True | UTC record timestamp |
| airport_id | VARCHAR(64) | True | airports.id |
| temperature | FLOAT | True | temperature |
| precipitation | FLOAT | True | precipitation |
| wind_speed | FLOAT | True | wind speed |
| wind_gust | FLOAT | True | wind gust |
| visibility | FLOAT | True | visibility |
| weather_code | INTEGER | True | weather code |
| weather_risk_score | FLOAT | True | weather risk score |

## audit

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | CHAR(32) | False | Primary key |
| timestamp | DATETIME | False | UTC record timestamp |
| prediction_id | VARCHAR(64) | True | predictions.id |
| event_id | VARCHAR(64) | False | operational_events.id |
| human_decision | VARCHAR(30) | True | human decision |
| action_taken | VARCHAR(200) | True | action taken |
| actual_outcome | FLOAT | True | actual outcome |
| prediction_error | FLOAT | True | Observed minus predicted mean wait, signed minutes |
| result | VARCHAR(200) | False | result |

## recommendations

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| prediction_id | VARCHAR(64) | True | predictions.id |
| action | VARCHAR(200) | True | action |
| expected_impact | FLOAT | True | Predicted passenger-minutes saved |
| cost | FLOAT | True | cost |
| constraints | VARCHAR(200) | True | constraints |
| score | FLOAT | True | score |
| accepted | BOOLEAN | True | accepted |
| decision | VARCHAR(200) | True | decision |
| reason | VARCHAR(200) | True | reason |
| actor | VARCHAR(200) | True | actor |
| timestamp | DATETIME | True | UTC record timestamp |

## intervention_results

| Field | SQL type | Nullable | Relationship / meaning |
|---|---|---|---|
| id | VARCHAR(64) | False | Primary key |
| source_type | VARCHAR(20) | False | REAL_PUBLIC / SYNTHETIC / DERIVED / SIMULATED / ASSUMPTION |
| recommendation_id | VARCHAR(64) | True | recommendations.id |
| before | FLOAT | True | Baseline average remaining wait, minutes |
| after_predicted | FLOAT | True | Predicted average remaining wait, minutes |
| after_actual | FLOAT | True | Synthetic observed average remaining wait, minutes |
| passenger_minutes_saved | FLOAT | True | passenger minutes saved |
| prediction_error | FLOAT | True | Observed minus predicted mean wait, signed minutes |
| result | VARCHAR(200) | True | result |
| timestamp | DATETIME | True | UTC record timestamp |
